"""
This parses the form line of a new filing and adds it as an hstore on the filing.
A subsequent script (set_new_filing_details) actually sets the data from that hstore.
These two scripts could be combined, but keeping them separate allows us to mark
when a form parsing error takes place, as opposed to a data assignment error. 
"""


import sys, os, logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from efilings.models import Filing

# Add parsing dir to path
sys.path.append(settings.PARSING_DIR)
# And parentdir, crap

sys.path.append(os.path.dirname(settings.PARSING_DIR))

from form_parser import form_parser, ParserMissingError
from filing import filing
from read_FEC_settings import FILECACHE_DIRECTORY


#from formdata.models import Filing_Header
from efilings.utils.filing_processors import process_new_filing

# Get an instance of a logger
logger = logging.getLogger(__name__)

# load up a form parser
fp = form_parser()


class Command(BaseCommand):
    help = "Enter file header from forms that have been downloaded; don't mark them as either amended or not."
    requires_system_checks = False

    def handle(self, *args, **options):
        logger.info('ENTER_HEADERS_FROM_NEW_FILINGS - starting regular run')
        
        downloaded_filings = Filing.objects.filter(filing_is_downloaded="1", header_is_processed="0").order_by('filing_number')
        for filing in downloaded_filings:
            result_header = None
            logger.info('ENTER_HEADERS_FROM_NEW_FILINGS - processing %s' % (filing.filing_number))
            
            try: 
                result_header = process_new_filing(filing, fp=fp, filing_time=filing.process_time, filing_time_is_exact=True)
            ## It seems like the FEC's response is now to give a page not found response instead of a 500 error or something. The result is that the except no longer seems to apply. 
            except IOError:
                # if the file's missing, keep running. 
                logger.error("Filing marked as downloaded is unavailable: %s" % (filing.filing_number))
                # Mark that an error has occurred.
                filing.header_is_processed = 'E'
                filing.save()
                
                continue
            if result_header:
                filing.header_is_processed="1"
                filing.save()
            else:
                
                logger.error("Header not created right: %s" % (filing.filing_number))
                filing.header_is_processed = 'E'
                filing.save()
                
                