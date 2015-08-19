# [JACOB I WOULD LIKE THINGS LIKE THIS TO BE IN THE ENV, I THINK?]
# [STILL MAKING UP MY MIND ABOUT IT.]
CYCLE = '2016'

# FEC daily bulk ZIP files URL. Requires the filing ID to be interpolated.
FEC_FILE_LOCATION = "ftp://ftp.fec.gov/FEC/electronic/%s.zip"

# FEC raw .fec files URL. Requires the filing ID to be interpolated.
FEC_DOWNLOAD = "http://docquery.fec.gov/dcdev/posted/%s.fec"

# [JACOB WHAT ARE THESE INTERPOLATIONS?]
FEC_HTML_LOCATION = "http://docquery.fec.gov/cgi-bin/dcdev/forms/%s/%s/"

# Requires the candidate ID to be interpolated.
FEC_CANDIDATE_SUMMARY = "http://www.fec.gov/fecviewer/CommitteeDetailCurrentSummary.do?tabIndex=1&candidateCommitteeId=%s&electionYr=2014"

# How should our requests be signed? 
USER_AGENT = "FEC READER 0.1; [ YOUR CONTACT INFO HERE ]"

# The FEC is known to block scrapers that do not have a delay.
# 2 is sufficient to avoid this.
DELAY_TIME=2

LOG_NAME = 'fecparsing.log'

# Load any system-specific settings from the FEC_local_settings.py.
try:
    from FEC_local_settings import *
except Exception, e:
    print "Exception in local settings: %s" % (e)
    pass
