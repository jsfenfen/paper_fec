# paper_fec

Parses the raw .FEC files using (a slightly improved version of) the NYT's csv sources files.

## Installation
We recommend virtualenv and virtualenvwrapper.

```
git clone git@github.com:jsfenfen/paper_fec.git && cd paper_fec
mkvirtualenv paper_fec
add2virtualenv .
pip install -r requirements.txt
cp parsing/local_FEC_settings.py-example parsing/local_FEC_settings.py
```

## Run the demo
```
python -m examples.read_FEC_demo
```

## Get more files
This tool includes a utility for downloading old daily filing ZIPs.

```python -m helpers.download_old_fec_filings --help```

To download filings for August 15 - August 19 of 2015, use this command.

```
python -m helpers.download_old_fec_filings --start=20150815 --end=20150819
```

## Todos
* Make the [newly created sources repo](https://github.com/dwillis/fech-sources) a requirement (it is currently included).
* Extend `read_FEC_demo` to read anything in the unzipped sources folder, maybe?