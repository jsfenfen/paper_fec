import sys, logging
from dateutil.parser import parse as dateparse

from django.db import connection, transaction
from django.core.management.base import BaseCommand, CommandError

from efilings.models import Filing


from django.conf import settings
# Put parsing dir on path
sys.path.append(settings.PARSING_BASE_DIR)
from parsing.read_FEC_settings import FILECACHE_DIRECTORY, USER_AGENT, FEC_DOWNLOAD, DELAY_TIME
from parsing.utils.cycle_utils import get_cycle_from_date
from parsing.form_parser import form_parser, ParserMissingError
from parsing.filing import filing

logger = logging.getLogger(__name__)


cursor = connection.cursor()


def process_new_filing(thisnewfiling, fp=None, filing_time=None, filing_time_is_exact=False):
    """ Enter the file header if needed.  """
       
    if not fp:
        fp = form_parser()
        
    #print "Processing filing %s" % (filingnum)
    f1 = filing(thisnewfiling.filing_number)
    if f1.get_error():
        return False
        
    form = f1.get_form_type()
    version = f1.get_version()

    ## leave the form if it's already been entered-- that's where it says if it is terminated. 
    if not thisnewfiling.form_type:
        thisnewfiling.form_type = form
        
    # check if it's an amendment based on form types -- if so, mark it. Otherwise the F1's will look like they haven't been amended. 
    try:
        if thisnewfiling.form_type[-1].upper() == 'A':
            thisnewfiling.is_amendment = True
    except IndexError:
        pass

    # only parse forms that we're set up to read
    if not fp.is_allowed_form(form):
        logger.info("Not a parseable form: %s - %s" % (form, thisnewfiling.filing_number))
        
        if thisnewfiling.is_amendment:
            thisnewfiling.save()
        return True

    header = f1.get_first_row()
    header_line = fp.parse_form_line(header, version)

    amended_filing=None
    if f1.is_amendment:
        amended_filing = f1.headers['filing_amended']


    
    from_date = None
    through_date = None
    #print "header line is: %s " % header_line
    try:
        # dateparse('') will give today, oddly
        if header_line['coverage_from_date']:
            from_date = dateparse(header_line['coverage_from_date'])
            if from_date:
                thisnewfiling.cycle = get_cycle_from_date(from_date)
    except KeyError:
        logger.debug("KeyError for coverage_from_date in %s" % thisnewfiling.filing_number)
        
    try:                
        if header_line['coverage_through_date']:
            through_date = dateparse(header_line['coverage_through_date'])
            if through_date:
                thisnewfiling.cycle = get_cycle_from_date(through_date)
    except KeyError:
        logger.debug("KeyError for coverage_through_date in %s" % thisnewfiling.filing_number)

    
    # Create the filing -- but don't mark it as being complete. 
    
    
    thisnewfiling.fec_id = f1.headers['fec_id']
    thisnewfiling.coverage_from_date = from_date
    thisnewfiling.coverage_to_date = through_date
    thisnewfiling.is_amendment = f1.is_amendment
    thisnewfiling.amends_filing = amended_filing
    thisnewfiling.amendment_number = f1.headers['report_number'] or None
    thisnewfiling.header_data = header_line
    
    thisnewfiling.save()
    
    return True

