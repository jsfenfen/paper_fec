import logging

from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse
from efilings.models import Filing

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Mark the originals as being amended."
    requires_system_checks = False
    

    def handle(self, *args, **options):
        
        all_new_amendment_headers = Filing.objects.filter(previous_amendments_processed="0",new_filing_details_set="1").order_by('filing_number')
        for new_amended_filing in all_new_amendment_headers: 
            if new_amended_filing.is_amendment:
                filing_num = new_amended_filing.filing_number
                
                try:
                    original = Filing.objects.get(filing_number=new_amended_filing.amends_filing)
                    logger.info("Writing amended original: %s %s" % (original.filing_number, filing_num))                        
                    original.is_superceded=True
                    original.amended_by = new_amended_filing.filing_number
                    original.save()
                        
                except Filing.DoesNotExist:
                    logger.info("Could not find original filing (%s) amended by later filing (%s). Probably it is from an earlier cycle." % (new_amended_filing.amends_filing,new_amended_filing.filing_number))
            
    
                # Now find others that amend the same filing 
                earlier_amendments = Filing.objects.filter(is_amendment=True,amends_filing=new_amended_filing.amends_filing, filing_number__lt=filing_num)
                for earlier_amendment in earlier_amendments:
                    logger.info("Handling prior amendment: %s %s" % (earlier_amendment.filing_number, new_amended_filing.filing_number))
                    earlier_amendment.is_superceded=True
                    earlier_amendment.amended_by = filing_num
                    earlier_amendment.save()

            # mark that this has had it's amendments processed:
            new_amended_filing.previous_amendments_processed = "1"
            new_amended_filing.save()
