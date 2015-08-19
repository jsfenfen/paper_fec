""" Util to download the zipped, raw OCR'ed paper fec files from the FEC ftp site and unzip them directly to the filecache directory. Assumes we can use unzip at the cmd prompt... """

import re
from datetime import date, timedelta
from dateutil.parser import parse
from os import system
from time import sleep
from argparse import ArgumentParser


from urllib2 import URLError

from parsing.read_FEC_settings import FEC_FILE_LOCATION, USER_AGENT, PAPER_ZIP_DIRECTORY, PAPER_FILECACHE_DIRECTORY, DELAY_TIME

from parsing.utils import download_with_headers


# Default to everything filed this year. 
default_end_date = date.today()
default_start_date = date(default_end_date.year,1,1)
one_day = timedelta(days=1)


# the supported format is anything that dateutil.parser will support--but... 
parser = ArgumentParser()
parser.add_argument('--start', '-s', action='store', help='Set a start date of the time range to download; YYYYMMDD format is supported', default=default_start_date.strftime("%Y%m%d"))
parser.add_argument('--end', '-e', action='store', help='Set an end date of the time range to download; YYYYMMDD format is supported', default=default_end_date.strftime("%Y%m%d"))
args = parser.parse_args()


file_regex = re.compile(r'(\d{8})\.zip')

def main():
    
    end_date = parse(args.end)
    start_date = parse(args.start)
    print "Downloading files from %s to %s ; zip files will be saved to %s and unarchived to %s" % (args.start, args.end, PAPER_ZIP_DIRECTORY, PAPER_FILECACHE_DIRECTORY)
    
    # get the current directory listing
    ftp_paper_listing = download_with_headers("ftp://ftp.fec.gov/FEC/paper/")
    
    for line in ftp_paper_listing.split("\n"):
        results = file_regex.search(line)
        if results:
            filedatestring =  results.groups()[0]
            filename = filedatestring + ".zip"
            filelocation = "ftp://ftp.fec.gov/FEC/paper/" + filename
            filedate = parse(filedatestring)
            if filedate >= start_date and filedate <= end_date:
                print "found file: %s" % (filelocation)
                
                downloaded_zip_file = PAPER_ZIP_DIRECTORY + "/" + filename
                dfile = open(downloaded_zip_file, "w")
                dfile.write(download_with_headers(filelocation))
                dfile.close()

                # Now unzip 'em 
                cmd = "unzip -q -o %s -d %s" % (downloaded_zip_file, PAPER_FILECACHE_DIRECTORY)
                print "Now unzipping with %s" % (cmd)
                system(cmd)

                # Pause 
                print "Now sleeping for a %s second(s)" % (DELAY_TIME)
                sleep(DELAY_TIME)
            



if __name__ == "__main__":
    main()