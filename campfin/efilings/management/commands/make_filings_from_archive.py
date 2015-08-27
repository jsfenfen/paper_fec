"""
Creates empty filing objects by searching the filng directory.
Intended to be run when creating from archived files. 

"""

import re, logging, os, sys

from django.core.management.base import BaseCommand, CommandError
from efilings.models import Filing
from django.conf import settings
from django.utils import timezone

# put the parsing directory stuff on the path -- needs more sane setup
sys.path.append(settings.PARSING_BASE_DIR)
from parsing.read_FEC_settings import FILECACHE_DIRECTORY, USER_AGENT, FEC_DOWNLOAD, DELAY_TIME, CYCLE


# Get an instance of a logger
logger = logging.getLogger(__name__)

fec_format_file = re.compile(r'\d+\.fec')

def enter_or_skip_filing(filing_number):
    """ 
    
    This script just creates the filing object if it doesn't exist.
    """
    # Now is EDT, 
    now = timezone.now()
    # set discovery method to 'A' for archive
    # in general, the process_time should be ignored for type = A. 
    obj, created = Filing.objects.get_or_create(filing_id=filing_number, filing_number=filing_number, filing_type="E", defaults = {'process_time':now, 'discovery_method':'A'})
    return created
    
class Command(BaseCommand):
    """  Creates new_filing objects from RSS feed. Will set cycle if possible. """
    requires_system_checks = False
    
    def handle(self, *args, **options):
        new_filings = 0
        
        # Process all .fec files in the FILECACHE_DIRECTORY
        for d, _, files in os.walk(FILECACHE_DIRECTORY):
            for this_file in files:

                # Ignore it if it isn't a numeric fec file, e.g. \d+\.fec
                if not fec_format_file.match(this_file):
                    continue

                filingnum = this_file.replace(".fec", "")
        
                filing_entered = enter_or_skip_filing(filingnum)
                if filing_entered:
                    new_filings += 1
        
        
        # log the results of this run
        logger.info("Completing archive entry run--created %s new filings" % new_filings)

        
