import logging, sys

from datetime import timedelta,date


from django.utils import timezone
from django.db.models import Sum, Max
from django.conf import settings


from efilings.models import Filing, Committee
from ftpdata.models import CandComLink

sys.path.append(settings.PARSING_BASE_DIR)
from parsing.utils.cycle_utils import cycle_calendar

# We might consider logging this somewhere else. 
logger = logging.getLogger(__name__)

try:
    CURRENT_CYCLE = settings.CURRENT_CYCLE
except:
    print "Missing current cycle list. Defaulting to 2016. "
    CURRENT_CYCLE = '2016'

this_cycle_calendar = cycle_calendar[int(CURRENT_CYCLE)]
this_cycle_start = this_cycle_calendar['start']
this_cycle_end = this_cycle_calendar['end']
one_day = timedelta(days=1)



## todo: move top two functions to utils somewhere 

def validate_decimal(value):
    
    if not value:
        return 0
        
    else:
        try:
            return float(value)
        except ValueError:
            logger.error("Error converting contribution amount '%s' from decimal to float" % (value))
            return 0
            

def string_to_float(the_string):
    # Return zero if it's a blank space
    if not the_string:
        return 0
    s = the_string.rstrip()
    if s:
        return float(s)
    else:
        return 0
                    
def warn_about_gap(gap_start, gap_end, committee):
    logger.warn("Gap in summary data coverage for %s %s -- gap start = %s and gap end = %s" % (committee.name, committee.fec_id, gap_start, gap_end))


def get_recent_reports(fec_id, coverage_from_date):
    if not coverage_from_date:
        coverage_from_date = this_cycle_start

    recent_report_list = Filing.objects.filter(fec_id=fec_id, coverage_from_date__gte=coverage_from_date, form_type__in=['F5A', 'F5', 'F5N', 'F24', 'F24A', 'F24N', 'F6', 'F6A', 'F6N']).exclude(is_f5_quarterly=True).exclude(superseded_by_amendment=True)

    # for these reports only itemized contributions are reported, so tot_raised = tot_contrib = tot_ite_contrib. 
    # also , tot_spent = tot_ies, but that's tracked at the report level. Maybe do something weird for F13s on this score, I dunno. 
    summary_data = recent_report_list.aggregate(tot_contrib=Sum('tot_raised'), tot_disburse=Sum('tot_spent'), tot_ite_contrib=Sum('tot_raised'), tot_receipts=Sum('tot_raised'), coo_exp_par=Sum('tot_coordinated'), total_indy_expenditures=Sum('tot_ies'))

    for i in summary_data:
        if not summary_data[i]:
            summary_data[i] = 0

    return summary_data

def sum_from_filings(relevant_filings, cycle, committee):

    this_cycle_calendar = cycle_calendar[int(cycle)]
    this_cycle_start = this_cycle_calendar['start']
    this_cycle_end = this_cycle_calendar['end']

    # Check for gap between periodic filings, and for duplicate filings covering the same period. 
    # Slightly time consuming, but good at finding issues. 

    previous_end = None
    previous_start = None
    # We're standardizing info from the filing header into committee-time summaries
    # Put each time summary into the below. 
    for i, this_filing in enumerate(relevant_filings):
        if i==0:

            if this_filing.coverage_from_date - this_cycle_start > one_day:
                warn_about_gap(this_cycle_start,this_filing.coverage_from_date, committee)


        if i>0:
            difference = this_filing.coverage_from_date - previous_end
            if difference > one_day:
                warn_about_gap(previous_end,this_filing.coverage_from_date, committee)

            if this_filing.coverage_from_date == previous_start and this_filing.coverage_to_date == previous_end:
                msg = "Duplicate unamended filing found for %s %s : %s-%s" % (committee.name, committee.fec_id, this_filing.coverage_from_date, this_filing.coverage_to_date)
                logger.error(msg)

        previous_start = this_filing.coverage_from_date
        previous_end = this_filing.coverage_to_date


    recent_summary = None     
    if relevant_filings:
        num_filing = len(relevant_filings)
        most_recent_report = relevant_filings[num_filing-1]
        committee.cash_on_hand_date = most_recent_report.coverage_to_date
        committee.cash_on_hand = most_recent_report.coh_end
        committee.outstanding_loans = most_recent_report.outstanding_loans

        if most_recent_report.coverage_to_date:
            recent_summary = get_recent_reports(committee.fec_id, most_recent_report.coverage_to_date)        
        else:
            recent_summary = get_recent_reports(committee.fec_id, None)
    else:
        recent_summary = get_recent_reports(committee.fec_id, None)

    # Actually run sums... 
    summary_data = relevant_filings.aggregate(total_contributions=Sum('tot_contribs'), total_disbursements=Sum('tot_spent'), total_itemized_indiv=Sum('tot_ite_contribs_indivs'), total_unitemized_indiv=Sum('tot_non_ite_contribs_indivs'), tot_receipts=Sum('tot_raised'), coo_exp_par=Sum('tot_coordinated'), total_independent_expenditures=Sum('tot_ies'))

    committee.total_contributions = (summary_data['total_contributions'] or 0) + validate_decimal(recent_summary['tot_contrib'])
    committee.total_disbursements = (summary_data['total_disbursements'] or 0) + validate_decimal(recent_summary['tot_disburse'])
    committee.total_unitemized_indiv = summary_data['total_unitemized_indiv'] or 0
    committee.total_itemized_indiv = summary_data['total_itemized_indiv'] or 0
    committee.total_coordinated_expenditures = summary_data['coo_exp_par'] or 0
    committee.total_receipts = (summary_data['tot_receipts'] or 0 ) + validate_decimal(recent_summary['tot_receipts'])
    committee.total_independent_expenditures = (summary_data['total_independent_expenditures'] or 0 ) + validate_decimal(recent_summary['total_indy_expenditures'])

    committee.committee_sum_update_time = timezone.now()
    committee.is_dirty=False
    committee.save()


def summarize_noncommittee_periodic_electronic(committee, cycle):
    relevant_filings = Filing.objects.filter(fec_id=committee.fec_id, superseded_by_amendment=False, coverage_from_date__gte=this_cycle_start, coverage_to_date__lte=this_cycle_end, form_type__in=['F5','F5A', 'F5N', 'F5']).exclude(is_f5_quarterly=False).order_by('coverage_to_date')
    
    sum_from_filings(relevant_filings, cycle, committee)
     
def summarize_committee_periodic_electronic(committee, cycle):
    
    relevant_filings = Filing.objects.filter(fec_id=committee.fec_id, superseded_by_amendment=False, coverage_from_date__gte=this_cycle_start, coverage_to_date__lte=this_cycle_end, form_type__in=['F3P', 'F3PN', 'F3PA', 'F3PT', 'F3', 'F3A', 'F3N', 'F3T', 'F3X', 'F3XA', 'F3XN', 'F3XT']).order_by('coverage_to_date')
    
    sum_from_filings(relevant_filings, cycle, committee)
    

def update_committee_totals(committee, cycle):

    logger.info("Creating summaries for %s and cycle=%s" % (committee.fec_id, cycle))
    
    if committee.is_paper_filer:
        ## This library doesn't process paper filings. If it did, we could run summaries
        ## on the basis of webk numbers (now known as report-by-report periodic summary, or some such)
        # summarize_committee_periodic_webk(committee.fec_id, force_update=True)
        return None
        
    else:
        # if they file on F5's it's different since, the same form is used for monthly and daily reports
        if committee.ctype == 'I':
            summarize_noncommittee_periodic_electronic(committee, cycle)                    
        else:
            summarize_committee_periodic_electronic(committee, cycle)

def update_candidate_totals(candidate, cycle):
    """
    Update the totals for a candidate based on their authorized and primary campaign committee (PCC) committees.
    Might want to switch to *only* the PCC, but...
    
    This doesn't include leadership PACs, or super PACs; those are probably more important, but they 
    are outside the scope of straight FEC data... 
    
    If the leadership_pac_candidate field is set on committees this would be possible... 
    
    
    """
    
    linked_committees = CandComLink.objects.filter(cand_id=candidate.fec_id, cycle=cycle, cmte_dsgn__in=['A', 'P'])
    related_fec_ids = [c.cmte_id for c in linked_committees]
    related_committees = Committee.objects.filter(cycle=cycle, fec_id__in=related_fec_ids)
    summary_data  = related_committees.aggregate(total_receipts=Sum('total_receipts'),total_disbursements=Sum('total_disbursements'),total_contributions=Sum('total_contributions'),total_unitemized_indiv=Sum('total_unitemized_indiv'),total_itemized_indiv=Sum('total_itemized_indiv'), outstanding_loans=Sum('outstanding_loans'), cash_on_hand=Sum('cash_on_hand'), cash_on_hand_date=Max('cash_on_hand_date'))
    
    # the keys are the same! could assign 
    candidate.total_receipts = summary_data['total_receipts'] or 0
    candidate.total_contributions = summary_data['total_contributions'] or 0
    candidate.total_disbursements = summary_data['total_disbursements'] or 0 
    candidate.total_unitemized_indiv = summary_data['total_unitemized_indiv'] or 0
    candidate.total_itemized_indiv = summary_data['total_itemized_indiv'] or 0
    candidate.outstanding_loans = summary_data['outstanding_loans']
    candidate.cash_on_hand = summary_data['cash_on_hand']
    candidate.cash_on_hand_date = summary_data['cash_on_hand_date']
     
    candidate.candidate_total_update_time = timezone.now()
    candidate.is_dirty=False
    candidate.save()

"""
from efilings.utils.summary_utils import update_candidate_totals
from efilings.models import Candidate
c = Candidate.objects.get(cycle='2016', fec_id='H0CA27085')
update_candidate_totals(c, '2016')

"""
    