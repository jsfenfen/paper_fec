"""
look for new filings by just testing filing numbers. This is a hack to deal with the fact that
the feed is too slow. 
"""

import urllib2, sys, logging
from time import sleep
from django.utils import timezone


from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from efilings.models import Filing
from efilings.utils.update_utils import set_update

# put the parsing directory stuff on the path -- needs more sane setup
sys.path.append(settings.PARSING_BASE_DIR)
from parsing.read_FEC_settings import FILECACHE_DIRECTORY, USER_AGENT, FEC_DOWNLOAD, DELAY_TIME, CYCLE



logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Find files by incrementing the filing number."
    requires_system_checks = False
    
    def handle(self, *args, **options):
        
        logger.info('FIND_NEW_FILINGS - starting regular run')
        
        highest_filing_number = Filing.objects.all().order_by('-filing_number')[0].filing_number
        logger.info("highest previously available filing number: %s" % (highest_filing_number))
        trial_file_number = highest_filing_number
        highest_available_file_number = highest_filing_number
        file_misses = 0
        file_miss_threshold = 3
        new_files = 0
        
        while True:
            trial_file_number += 1 
            location = FEC_DOWNLOAD % (trial_file_number)
            try:
                result = urllib2.urlopen(location)
                logger.info("FIND_NEW_FILINGS: found new filing %s" % (location))
                now = timezone.now()
                obj, created = Filing.objects.get_or_create(filing_id=trial_file_number, filing_number=trial_file_number, filing_type="E", defaults = {'process_time':now, 'discovery_method':'F'})
                if created:
                    new_files += 1
                                

            except urllib2.HTTPError:
                logger.info("FIND_NEW_FILINGS: filing unavailable at %s" % (location))
                file_misses += 1
                
            if file_misses >= file_miss_threshold:
                break
                
            sleep(1)
            logger.info("FIND_NEW_FILINGS - completing regular run--created %s new filings" % new_files)
        
        # set the update time. 
        set_update('incremental_find_filings')

