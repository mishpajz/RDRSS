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
Run 
```
pip3 install requests
pip3 install feedparser
pip3 install argparse
``` 
in your shell. 
Then download [the latest release](https://github.com/CaptainMishan/RDRSS/releases/latest) and save the python file somewhere accessible.

### Set up
1. Run `RDRSS.py --rss "<url to your feed>"` in your shell to specify feed with magnet links that should be added to real-debrid.
2. Obtain your [real-debrid api token here](https://real-debrid.com/apitoken)
3. Run `RDRSS.py --token "<your real-debrid api token>"` in your shell to save your api token.

## Usage
Run `RDRSS.py` in your shell to add magnets from new entries in feed to real-debrid.
I recommend running this regularly, for example at startup, using Automator or using cron job.

## License
This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file for details

## Contributions
All contributions are most welcome.
