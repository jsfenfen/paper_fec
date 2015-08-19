paper_fec
=========

Parse the raw .FEC files using (a slightly improved version of) the NYT's csv sources files. Todo: make the [newly created sources repo](https://github.com/dwillis/fech-sources) a requirement (it is currently included).


Installation
========
Clone this repo with: 
` git clone git@github.com:jsfenfen/paper_fec.git`

Change directories into the newly created paper_fec directory. Install the requirements, preferably into a virtualenv, with  `pip install -r requirements.txt`

Copy the local settings example file into place with `cp parsing/local_FEC_settings.py-example parsing/local_FEC_settings.py`. This file sets the location of a number of directories used in retrieving and unzipping archived .fec files, and you can change the location of these, but just copying the example should work for the moment.

Still in the paper_fec directory, run the demo with `python -m examples.read_FEC_demo`. That should parse a single .fec file and add the keys defined in the sources directory. 

Getting more files
=====

The demo worked on a single .fec file. There's a utility for retrieving many .fec files from the zipped archive that FEC maintains. You can see its usage with: `python -m helpers.download_old_fec_filings --help`
	
	usage: download_old_fec_filings.py [-h] [--start START] [--end END]
	
	optional arguments:
	  -h, --help            show this help message and exit
	  --start START, -s START
	                        Set a start date of the time range to download;
	                        YYYYMMDD format is supported
	  --end END, -e END     Set an end date of the time range to download;
	                        YYYYMMDD format is supported

With no arguments the default behaviour is to download all the zipped fec files (to the ZIP_DIRECTORY specified in parsing.FEC_local_settings and unzips them to FILECACHE_DIRECTORY).


