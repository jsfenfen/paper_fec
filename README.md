# paper_fec
**paper_fec** downloads and parses raw .fec files using a slightly improved version of the [canonical CSV header files](https://github.com/dwillis/fech-sources) maintained by the New York Times.

## Installation
We recommend [virtualenv](https://virtualenv.pypa.io/en/latest/) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/).

```
git clone git@github.com:jsfenfen/paper_fec.git && cd paper_fec
mkvirtualenv paper_fec
add2virtualenv .
pip install -r requirements.txt
```


## Run the demo
This parses all the files in the FILECACHE_DIRECTORY specified in parsing/read_FEC_settings.py. This repo should include at least one file in the default location. 
```
python -m examples.read_FEC_demo
```

## Get more files
This tool includes a utility for downloading old daily filing ZIPs.

```python -m helpers.download_old_fec_filings --help```

To download filings for August 15 - August 19 of 2015, use this command.

```
python -m helpers.download_old_fec_filings --start=20150815 --end=20150820
```

## Todos
* Make the [newly created sources repo](https://github.com/dwillis/fech-sources) a requirement (it is currently included).
