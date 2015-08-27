"""
Utility to download the zipped, raw fec files from the FEC ftp site and unzip them directly to the filecache directory.
If we do this ahead of time, we don't need to hit their site tons of times to backfill / analyze older data.
Assumes we can use unzip at the cmd prompt.
"""
from argparse import ArgumentParser
from datetime import date, timedelta
from dateutil.parser import parse
from os import system
from time import sleep

from urllib2 import URLError

from parsing.read_FEC_settings import FEC_FILE_LOCATION, USER_AGENT, ZIP_DIRECTORY, FILECACHE_DIRECTORY, DELAY_TIME
from parsing.utils.parsing_utils import download_with_headers

# Note that 2011/12/04, 2012/07/01, 2012/12/15, 2012/12/25 do not exist; presumably no filings were received on these days.

# Default to everything filed this year. 
default_end_date = date.today()
default_start_date = date(default_end_date.year,1,1)
one_day = timedelta(days=1)


# the supported format is anything that dateutil.parser will support--but... 
parser = ArgumentParser()
parser.add_argument('--start', '-s', action='store', help='Set a start date of the time range to download; YYYYMMDD format is supported', default=default_start_date.strftime("%Y%m%d"))
parser.add_argument('--end', '-e', action='store', help='Set an end date of the time range to download; YYYYMMDD format is supported', default=default_end_date.strftime("%Y%m%d"))
args = parser.parse_args()

def main():
    

    
    end_date = parse(args.end)
    this_date = parse(args.start)
    print "Downloading files from %s to %s ; zip files will be saved to %s and unarchived to %s" % (args.start, args.end, ZIP_DIRECTORY, FILECACHE_DIRECTORY)
    while (this_date < end_date):
        datestring = this_date.strftime("%Y%m%d")
        file_to_download = FEC_FILE_LOCATION % datestring
        # print "Downloading: %s" % (file_to_download)
        this_date += one_day
        
        downloaded_zip_file = ZIP_DIRECTORY + "/" + datestring + ".zip"
        try:
            retrieved_file = download_with_headers(file_to_download)
        
        except URLError:
            print "Couldn't retrieve file for %s -- skipping" % (datestring)
            continue
    
        dfile = open(downloaded_zip_file, "w")
        dfile.write(retrieved_file)
        dfile.close()
    
        # Now unzip 'em; they all go in the same folder--in other words, we're not preserving the file hierarchy. 
        cmd = "unzip -q -o %s -d %s" % (downloaded_zip_file, FILECACHE_DIRECTORY)
        # print "Now unzipping with %s" % (cmd)
        system(cmd)
    
        # Pause 
        sleep(DELAY_TIME)

if __name__ == "__main__":
    main()