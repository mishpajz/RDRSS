# RDRSS
Python script which takes torrent magnet links from RSS feed and feeds them to your [real-debrid.com](https://real-debrid.com) account.

### Features
- Adds magnet links from any RSS feed to [real-debrid.com](https://real-debrid.com)
- Fetches only new links, will ignore already fetched entries.
- Saves all set up data.

## Getting Started
### Prerequisites
- Python (3)
- pip
- Premium [real-debrid.com](https://real-debrid.com) account

### Install
Install the required packages.
```
pip install -r requirements.txt
``` 

Then download [the latest release](https://github.com/CaptainMishan/RDRSS/releases/latest) and save the python file somewhere accessible.

### Set up
1. Run `RDRSS.py --rss "<url to your feed>"` to specify RSS feed with magnet links (in link tag of RSS feed) that should be added to Real-Debrid.
2. Obtain your [real-debrid api token here](https://real-debrid.com/apitoken)
3. Run `RDRSS.py --token "<your Real-Debrid api token>"` in your shell to save your api token.

The script creates "rdrss.json" save file, which contains:
- stored token ("authToken" field)
- stored RSS url ("rssUrl" field)
- timestamp for last entry that was added to Real-Debrid ("updated" field) 

## Usage
Run `RDRSS.py` to add magnets from new entries in feed to real-debrid.
For help run `RDRSS.py -h`.
It is recommended to run this regularly, for example at startup, using cron job or Automator.

## License
This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file for details

## Contributions
All contributions are most welcome.
