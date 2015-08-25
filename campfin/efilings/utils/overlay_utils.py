"""
Create Candidate, Committee models by copying data over from the FTP_data app (which comes directly from FEC).

Probably you'd want to include an update version of this, because candidate and committee data does sometimes change. 

For now, creating the new cand or committee doesn't trigger an update. 

Only returns a candidate or committee if it is newly created -- returns None if it already exists.


"""


import logging, sys

from ftpdata.models import Candidate as FTP_Candidate
from ftpdata.models import Committee as FTP_Committee
from efilings.models import Candidate, Committee

from efilings.utils.term_reference import get_election_year_from_term_class, get_term_class_from_election_year
from efilings.utils.party_reference import get_party_from_pty
from django.template.defaultfilters import slugify
from django.conf import settings
from django.utils import timezone

# put the parsing directory stuff on the path -- needs more sane setup
sys.path.append(settings.PARSING_DIR)
from read_FEC_settings import FILECACHE_DIRECTORY, USER_AGENT, FEC_DOWNLOAD, DELAY_TIME, CYCLE
from utils.blacklist import blacklisted_committees, blacklisted_candidates

# Get an instance of a logger
logger = logging.getLogger(__name__)

def make_candidate_overlay_from_masterfile(candidate_id, cycle, verify_does_not_exist=True):
    
    if candidate_id in blacklisted_candidates:
        return None
        
    ## Returns overlay if created, None if not. 
    

    if verify_does_not_exist:
        try:
            # If there's already a candidate overlay, don't do this. 
            entered_candidate = Candidate.objects.get(cycle=cycle, fec_id=candidate_id)            
            return None
        except Candidate.DoesNotExist:
            pass

    thiscandidate = None
    
    try:
        thiscandidate = FTP_Candidate.objects.get(cycle=cycle, cand_id=candidate_id)
    except FTP_Candidate.DoesNotExist:
        logger.info("Couldn't find candidate in masterfile id=%s election_year=%s cycle=%s" % (candidate_id, election_year, cycle))
        return None
        
    
    state = thiscandidate.cand_office_st
    term_class = None
    if thiscandidate.cand_office == 'S':
        term_class = get_term_class_from_election_year(thiscandidate.cand_election_year)
    
    
    cand = Candidate.objects.create(
            office_district=thiscandidate.cand_office_district,
            cycle=cycle,
            fec_id=candidate_id,
            name=thiscandidate.cand_name,
            slug = slugify(thiscandidate.cand_name)[:50],
            pty=thiscandidate.cand_pty_affiliation,
            party = get_party_from_pty(thiscandidate.cand_pty_affiliation),
            pcc=thiscandidate.cand_pcc,
            term_class=term_class,
            election_year=thiscandidate.cand_election_year,
            state=thiscandidate.cand_office_st,
            office=thiscandidate.cand_office,
            fec_data_update_time = timezone.now(),
    )
    return cand
    

    

    
def make_committee_overlay_from_masterfile(committee_id, cycle, verify_does_not_exist=True):
    if committee_id in blacklisted_committees:
        return None
        
    c = None
    try:
        c = FTP_Committee.objects.get(cmte_id=committee_id, cycle=cycle)
    except Committee.MultipleObjectsReturned:
        logger.info("Multiple committees found with id=%s cycle=%s!" % (committee_id, cycle))
        return None
    
    if verify_does_not_exist:
        try:
            Committee.objects.get(fec_id=committee_id, cycle=cycle)
            return None
        except Committee.DoesNotExist:
            pass

                
    # Make senate committees paper filers by default. 
    ctype = c.cmte_tp
    is_paper_filer = False
    if ctype:
        if ctype.upper() in ['S']:
            is_paper_filer = True
        
    party = c.cmte_pty_affiliation
    if party:
        party = get_party_from_pty(party)
    
    cm = Committee.objects.create(
        cycle = cycle,
        name = c.cmte_name,
        fec_id = c.cmte_id,
        slug = slugify(c.cmte_name)[:50],
        party = party,
        treasurer = c.tres_nm,
        street_1 = c.cmte_st1,
        street_2 = c.cmte_st2,
        city = c.cmte_city,
        state = c.cmte_st,
        connected_org_name = c.connected_org_nm,
        filing_frequency = c.cmte_filing_freq,
        candidate_id = c.cand_id,
        designation = c.cmte_dsgn,
        ctype = ctype,
        is_dirty=True,
        is_paper_filer=is_paper_filer,
        fec_data_update_time = timezone.now(),
    )
    
    return cm
    
    

"""
from efilings.utils.overlay_utils import make_candidate_overlay_from_masterfile
make_candidate_overlay_from_masterfile('H0CA48024', '2016') # issa

from efilings.utils.overlay_utils import make_committee_overlay_from_masterfile
make_committee_overlay_from_masterfile('C00542779', '2016')


"""