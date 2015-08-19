import re
import csv
from utils import utf8_clean, clean_entry

from read_FEC_settings import FILECACHE_DIRECTORY, PAPER_FILECACHE_DIRECTORY
from header_parser import parse_header


# Current FCC files are delimited by ascii 28
new_delimiter = chr(28)
# electronic versions less than 6 (so through 5.3) use a comma
old_delimiter = ','

## very old versions are really in .csv format, so strictly splitting on commas doesn't work:
# 23132
# "HDR","FEC","3.00","Vocus, Inc. PACPRO","6.16.099","","FEC-22522",1,""



## adapted from FECH: https://github.com/NYTimes/Fech/blob/master/lib/fech/rendered_maps.rb

######  !! All the header stuff needs to be refactored somewhere else--just assembling it here for now. 

# versions 3-5
old_headers = ['record_type', 'ef_type', 'fec_version', 'soft_name', 'soft_ver', 'name_delim', 'report_id', 'report_number']

# versions 6+
new_headers = ['record_type', 'ef_type', 'fec_version', 'soft_name', 'soft_ver', 'report_id', 'report_number']

## paper headers
paper_headers_v1 = ['record_type', 'fec_version', 'vendor', 'batch_number']
# versions 2.2 - 
paper_headers_v2_2 = ['record_type', 'fec_version', 'vendor', 'batch_number']
paper_headers_v1 = ['record_type', 'fec_version', 'vendor', 'batch_number', 'report_id']



class filing(object):


    # FEC-assigned filing number
    filing_number = None
    # What FEC version is it
    version = None

    # Array of filing goes here
    filing_lines = []

    # what's the filing number given in the header?
    is_amendment = None
    # what's the original being amended?
    filing_amended = None
    page_read = None
    headers = {}
    headers_list = []
    
    use_new_delimiter = True
    csv_reader = None
    

    def __init__(self, filing_number, is_paper=False):
        self.filing_number = filing_number
        # is this a paper filing? 
        self.is_paper = is_paper
        self.headers['filing_number'] = filing_number
        # This is where we *expect* it to be 
        if self.is_paper:
            self.local_file_location = "%s/%s.fec" % (PAPER_FILECACHE_DIRECTORY, self.filing_number)
            
        else:
            self.local_file_location = "%s/%s.fec" % (FILECACHE_DIRECTORY, self.filing_number)
        
        self.fh = open(self.local_file_location, 'r')
        
        # read the first row to see what kind of file we're dealing with
        self.header_row = self.fh.readline()    
        # sniff for a delimiter; 
        if self.header_row.find(new_delimiter) > -1:
            self.use_new_delimiter = True
            self.headers_list = new_headers
            # go back to zero
            self.fh.seek(0)
            
        else:
            self.use_new_delimiter = False
            self.headers_list = old_headers
            # We're going to read the file like a csv, so start again at zero:
            self.fh.seek(0)
            self.csv_reader = csv.reader(self.fh)
        
        
        self.is_error = not self._parse_headers()
        

    def _get_next_fields(self):
        if self.use_new_delimiter:
            nextline = self.fh.readline()
            if nextline:
                return [utf8_clean(i) for i in nextline.split(new_delimiter)]
            else:
                return None
        else:
            try:
                return [utf8_clean(i) for i in self.csv_reader.next()]
            except StopIteration:
                return None
        

    def _parse_headers(self):

        header_arr = self._get_next_fields()
        summary_line = self._get_next_fields()
        self.form_row = summary_line
        
        # amendment number - not sure what version it starts in. 
        #if len(summary_line) > 6:
        #    self.headers['report_num'] = clean_entry(summary_line[6])[:3]

        self.headers = parse_header(header_arr, self.is_paper)
        self.headers['filing_amended'] = None
        self.headers['report_num'] = None
        self.version = self.headers['fec_version']
        
        
        # These are always consistent ## Are they? 
        try:
            self.headers['form'] = clean_entry(summary_line[0])
            self.headers['fec_id'] = clean_entry(summary_line[1])
        except IndexError:
            return False
        
        # figure out if this is an amendment, and if so, what's being amended.
        
        form_last_char = self.headers['form'][-1].upper()
        if form_last_char == 'A':
            self.is_amendment = True
            self.headers['is_amendment'] = self.is_amendment
            
            if self.is_paper:
                self.headers['filing_amended'] = None
            else:
                # Listing the original only works for electonic filings, of course! Paper filings don't include this--which is insane when you think about it. 
    
                print "Found amendment %s : %s " % (self.filing_number, self.headers['report_id'])
                amendment_match = re.search('^FEC\s*-\s*(\d+)', self.headers['report_id'])
    
                if amendment_match:
                    original = amendment_match.group(1)
                    #print "Amends filing: %s" % original
                    self.headers['filing_amended'] = original

                else:
                    raise Exception("Can't find original filing in amended report %s" % (self.filing_number))
        else:
            self.is_amendment = False
            self.headers['is_amendment'] = self.is_amendment
            


        return True


    def get_headers(self):
        """Get a dictionary of file data"""
        return self.headers

    def get_error(self):
        """Was there an error?"""
        return self.is_error

    def get_first_row(self):
        return(self.form_row)

    """ deprecated """
    def get_raw_first_row(self):
        return(self.form_row)
    
    def get_filer_id(self):
        return self.headers['fec_id']

    def get_body_row(self):
        """get the next body row"""
        next_line = ''
        while True:
            next_line = self._get_next_fields()
            if next_line:
                if "".join(next_line).isspace():
                    continue
                else:
                    return next_line
            else:
                break

    def get_form_type(self):
        """ Get the base form -- remove the A, N or T (amended, new, termination) designations"""
        try:
            raw_form_type = self.headers['form']
            a = re.search('(.*?)[A|N|T]', raw_form_type)
            if (a):
                return a.group(1)
            else:
                return raw_form_type

        except KeyError:
            return None

    def get_version(self):
        try:
            return self.version
        except KeyError:
            return None

    def dump_details(self):
        print "filing_number: %s ; self.headers: %s" % (self.filing_number, self.headers)



"""


767168 -- 8.2 mb
from filing import filing
a = filing(767168)

"""