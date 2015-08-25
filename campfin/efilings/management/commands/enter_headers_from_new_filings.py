import sys, os

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

# load up a form parser
fp = form_parser()


class Command(BaseCommand):
    help = "Enter file header from forms that have been downloaed; don't mark them as either amended or not."
    requires_system_checks = False

    def handle(self, *args, **options):
        downloaded_filings = Filing.objects.filter(filing_is_downloaded="1", header_is_processed="0").order_by('filing_number')
        for filing in downloaded_filings:
            print "Entering filing %s, entry_time %s" % (filing.filing_number, filing.process_time)
            result_header = None
            try: 
                result_header = process_new_filing(filing, fp=fp, filing_time=filing.process_time, filing_time_is_exact=True)
            ## It seems like the FEC's response is now to give a page not found response instead of a 500 error or something. The result is that the except no longer seems to apply. 
            except IOError:
                # if the file's missing, keep running. 
                print "MISSING FILING: %s" % (filing.filing_number)  
                continue
            if result_header:
                filing.header_is_processed=True
                filing.save()
            else:
                print "Header not created right... %s" % (filing)