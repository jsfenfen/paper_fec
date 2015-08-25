### Copying bulk FEC data from FEC

This app exists just to keep a local copy of the FEC's ftp files in synch with the official version. The Committee, Candidate, and Candidate Committee Linkage files are now updated daily. The update procedure here is just to drop and recreate the database tables with raw postgres-flavored sql. There are also bash importers, which do a teensy bit of cleanup.

There's also a table for contributions, but we won't go into that here.

This isn't really essential to the rest of the parsing business going on elsewhere, but you need something like this to keep basic cycle committee details straight. 

### Retrieving the files

To retrieve the cand, com and ccl files edit this file to set a data directory: shellscripts/get_summary_ftp_files.sh. Yes an env variable would be nice here. 

There are a few perl one-liners to clean up crazy character sequences 

Run the script to retrieve the raw files:

	$ source get_summary_ftp_files.sh

### Adding data to the database

Once you've synced / migrated to create the database tables, you should be able to use the sql in sqlscripts/reload_ftp_summarydata_16.sql to load in the summary files. Before you do, edit the file directly to set the datadir (or fix stuff to use the same environment variable) that was used before. 

Assuming you have database credentials, you can load the data with: 

	psql -d [databasename] < sqlscripts/reload_ftp_summarydata_16.sql

or something similar. Note that those files will first completely wipe the three tables before adding the new data from scratch. It's intended that this model is at best loosely tied to the rest of the app--it's really just a data reference. 

### Context

These scripts are intended to run daily so that there's fresh data to support the rest of the app. 