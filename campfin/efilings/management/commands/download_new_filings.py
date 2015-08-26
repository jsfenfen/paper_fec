import subprocess, sys, logging
from time import sleep
from os import path
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings

from efilings.models import Filing

sys.path.append(settings.PARSING_BASE_DIR)
from parsing.read_FEC_settings import FILECACHE_DIRECTORY, USER_AGENT, FEC_DOWNLOAD, DELAY_TIME


logger = logging.getLogger(__name__)

max_retry_days = 7 # stop trying to download filings more than 7 days old. 

class Command(BaseCommand):
    help = "Download files from FEC. Mark them as having been downloaded."
    requires_system_checks = False
    
    def handle(self, *args, **options):
        logger.info('DOWNLOAD_NEW_FILINGS - starting regular run')
        
        now = timezone.now()
        recent_start = now - timedelta(days=max_retry_days)
        new_filings = Filing.objects.filter(filing_is_downloaded="0", process_time__gte=recent_start).order_by('filing_number')
        for filing in new_filings:

            location = FEC_DOWNLOAD % (filing.filing_number)
            local_location = FILECACHE_DIRECTORY + "/" + str(filing.filing_number) + ".fec"
            
            # only get it if it's not there. 
            # FEC is pretty good about not posting defective files
            # but if that becomes an issue this logic should reflect that.
            if not path.isfile(local_location):
                cmd = "curl \"%s\" -o %s" % (location, local_location)
                # run it from a curl shell
                proc = subprocess.Popen(cmd,shell=True)
                # pause for a bit
                sleep(DELAY_TIME)
            
            # Putting the file check after the 1 second sleep gives better results; sometimes it appears absent if it's not before
            # if it's there when we're done, mark it as downloaded
            if path.isfile(local_location):
                filing.filing_is_downloaded="1"
                filing.save()
            else:
                print "MISSING: %s" % (filing.filing_number)
                logger.info("DOWNLOAD_NEW_FILINGS downloaded filing is missing ?: %s" % (filing.filing_number))
                

            