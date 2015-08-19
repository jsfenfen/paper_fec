"""
Parse a header row, passed in as an array. This should happen after a delimiter has been detected and the line properly split, whether it's a delimited or csv style line. 

There are different methods for paper and electronic filings; because these come from different locations we're assuming we know what we're handling ahead of time. 

The logic here is analogous to what's used in line parser with the HDR.csv file, but for architectural reasons we don't want the overhead of attaching line parsers to filings. 

We still maintain the HDR.csv file, but don't actually read from it. 


"""
import re
from utils import clean_entry


# versions 3-5
old_eheaders = ['record_type', 'ef_type', 'fec_version', 'soft_name', 'soft_ver', 'name_delim', 'report_id', 'report_number']
# versions 6+
new_eheaders = ['record_type', 'ef_type', 'fec_version', 'soft_name', 'soft_ver', 'report_id', 'report_number']

# regexes to choose electronic headers from version numbers
old_eheaders_re = re.compile(r'^[3|4|5]')
new_eheaders_re = re.compile(r'^[6|7|8]')


## paper headers
paper_headers_v1 = ['record_type', 'fec_version', 'vendor', 'batch_number']
# versions 2.2 - 
paper_headers_v2_2 = ['record_type', 'fec_version', 'vendor', 'batch_number']
paper_headers_v2_6 = ['record_type', 'fec_version', 'vendor', 'batch_number', 'report_id']

paper_headers_v1_re = re.compile(r'^P1\.0')
paper_headers_v2_2_re = re.compile(r'^P2\.2|^P2\.3|^P2\.4')
paper_headers_v2_6_re = re.compile(r'^P2\.6|^P3\.0|^P3\.1')

class UnknownHeaderError(Exception):
 pass
 
def parse_header(header_array, is_paper=False):
    
    if not is_paper:
        version = clean_entry(header_array[2])
        
        if old_eheaders_re.match(version):
            headers_list = old_eheaders
        elif new_eheaders_re.match(version):
            headers_list = new_eheaders
        else:
            raise UnknownHeaderError ("Couldn't find parser for electronic version %s" % (version))
        
    else:
        version = clean_entry(header_array[1])
        
        if paper_headers_v1_re.match(version):
            headers_list = paper_headers_v1
        elif paper_headers_v2_2_re.match(version):
            headers_list = paper_headers_v2_2
        elif paper_headers_v2_6_re.match(version):
            headers_list = paper_headers_v2_6
        else:
            raise UnknownHeaderError ("Couldn't find parser for paper version %s" % (version))
        
    
    headers = {}   
    for i in range(0, len(headers_list)):
        # It's acceptable for header rows to leave off delimiters, so enter missing trailing args as blanks
        this_arg = ""
        try:
            this_arg = clean_entry(header_array[i])

        except IndexError:
            pass

        headers[headers_list[i]] = this_arg
    
    return headers