#!/usr/bin/python3

# Python script for feeding magnet links from RSS feed into Real-Debrid

import json
import requests
import feedparser
import argparse
import datetime
import os

# SECTION: VARIABLES
__location__ = os.path.realpath(os.path.join(
    os.getcwd(), os.path.dirname(__file__)))

# Save file information
save_file_name = "RDRSSconfig/rdrss.json"
save_file_path = os.path.join(__location__, save_file_name)

BASE_DATE_STRING = "2000-01-01 00:00:00"

# Variables loaded from file
_auth_token = ""
_data = {}
_headers = {"Authorization": "Bearer " + _auth_token}
# !SECTION


# SECTION: METHODS


def load_data(initialize_if_not: bool) -> bool:
    """Load data from config file into data variable

    @param initialize_if_not Create empty boilerplate data if file didnt exist

    @return bool File does exist
    """
    global _data
    try:
        json_file = open(save_file_path, "r+", encoding="utf-8")
        _data = json.load(json_file)
        json_file.close()
        return True
    except Exception:
        if initialize_if_not:
            _data["rssUrls"] = []
            _data["updated"] = BASE_DATE_STRING
            _data["authToken"] = ""
        return False


def store_data() -> bool:
    """Store data to config file from data variable

    @return bool Storing was successful
    """

    try:
        os.makedirs(os.path.dirname(save_file_path), exist_ok=True)
        json_file = open(save_file_path, "w", encoding="utf-8")
        json.dump(_data, json_file, indent=4)
        json_file.close()
        return True
    except Exception:
        return False


def ready_and_parse():
    """Try to parse RSS urls to Real-Debrid """
    global _data

    # Check for token
    if not (token_check()):
        return

    # Load stored last updated time
    if not load_data(True):
        return
    try:
        last_updated_date = datetime.datetime.strptime(
            str(_data["updated"]), '%Y-%m-%d %H:%M:%S').timetuple()
    except Exception:
        last_updated_date = datetime.datetime.strptime(
            str(BASE_DATE_STRING), '%Y-%m-%d %H:%M:%S').timetuple()

    # Load stored urls
    urls = get_rss()
    if len(urls) < 1:
        print("Missing RSS url. To add RSS url, use --add <value>")
        return

    # For each url print info and fetch to Real-Debrid
    x = 0
    for rss in urls:
        x += 1
        print("(" + str(x) + "/" + str(len(urls)) + ") " + rss)
        parse_feed(rss, last_updated_date)

    # Store now as last update time
    _data["updated"] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    store_data()

    # Select files in Real-Debrid
    select_files()


def parse_feed(rss_url, last_load_date):
    """Parse RSS feed into Real-Debrid

    @param rss_url RSS feed url
    @param last_load_date Last date this feed was updated (when to fetch new entries from)
    """

    feed = feedparser.parse(rss_url)

    # If feed is empty return
    if len(feed.entries) == 0:
        print(". Fetch from RSS failed.")
        return

    # Try to add magnet from each entry that has not yet been added to Real-Debrid
    # based on update time
    for entry in feed.entries:
        if (entry.updated_parsed > last_load_date):
            add_magnet(entry.link)

    print(". Successfully fetched RSS to RD.")


def process_api_response(result) -> bool:
    """Process response codes from Real-Debrid api

    @param result

    @returns bool Response is ok
    """

    if not result.ok:
        if result.status_code == 401:
            print(
                ". Failed reaching RD: Invalid token, to enter authentication token, use --token <value>.")
        elif result.status_code == 402:
            print(". Failed reaching RD: User not premium.")
        elif result.status_code == 503:
            print(". Failed reaching RD: Service not available.")
        else:
            print(". Failed reaching RD.")
        return False
    return True


def add_magnet(magnet) -> bool:
    """Add magnet url into Real-Debrid using API

    @param magnet Url to magnet

    @returns bool Magnet added successfully
    """

    # Add magnet to Real-Debrid and process response
    request_data = {"magnet": magnet, "host": "real-debrid.com"}
    result = requests.post(
        "https://api.real-debrid.com/rest/1.0/torrents/addMagnet", headers=_headers, data=request_data)
    if not process_api_response(result):
        return False

    return True


def select_files() -> bool:
    """Select files added into Real-Debrid using API

    @returns bool Files selected successfully
    """

    # Get files from Real-Debrid
    result = requests.get(
        "https://api.real-debrid.com/rest/1.0/torrents?limit=100", headers=_headers)
    if not process_api_response(result):
        return False

    # Select correct files
    files = result.json()
    for file in files:
        if file["status"] == "waiting_files_selection":
            result = requests.post("https://api.real-debrid.com/rest/1.0/torrents/selectFiles/" +
                                   file["id"], data={"files": "all"}, headers=_headers)
            if not process_api_response(result):
                return False

    return True


def get_rss():
    """  Retrieve stored RSS urls

    @return array of urls
    """

    if load_data(True):
        if ("rssUrls" in _data) and (len(_data["rssUrls"]) != 0):
            return _data["rssUrls"]
    return []


def set_token(token):
    """Store Real-Debrid token

    @param token Real-Debrid user token
    """
    global _data

    # Load data and store token
    load_data(True)
    _data["authToken"] = token

    # Store data
    if not store_data():
        print("Couldn't store token.")
        return
    print("Token succesfully added.")


def token_check() -> bool:
    """Check if Real-Debrid token is stored

    @returns bool If true, token is stored
    """

    global _auth_token
    global _headers

    # Check if token is in loaded data
    if load_data(True):
        if len(_data["authToken"]) != 0:
            _auth_token = _data["authToken"]
            _headers = {"Authorization": "Bearer " + _auth_token}
            return True

    print(
        "Missing Real-Debrid authentication token. To enter auth token, use --token <value>")
    return False


def add_rss(rss):
    """Store RSS url

    param rss Url to RSS feed
    """

    global _data

    # Load data and add new rss
    load_data(True)
    _data["rssUrls"].append(rss)

    # Store data
    if not store_data():
        print("Couldn't store RSS url.")
        return
    print("RSS url succesfully added.")


def list_rss():
    """List stored RSS urls"""

    if load_data(True):
        if ("rssUrls" in _data) and (len(_data["rssUrls"]) != 0):
            print("RSS urls stored:")

            # Loop through urls and print them numbered
            x = 0
            for rss in _data["rssUrls"]:
                x += 1
                print(" [" + str(x) + "] " + rss)
            if (x > 0):
                return

    print("No RSS url added. To add RSS url, use --add <value>")


def remove_rss(n):
    """Remove stored RSS url number n

    @param n Index of url to remove
    """

    global _data

    if not load_data(True):
        print("Configuration file is empty.")

    # Check if url at index exists
    if ("rssUrls" not in _data) or (len(_data["rssUrls"]) < n):
        print("No url at index " + str(n) + " found.")
        return

    # Remove url from data
    _data["rssUrls"].pop(n-1)

    # Store data back into file
    if not store_data():
        print("Couldn't remove RSS url.")
        return
    print("RSS url succesfully removed.")

# !SECTION


# SECTION: ARGUMENT PROCESSING
parser = argparse.ArgumentParser(description='RSS feed to Real-Debrid.')
parser.add_argument('-t', '--token', type=str,
                    help='set Real-Debrid token (acquire token at https://real-debrid.com/apitoken)')
parser.add_argument('-l', '--list',
                    help='list RSS urls', action='store_true')
parser.add_argument('-a', '--add', type=str, help='add RSS url')
parser.add_argument('-r', '--remove', type=int,
                    help='remove RSS url at index (obtained using --list)')
parser.add_argument('-m', '--magnet', type=str,
                    help='add magnet to Real-Debrid')
parser.add_argument('-s', '--select',
                    help='select added files on Real-Debrid', action='store_true')

args = parser.parse_args()
if args.token:
    set_token(args.token)
elif args.list:
    list_rss()
elif args.add:
    add_rss(args.add)
elif args.remove:
    remove_rss(args.remove)
elif args.magnet:
    if token_check():
        add_magnet(args.magnet)
elif args.select:
    if token_check():
        select_files()
else:
    ready_and_parse()
# !SECTION
