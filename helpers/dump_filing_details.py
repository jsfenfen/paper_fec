"""
Grab filing info for 2015/2016 from Sunlight's realtime; requires an API key.
results include timestamp that files were submitted
can be used to simulate filing frequency of a filing deadline
use semi/non-documented args passed to their API
each line is json representation of 100 filings
so the file isn't valid json; only individual lines are

See filing deadlines here http://www.fec.gov/info/report_dates_2014.shtml
big days: Oct. 15 (Q3); Oct. 20 (Sept. monthly) Oct. 23 (Pre-general)
"""

import requests, json, csv
from time import sleep
from collections import defaultdict


from SUNLIGHT_APIKEY import APIKEY
BASE_URL = "http://realtime.influenceexplorer.com/api/new_filing/"

# Date arg needs "YYYY-MM-DD" format
dates_to_import = ["2014-10-15", "2014-10-20", "2014-10-23"] 

# 100 is API max
base_params = {'page_size':100, 'apikey':APIKEY} 

field_names = ["filing_number","time_filed","form_type","skeda_lines","skedb_lines","skede_lines", "other_lines","total_lines"]

def write_results_to_csv(writer, results):
    for result in results:
        print result
        result['time_filed'] = result['process_time_formatted']
        lines_present = defaultdict(lambda:0, json.loads(result['lines_present']))
        result['skeda_lines'] = int(lines_present['A'])
        result['skedb_lines'] = int(lines_present['B'])
        result['skede_lines'] = int(lines_present['E'])
        result['other_lines'] = int(lines_present['O'])
        result['total_lines'] = ( result['skeda_lines'] + result['skedb_lines'] 
            + result['skede_lines'] + result['other_lines'] )

        dw.writerow(result)
        
for import_date in dates_to_import:
    outfile = open(import_date + ".csv" ,"w")
    
    outfile.write(",".join(field_names) +"\n")
    dw = csv.DictWriter(outfile, fieldnames=field_names, restval='', extrasaction='ignore')
    
    page_number=1
    request_params = base_params
    request_params.update({'filed_before':import_date, 
        'filed_after':import_date})
    
    while True:
        
        request_params['page'] = page_number
        print "Retrieving request params: %s" % request_params
    
        api_response = requests.get(BASE_URL, request_params)
        response_data = api_response.json()
        results = response_data['results']
        #outfile.write(json.dumps(results) + "\n")
        write_results_to_csv(dw, results)
        next_page = response_data['next']
        page_number += 1
        if not next_page:
            break
    
        sleep(0.5) # be nice-ish to them. 
        
    outfile.close()
