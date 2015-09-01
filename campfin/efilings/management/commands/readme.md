
##Overview

There are several different loading processes that must be run to keep things current.


* Quick .fec file ingestion: New files are collected, information that's available without processing them line by line is set, and older filings that are being replaced are marked as such. Can be run in a cron job every few minutes.

* Processing of line itemizations: Enter the line itemizations from new filings. Since filings can be large, it's recommended that this job be triggered by cron, but processing itself should be queued. Scripts to do this part do not depend on django.

* Set values after line itemization is complete: Some forms do not include totals, so these totals must be set once all line items have been entered.

* Periodic committee and candidate aggregation: Periodically recalculate the total raised and spent by candidates and committees. Candidate totals are based only on authorized committees listed as such in the candidate-committee linkage file; leadership accounts are not included.


* Daily updates: Set candidate, committee and candidate committee linkage files from the FEC's master files, which are updated daily. Data copied directly from the FEC's files lives in FTPData, and is wiped and rewritten onload. Copy the data from this app to the campfin app so that hand-edited changes remain.

## Schedule transformations

The FEC uses slightly different forms to report what are essentially the same transactions. For example, independent expenditures by a corporation are disclosed on a different form than independent expenditures by a party PAC, even though, in the eyes of the law, and the information required, they are basically the same thing. This repo deals with this by intelligently transforming the schedule used in the manner described by [The Sunlight Foundation here](http://realtime.influenceexplorer.com/about/)  (see the "schedule transformation" section). 

Transformed schedules are noticeable in the database because the original linetype is preserved. So an independent expenditure made by a corporation would be reported on a form 5 in a F57 line, but would be reported by this repo in a schedule E line where the "linetype" field is given as "F57".


## Amendments

One important challenge is how to handle amended electronic filings (there is currently no good way no handle amended paper filings). 

Campaign finance rules allow PACs to file an "amended" version of an earlier filing *at any time*. This essentially means that the committees can revise claims they made, years ago, whenever they want. 

Electronic filings make amendments fairly straightforward. For one, the amended version of the original filing must *entirely replace* the initial filing. In this case, the "superseded_by_amendment" flag is set to true on the superseded filing object, and the "amended_by" field is set to the filing number of the filing that replaces it. 

One important wrinkle is slight variations in how the sequence of filings is reported. Imagine a committee files filing 100, and then amends it twice, first in filing 200, and then in filing 300. 

Clearly filing 200 should say that it is amending filing 100, but should filing 300 say that it is amending filing 100 or 200? In the wild, both situations are encountered, so it's important to look for that. Moreover, it's not uncommon for important filings to be amended 3 or 4 times; typically the *biggest* filings need the most amendments, because there are so many details that might need correcting. 

Besides amendments, FEC requires that some contributions and expenses be reported twice: first on a form that's due in 24- or 48- hours, and then again in a committees regular periodic filing (which is generally monthly or quarterly). 

Historically the FEC has required quicker disclosure of larger itemizations toward the end of a campaign, but doesn't hold them to the same standard of accuracy; its common for ad buys to be refunded substantially after the fact due to preempted ads, etc. Therefore, the FEC has not historically included the 24- and 48- hour notices in it's summations of committee activity. 

That's understandable--but probably not desirable in a reporting context. So summation processes in this repo *do* count these quick turnaround forms in sums, when applicable, though often they are represented separately to reflect different filing requirements. 

For example, during the final 20 days of an election, a candidate pac must report all contributions of $1,000 or more within 48 hours. Note how fundamentally poorly-though out this is; to circumvent this particular disclosure, one could simply write two checks for $500. And yet, even though FEC has records of these reports (albeit on paper for senate candidates), they aren't counted towards the contribution totals. 

This repo treats 24 hour notice forms as being amended when the periodic filing is received. There's one crucial difference though: instead of marking the *filing* as being superseded, each line item is marked as being superceded. (The same is true for 48-hour notice contributions). That's because there's no guarantee that the timerange covered by a 24- or 48-hour form will be entirely covered by a single periodic report. For instance, a single report of independent expenditures might cover the last day of one month and the first of another. A monthly filer would then report some of those transactions on two different months' reports. After the first months report was filed (but before the second) a correct summation requires that only some of the expenditures be counted *in addition to* the amounts disclosed on the monthly filings. 

The general rule for line itemizations is to not count them towards totals if **either**  the filng they appear on, or the itemization itself is marked as superseded by an amendment.
 


## Bulk loading vs realtime operation

The same breakdown of processing tasks can be used to load filings in real time, or in bulk, with a few crucial differences. Loading historic data relies on it being downloaded from the FEC's daily zipfiles (as opposed to file-by-file), and the filing numbers must be entered into the database as if they were retrieved file-by-file. See more below. 


##Processing steps

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

Relevant scripts: **scrape_rss_filings** hits the rss feed; **find_new_filings** looks for filings based on the highest available fiiling number. Note that it's possible for find_filings to *miss* filings if they land out of order (this seems to not really happen), so it's important to keep running the rss script, which will catch anything that was missed. You could rely exclusively on the feed, it's just up to 5 minutes out of date. I haven't run find_filings more than once every few minutes, but it should be fine to run once a minute or so. 

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


**mark_amended** finds previous filings that are superceded by new filings and marks them as amended. It also looks for other, earlier filings that amend the same filing (as the new filing amends)--which is how these things sometimes are reported. It runs on filings where previous_amendments_processed="0" and new_filing_details_set="1"; it sets previous_amendments_processed to "1" when it's done. Note that this doesn't mark the line items attached to each filing as having been amended--that takes place in a subsequent script. 


### Processing of line itemizations

It's probably useful to queue the line itemization entry process. An example of the line entry is given in examples/read_and_transform_FEC_demo.py. This part of the script should act on filings where data_is_processed is "0" and set it to "1" upon completion. 


There's a managementment command called **send_body_row_jobs** that will enter all of the needed itemizations from within django. It's useful for entering archived data, and is slightly more efficient because it doesn't need to create new form parsers for every filing. 



### Set values after line itemization is complete

**mark_superseded_body_rows** Marks the body rows that are superseded by certain filings, and set totals on filings 
that can only be computed after all body rows are entered. 

Specifically, summarizes F24, F5 and F6 and marks as superseded F24, F57 and F65. 

Acts on Filing objects with: previous_amendments_processed="1", header_is_processed="1", 
data_is_processed="1", body_rows_superseded="0" and sets body_rows_superseded to "1" on 
completion.


**update_dirty_committees** Set the basic sums for committees. Sets the committee_sum_update_time on each committee. This can also be run on all committees (after doing a bulk load) with **update_all_committees**


**update_dirty_candidates** Not implemented. Should be trivial, but need to hit candcomlink table in FTPData first. 

**process_skede_lines** One of the significant challenges is that independent expenditures (made by outside groups) to support or oppose candidates often leave off the candidate ID, or get it wrong, or mix up a variety of information. Fixing this is not part of this process. For a fuzzy matching approach, see [here](https://github.com/sunlightlabs/read_FEC/tree/master/fecreader/reconciliation). 

## Importing an entire cycle at once

The process of importing an entire cycle's worth of data is similar to uploading the most recent filings, although there are a few differences. 

First download and import the candidate, committee and candcomlink files to the ftpdata app as detailed [here](https://github.com/jsfenfen/paper_fec/tree/master/campfin/ftpdata).

Next import an entire cycle of filings. From the paper_fec directory run:

```
python -m helpers.download_old_fec_filings
```
With no arguments this will attempt do download and unzip every filing received this cycle (through yesterday). 

From the campfin directory run the command make_files_from_archive, i.e., 

```
python manage.py make_files_from_archive
```

Then run these commands, in order, waiting for each one to finish before running the next:

- download_new_filings (this checks whether the file is available for downloading, and after finding it, will just mark it as having been downloaded)
- enter_headers_from_new_filings
- set_new_filing_details
- mark_amended
- send_body_row_jobs (This may take a while)
- mark_superseded_body_rows
- update_all_committees
- update_all_candidates

## Regular operation once the archive has been imported

Daily cron: The candidate, committee and candidate-committee linkage files should downloaded and imported daily to keep these files up-to-date (see link above). As currently written, these simply add new files--this approach will miss changes to committee details, like name changes. 

Cron 1: get filings from the FEC's rss feed, updated every 5 minutes (so run it about every 5 minutes)

- scrape_rss_filings
- download_new_filings
- enter_headers_from_new_filings
- set_new_filing_details
- mark_amended
- [ if queued: send_body_row_jobs ]

Cron 2: Find filings, whether or not they are on the feed. Could run this every minute or so--though skip the minute when the rss feed is being hit. 

- find_new_filings
- download_new_filings
- enter_headers_from_new_filings
- set_new_filing_details
- mark_amended
- [ if queued: send_body_row_jobs ]

The send_body_row_jobs command is intended to not actually enter the line itemizations (aka the body rows) but just queue them for another process to handle. This is by far the most time consuming step, so trying to run via cron can be a problem. 

Cron 3: Process data that assumes line itemizations are complete. Every 5 minutes or so? 

- mark_superseded_body_rows
- update_dirty_committees
- update_dirty_candidates

Note that in this version, it's only the 'dirty' committees and candidates that are updated. The dirty flag is set when new filings are added to a committee or candidate. This part hasn't been tested much. 











 
