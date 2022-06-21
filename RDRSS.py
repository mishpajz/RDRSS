#!/usr/bin/python3

## Python script for feeding magnet links from RSS feed into Real-Debrid

import json
import requests
import feedparser
import sys
import argparse
import datetime
import time
import os

# SECTION: VARIABLES
__location__ = os.path.realpath(os.path.join(
    os.getcwd(), os.path.dirname(__file__)))

# Save file information
_save_file_name = "rdrss.json"
_save_file_path = os.path.join(__location__, _save_file_name)

_base_date_string = "2000-01-01 00:00:00"

# Variables loaded from file
rss_url = ""
auth_token = ""
# !SECTION


# SECTION: METHODS
## Check if RSS and token is stored and try to parse RSS with magnets into Real-Debrid
#
def ready_and_parse():
    if not (rss_check() and token_check()):
        return
    parse_feed()


## Parse RSS feed into Real-Debrid
#
def parse_feed():
    feed = feedparser.parse(rss_url)

    # If feed is empty
    if len(feed.entries) == 0:
        print("Fetch from RSS failed")
        return

    # Load stored last updated time
    last_updated_date = datetime.datetime.strptime(
        str(_base_date_string), '%Y-%m-%d %H:%M:%S').timetuple()
    data = {}
    try:
        json_file = open(_save_file_path, 'r+')
        data = json.load(json_file)
        json_file.close()
        last_updated_date = datetime.datetime.strptime(
            str(data["updated"]), '%Y-%m-%d %H:%M:%S').timetuple()
    except:
        print("Corrupted save file (try removing " +
              _save_file_name + " file and adding token and RSS again)")
        return

    # For each entry in RSS feed that has not been added to Real-Debrid yet,
    # try to add magnet from each entry like this
    added = False
    for entry in feed.entries:
        if (entry.updated_parsed > last_updated_date):
            if add_magnet(entry.link):
                added = True

    # If some entry has been added into Real-Debrid, try to change
    # last updated date in save file
    if not added:
        return
    last_item = feed.entries[0]
    data["updated"] = time.strftime(
        '%Y-%m-%d %H:%M:%S', last_item.updated_parsed)
    json_file = open(_save_file_path, 'w')
    json.dump(data, g, indent=4)
    json_file.close()
    print("Successfully added RSS to RD")


## Add magnet url into Real-Debrid using API
#
#  @param magnet Url to magnet
#
def add_magnet(magnet):
    # HTML request header
    headers = {"Authorization": "Bearer " + auth_token}

    # Add magnet to Real-Debrid and process response
    data = {"magnet": magnet, "host": "real-debrid.com"}
    result = requests.post(
        "https://api.real-debrid.com/rest/1.0/torrents/addMagnet", headers=headers, data=data)
    if result.status_code != 201:
        if result.status_code == 401:
            print(
                "Failed adding magnet to RD: Invalid token, to enter authentication token, use --token <value>.")
        elif result.status_code == 402:
            print("Failed adding magnet to RD: User not premium.")
        elif result.status_code == 503:
            print("Failed adding magnet to RD: Service not available.")
        else:
            print("Failed adding magnet to RD.")
        return False

    # Try to select file in magnet on Real-Debrid
    try:
        id = result.json()["id"]
        select_data = {"files": "all"}
        select_url = "https://api.real-debrid.com/rest/1.0/torrents/selectFiles/" + id
        requests.post(select_url, headers=headers, data=select_data)
    except:
        print("  Magnet couldn't be activated on Real-Debrid (requires manual activation).")
    print("Added magnet to Real-Debrid.")
    return True


## Store RSS url
#
#  @param rss Url to RSS feed
#
def set_rss(rss):
    data = {}
    # Try loading other data from file, else set default values
    try:
        json_file = open(_save_file_path, 'r+')
        data = json.load(json_file)
        json_file.close()
    except:
        data["authToken"] = ""
        data["updated"] = _base_date_string

    data["rssUrl"] = rss

    # Store data back into file
    try:
        json_file = open(_save_file_path, 'w')
        json.dump(data, json_file, indent=4)
        json_file.close()
    except:
        print("Couldn't store RSS url.")
        return
    print("RSS url succesfully added.")


## Check if RSS url is stored
#
def rss_check():
    global rss_url
    try:
        json_file = open(_save_file_path, 'r+')
        data = json.load(json_file)
        json_file.close()

        if len(data["rssUrl"]) > 0:
            rss_url = data["rssUrl"]
            return True
    except:
        pass

    print(
        "Missing RSS url. To enter RSS url, use --rss <value>")
    return False


## Store Real-Debrid token
#
#  @param token Real-Debrid user token
#
def set_token(token):
    data = {}
    # Try loading other data from file, else set default values
    try:
        json_file = open(_save_file_path, 'r+')
        data = json.load(json_file)
        json_file.close()
    except:
        data["rssUrl"] = ""
        data["updated"] = _base_date_string

    data["authToken"] = token

    # Store data back into file
    try:
        json_file = open(_save_file_path, 'w')
        json.dump(data, json_file, indent=4)
        json_file.close()
    except:
        print("Couln't store token")
        return
    print("Token succesfully added")


## Check if Real-Debrid token is stored
#
def token_check() -> bool:
    global auth_token
    try:
        json_file = open(_save_file_path, 'r+')
        data = json.load(json_file)
        json_file.close()

        if len(data["authToken"]) != 0:
            auth_token = data["authToken"]
            return True
    except:
        pass

    print(
        "Missing Real-Debrid auth token. To enter authentication token, use --token <value>")
    return False
# !SECTION


# SECTION: ARGUMENT PROCESSING
parser = argparse.ArgumentParser(description='RSS feed to Real-Debrid.')
parser.add_argument('-r', '--rss', type=str, help='set RSS url')
parser.add_argument('-t', '--token', type=str,
                    help='set Real-Debrid token (acquire token at https://real-debrid.com/apitoken)')
parser.add_argument('-m', '--magnet', type=str, help='add magnet to Real-Debrid')

args = parser.parse_args()
if args.rss:
    set_rss(args.rss)
elif args.token:
    set_token(args.token)
elif args.magnet:
    if token_check():
        add_magnet(args.magnet)
else:
    ready_and_parse()
# !SECTION