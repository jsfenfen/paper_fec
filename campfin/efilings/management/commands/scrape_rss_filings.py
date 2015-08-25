"""
Get new filings from the FEC's new feed of electronic filings. It shows all filings for last 7 days. 

FEC caches their feed of new electronic filings by 5 minutes. 
That's too slow (but better than when it used to be 30 minutes). 
Another (parallel) approach is in find_new_filigs, which just looks where it thinks the next filings should be.

"""

import urllib2, re, logging, os, sys
from lxml import etree
from StringIO import StringIO

from django.core.management.base import BaseCommand, CommandError
from efilings.models import Filing
from efilings.utils.update_utils import set_update
from django.conf import settings
from django.utils import timezone

# put the parsing directory stuff on the path -- needs more sane setup
sys.path.append(settings.PARSING_DIR)
from read_FEC_settings import FILECACHE_DIRECTORY, USER_AGENT, FEC_DOWNLOAD, DELAY_TIME, CYCLE


# Get an instance of a logger
logger = logging.getLogger(__name__)

# pull the filng number from the link. Will break, duh, if the link changes. 
filing_number_re = re.compile('<link>\s*http://docquery.fec.gov/dcdev/posted/(\d+).fec\s*</link>')

def enter_or_skip_filing(filing_number):
    """ 
    There's lotsa information available from the feed, and one could do more with it.
    But results are more uniform if all data is entered with the same routine. 
    That means a slight delay (seconds?) required to download the filings 
    in a subsequent step, then process them in another. 
    
    This script just creates the filing object if it doesn't exist.
    """
    # Now is EDT, 
    now = timezone.now()
    obj, created = Filing.objects.get_or_create(filing_number=filing_number, filing_type="E", defaults = {'process_time':now, 'discovery_method':'R'})
    return created

def parse_xml_from_text(xml):
    tree = etree.parse(StringIO(xml))
    results = []
    print tree
    
    for  elt in tree.getiterator('item'):
        stringtext =  etree.tostring(elt)
        filing_number_groups = re.search(filing_number_re, stringtext)
        if filing_number_groups:
            filing_number = filing_number_groups.group(1)
            results.append(filing_number)
        else:
            logger.error('SCRAPE_RSS_FILINGS Couldn\'t find filing number in RSS feed element: %s' % stringtext)
    return results

class Command(BaseCommand):
    """  Creates new_filing objects from RSS feed. Will set cycle if possible. """
    requires_system_checks = False
    
    def handle(self, *args, **options):
        
        new_filings = 0
        rss_url = "http://efilingapps.fec.gov/rss/generate?preDefinedFilingType=ALL"
        
        logger.info('SCRAPE_RSS_FILINGS - starting regular run')
        headers = {'User-Agent': USER_AGENT}   
        data = None       
        req = urllib2.Request(rss_url, data, headers)
        response = urllib2.urlopen(req)
        rssdata = response.read()
        
        #print rssdata
        results = parse_xml_from_text(rssdata)
        for filing_number in results:
            filing_entered = enter_or_skip_filing(filing_number)
            if filing_entered:
                new_filings += 1
        
        # log the results of this run
        logger.info("SCRAPE_RSS_FILINGS - completing regular run--created %s new filings" % new_filings)
        # update the global scrape time (don't do this at the start 
        # of the script in case it dies before completion). 
        set_update('scrape_rss_filings')
        
        
