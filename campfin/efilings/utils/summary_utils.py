import logging, sys

from datetime import timedelta,date


from django.utils import timezone
from django.db.models import Sum
from django.conf import settings


from efilings.models import Filing, Committee

sys.path.append(settings.PARSING_BASE_DIR)
from parsing.utils.cycle_utils import cycle_calendar

# We might consider logging this somewhere else. 
logger = logging.getLogger(__name__)
one_day = timedelta(days=1)



## todo: move top two functions to utils somewhere 

def validate_decimal(value):
    
    if not value:
        return 0
        
    else:
        try:
            return float(value)
        except ValueError:
            logger.error("Error converting contribution amount '%s' from decimal to float" % (value)
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

# routines to standardize the variables present in different filings. Sigh. 
def map_f3x_to_cts(this_dict):
    cts_dict = {
        'tot_receipts':this_dict.get('col_a_total_receipts'),
        'tot_ite_contrib':this_dict.get('col_a_individuals_itemized'), #*
        'tot_non_ite_contrib':this_dict.get('col_a_individuals_unitemized'), #*
        'tot_disburse':this_dict.get('col_a_total_disbursements'),
        'ind_exp_mad':this_dict.get('col_a_independent_expenditures'), #
        'coo_exp_par':this_dict.get('col_a_coordinated_expenditures_by_party_committees'), # na for form 3
        'new_loans':this_dict.get('col_a_total_loans'),
        'outstanding_loans':this_dict.get('col_a_debts_by'),
        'electioneering_made':0, # NA
        'cash_on_hand_end':this_dict.get('col_a_cash_on_hand_close_of_period'),
    }
    return cts_dict

def map_f5_to_cts(this_dict):
    cts_dict = {
        'tot_receipts':this_dict.get('total_contribution'),
        # 'tot_ite_contrib': F5 doesn't have this line
        #'tot_non_ite_contrib':this_dict.get('col_a_individuals_unitemized'), #*
        'tot_disburse':this_dict.get('total_independent_expenditure'),
        'ind_exp_mad':this_dict.get('total_independent_expenditure'), #
        'coo_exp_par':0, # na for form 3
        #'new_loans':this_dict.get('col_a_total_loans'),
        #'outstanding_loans':this_dict.get('col_a_debts_by'),
        'electioneering_made':0, # NA
        #'cash_on_hand_end':this_dict.get('col_a_cash_on_hand_close_of_period'),
    }
    return cts_dict


def map_f3_to_cts(this_dict):
    cts_dict = {
        'tot_receipts':this_dict.get('col_a_total_receipts'),
        'tot_ite_contrib':this_dict.get('col_a_individual_contributions_itemized'),
        'tot_non_ite_contrib':this_dict.get('col_a_individual_contributions_unitemized'),
        'tot_disburse':this_dict.get('col_a_total_disbursements'),
        'ind_exp_mad':0, # na for form 3
        'coo_exp_par':0, # na for form 3
        'new_loans':this_dict.get('col_a_total_loans'),
        'outstanding_loans':this_dict.get('col_a_debts_by'),
        'electioneering_made':0, # NA
        'cash_on_hand_end':this_dict.get('col_a_cash_on_hand_close_of_period'),
    }
    return cts_dict

def map_f3p_to_cts(this_dict):
    cts_dict = {
        'tot_receipts':this_dict.get('col_a_total_receipts'),
        'tot_ite_contrib':this_dict.get('col_a_individuals_itemized'), #*
        'tot_non_ite_contrib':this_dict.get('col_a_individuals_unitemized'), #*
        'tot_disburse':this_dict.get('col_a_total_disbursements'),
        'ind_exp_mad':0, # na for form 3
        'coo_exp_par':0, # na for form 3
        'new_loans':this_dict.get('col_a_total_loans'),
        'outstanding_loans':this_dict.get('col_a_debts_by'),
        'electioneering_made':0, # NA
        'cash_on_hand_end':this_dict.get('col_a_cash_on_hand_close_of_period'),
    }
    return cts_dict


def map_summary_form_to_dict(form, header_data, Filing):
    if form in ['F3', 'F3A', 'F3T', 'F3N']:
        cts_dict = map_f3_to_cts(header_data)
    elif form in ['F3P', 'F3PA', 'F3PN', 'F3PT']:
        cts_dict = map_f3p_to_cts(header_data)
    elif form in ['F3X', 'F3XA', 'F3XN', 'F3XT']:
        cts_dict = map_f3x_to_cts(header_data)
    elif form in ['F5', 'F5A', 'F5N']:
        cts_dict = map_f5_to_cts(header_data)
    
    cts_dict['coverage_from_date'] = Filing.coverage_from_date
    cts_dict['coverage_to_date'] = Filing.coverage_to_date
    
    return cts_dict

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

def summarize_noncommittee_periodic_electronic(committee, cycle):
    """ Not implemented. This should probably just use non-quarterly reports, but it's a tossup."""
    this_cycle_calendar = cycle_calendar[int(cycle)]
    this_cycle_start = this_cycle_calendar['start']
    this_cycle_end = this_cycle_calendar['end']

     
def summarize_committee_periodic_electronic(committee, cycle):
    this_cycle_calendar = cycle_calendar[int(cycle)]
    this_cycle_start = this_cycle_calendar['start']
    this_cycle_end = this_cycle_calendar['end']
    
    relevant_filings = Filing.objects.filter(fec_id=committee.fec_id, superseded_by_amendment=False, coverage_from_date__gte=this_cycle_start, coverage_to_date__lte=this_cycle_end, form_type__in=['F3P', 'F3PN', 'F3PA', 'F3PT', 'F3', 'F3A', 'F3N', 'F3T', 'F3X', 'F3XA', 'F3XN', 'F3XT']).order_by('coverage_to_date')
    if not relevant_filings:
        return None
    
    
    # check gaps
    previous_end = None
    previous_start = None
    # We're standardizing info from the filing header into committee-time summaries
    # Put each time summary into the below. 
    cts_array = []
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
        
        
        form = this_filing.form_type
        header_data = this_filing.header_data
        cts_dict = map_summary_form_to_dict(form, header_data, this_filing)
        
        for i in cts_dict:
            if cts_dict[i] == '':
                cts_dict[i] = None
        cts_array.append(cts_dict)
    
    # we have each filing period represented in the cts_array.
    # so sum them. 
    if cts_array:
        most_recent_report = cts_array[-1]
    
   
        committee.cash_on_hand_date = most_recent_report['coverage_to_date']


        committee.cash_on_hand = most_recent_report['cash_on_hand_end']
        committee.outstanding_loans = most_recent_report['outstanding_loans']

    recent_summary = None
    if cts_array and most_recent_report['coverage_to_date']:
        recent_summary = get_recent_reports(committee.fec_id, most_recent_report['coverage_to_date'])        
    else:
        recent_summary = get_recent_reports(committee.fec_id, None)
        
    committee.total_contributions = sum(string_to_float(item['tot_non_ite_contrib']) for item in cts_array) + sum(string_to_float(item['tot_ite_contrib']) for item in cts_array) + validate_decimal(recent_summary['tot_contrib'])
    committee.total_disbursements = sum(string_to_float(item['tot_disburse']) for item in cts_array) + validate_decimal(recent_summary['tot_disburse'])
    committee.total_unitemized = sum(string_to_float(item['tot_non_ite_contrib']) for item in cts_array)
    committee.total_coordinated_expenditures = sum(string_to_float(item['coo_exp_par']) for item in cts_array) + validate_decimal(recent_summary['coo_exp_par'])
    committee.total_receipts = sum(string_to_float(item['tot_receipts']) for item in cts_array) + validate_decimal(recent_summary['tot_receipts'])
    committee.total_indy_expenditures = sum(string_to_float(item['ind_exp_mad']) for item in cts_array) + validate_decimal(recent_summary['total_indy_expenditures'])
    
    committee.committee_sum_update_time = timezone.now()
    
    committee.save()

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
    
    