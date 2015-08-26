"""
This command *is intended* to put the task of processing 
and entering line itemizations into the database by queuing them
via an application like celery in a context that's not django depenent

The below simply executes the command from within django.

"""
import sys, os, logging

from django.core.management.base import BaseCommand, CommandError


# first put the parsing stuff on the path
from django.conf import settings
sys.path.append(settings.PARSING_BASE_DIR)

## get a form parser to hand off; we wouldn't do this if it was queued.
from parsing.form_parser import form_parser


## don't import the celery version, not included with this distribution
# from celeryproj.tasks import process_filing_body_celery
## instead just get the actual code
from parsing.utils.filing_body_processor import process_filing_body

from efilings.models import Filing

# Get a logger
logger = logging.getLogger(__name__)


# Don't bother with these
excluded_filings_list = ['F1', 'F2', 'F1M']

class Command(BaseCommand):
    help = "Queue filing body row entry for execution by celery processes"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        fp = form_parser()
        
        filings_to_queue = Filing.objects.filter(filing_is_downloaded="1", header_is_processed="1", previous_amendments_processed="1", data_is_processed="0").order_by('filing_number').exclude(form_type__in=excluded_filings_list)
        for filing in filings_to_queue:
            ######### don't actually do this
            msg = "send_body_row_jobs: Adding filing %s to entry queue" % (filing.filing_number)
            print msg
            logger.info(msg)            
            #process_filing_body_celery.apply_async([filing.filing_number], queue='slow',routing_key="slow")
            
            # Passing in the fp means we don't have to create a new one each time
            # Giving it the logger will record output in django logs.
            process_filing_body(filing.filing_number, fp, logger)
