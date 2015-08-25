
##Overview

There are several different loading processes that must be run to keep things current.


* Quick .fec file ingestion: New files are collected, information that's available without processing them line by line is set, and older filings that are being replaced are marked as such. Can be run in a cron job every few minutes.

* Processing of line itemizations: Enter the line itemizations from new filings. Since filings can be large, it's recommended that this job be triggered by cron, but processing itself should be queued. Scripts to do this part do not depend on django.

* Set values after line itemization is complete: Some forms do not include totals, so these totals must be set once all line items have been entered.

* Periodic committee and candidate aggregation: Periodically recalculate the total raised and spent by candidates and committees. Candidate totals are based only on authorized committees listed as such in the candidate-committee linkage file; leadership accounts are not included.


* Daily updates: Set candidate, committee and candidate committee linkage files from the FEC's master files, which are updated daily. Data copied directly from the FEC's files lives in FTPData, and is wiped and rewritten onload. Copy the data from this app to the campfin app so that hand-edited changes remain. 




### Quick .fec file ingestion

These steps retrieve and process the efilings by entering summary data into the filing model, and itemized data into the appopriate model. Some updates are made to the filing model once the body data is completely entereed. 

This process doesn't load or set committee or candidate data or aggregates. 

#### Find new filings

There are really three ways to locate newly filed .fec documents:

- query an interactive FEC page
- hit the RSS feed of new filings (which is regenerated on their end at 5-minute intervals)
- Simply look for documents at the location where we expect them to arrive, because that locations is uniquely determined by their numeric filing number. 

The approach I've taken is to do both two and three. Hitting the query page is in violation of robots.txt (other things may be as well) but seemed nicer to me. Occasionally people get IP-banned from this site, and hitting a db query (as opposed to a cached feed or a single url) just seemed nicer. This stuff is fairly trivial, so YMMV. 

The RSS feed contains a substantial amount of information, but just blinding hitting a single URL provides no data. In general I just create a filing object once we know one exists, and populate the data from the header in a subsequent step. 

Relevant scripts: **scrape_rss_filings** hits the rss feed; **find_filings** looks for filings based on the highest available fiiling number. Note that it's possible for find_filings to *miss* filings if they land out of order (this seems to not really happen), so it's important to keep running the rss script, which will catch anything that was missed. You could rely exclusively on the feed, it's just up to 5 minutes out of date. I haven't run find_filings more than once every few minutes, but it should be fine to run once a minute or so. 

Either script should create the filing object, but set the filing_is_downloaded char to 0.

#### Retrieving the new filings

This is pretty straightforward--see **download_new_filings**: find new filings where filing_is_downloaded = "0" and download them in a subprocess. Verify that they've downloaded, and if they have, mark that result of filing_is_downloaded = "1". 

For a while FEC's servers were returning an error message with a 200 response, but I think they stopped doing that. (If they do that, that response obviously won't parse). There are times, I think, when large filings won't download because they are being 
processed. Should have some logic about how many times a filing will be attempted before it is marked as being in error (and this should be reflected in the status code).

#### Enter filing 'form line' data

For most forms we care about -- in particular, form F3 and F3X--there's useful summary information in the first line of the .fec file. That means that as soon as the filing is downloaded, we can parse the first line and get the data we need. The script enter_headers_from_new_filers does this by selecting filing objects where filing_is_download=1 and header_is_processed is not "1" or "E" or some other error condition. 

A few minor complications: the .fec forms don't actually include the name of the committee that filed them, so we'd need to hit another table to get the name. The committee master file is updated daily, and usually is helpful. Ever so often, however, the filing will be from a committee that is new (or more likely is a non-committee making IE's). 

We're denormalizing the name of the committee into the filing row. One downside--maybe--is that if the committee subsequently changes its name, the name listed in this filing will be wrong later. 

Finally, some filings are missing important information in their form lines. Form F24 is a good example of this--there are no sums of total spending on the form, just lines for each. So to summarize the form we need to run a summary after all the line itemizations have been created. 

Scripts are: **enter_headers_from_new_filings** which looks for filings that have filing_is_downloaded = "1" and header_is_processed="0". If successful, it sets header_is_processed to "1". This script uses the form parser to get the "form line" data on each filing and saves it into the header_data hstore column. 

The next script is **set_new_filing_details** which sets the basic summary information on each filing by looking in the header. This includes the business logic for doing so. The script looks for filings where header_is_processed="1" and new_filing_details_set="0" and if successful sets new_filing_details_set to "1".

It's possible to combine these two scripts into one, but it's sometimes useful to track when form parsing breaks as opposed to when the business logic of attaching parsed form values to a few summary points is borked. 


