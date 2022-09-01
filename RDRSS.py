#!/usr/bin/python3

# Python script for feeding magnet links from RSS feed into Real-Debrid

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
auth_token = ""
data = {}
# !SECTION


# SECTION: METHODS


#  Load data from config file into data variable
#
#  @param initializeIfNot Create empty boilerplate data if file didnt exist
#
#  @return bool File does exist
def load_data(initializeIfNot: bool) -> bool:
    global data
    try:
        json_file = open(_save_file_path, 'r+')
        data = json.load(json_file)
        json_file.close()
        return True
    except:
        if initializeIfNot:
            data["rssUrls"] = []
            data["updated"] = _base_date_string
            data["authToken"] = ""
        return False

#  Store data to config file from data variable
#
#  @return bool Storing was successful
def store_data() -> bool:
    global data
    try:
        json_file = open(_save_file_path, 'w')
        json.dump(data, json_file, indent=4)
        json_file.close()
        return True
    except:
        return False

#  Try to parse RSS urls to Real-Debrid
def ready_and_parse():
    global data
    
    # Check for token
    if not (token_check()):
        return

    # Load stored last updated time
    last_updated_date = datetime.datetime.strptime(
    str(_base_date_string), '%Y-%m-%d %H:%M:%S').timetuple()
    if not load_data(True):
        return
    try:
        last_updated_date = datetime.datetime.strptime(
            str(data["updated"]), '%Y-%m-%d %H:%M:%S').timetuple()
    except:
        pass

    # Load stored urls
    urls = get_rss()
    if len(urls) < 1:
        print("Missing RSS url. To add RSS url, use --add <value>")
        return

    # For each url print info and fetch to Real-Debrid
    c = 0
    for rss in urls:
        c += 1
        print("(" + str(c) + "/" + str(len(urls)) + ") " + rss)
        parse_feed(rss, last_updated_date)

    # Store now as last update time
    data["updated"] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    store_data()


#  Parse RSS feed into Real-Debrid
#
#  @param rss_url RSS feed url
#  @param last_load_date Last date this feed was updated (when to fetch new entries from)
def parse_feed(rss_url, last_load_date):
    feed = feedparser.parse(rss_url)

    # If feed is empty return
    if len(feed.entries) == 0:
        print("Fetch from RSS failed.")
        return

    # Try to add magnet from each entry that has not yet been added to Real-Debrid
    # based on update time
    for entry in feed.entries:
        if (entry.updated_parsed > last_load_date):
            add_magnet(entry.link)

    print("Successfully fetched RSS to RD.")

#  Add magnet url into Real-Debrid using API
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
                "  Failed adding magnet to RD: Invalid token, to enter authentication token, use --token <value>.")
        elif result.status_code == 402:
            print("  Failed adding magnet to RD: User not premium.")
        elif result.status_code == 503:
            print("  Failed adding magnet to RD: Service not available.")
        else:
            print("  Failed adding magnet to RD.")
        return False

    # Try to select file in magnet on Real-Debrid
    try:
        id = result.json()["id"]
        select_data = {"files": "all"}
        select_url = "https://api.real-debrid.com/rest/1.0/torrents/selectFiles/" + id
        requests.post(select_url, headers=headers, data=select_data)
    except:
        print("  Magnet couldn't be activated on Real-Debrid (requires manual activation).")
    print("  Added magnet to Real-Debrid.")
    return True

#  Retrieve stored RSS urls
#
#  @return array of urls
#
def get_rss():
    global data

    if load_data(True):
        if ("rssUrls" in data) and (len(data["rssUrls"]) != 0):
            return data["rssUrls"]
    return []


#  Store Real-Debrid token
#
#  @param token Real-Debrid user token
#
def set_token(token):
    global data

    # Load data and store token
    load_data(True)
    data["authToken"] = token

    # Store data
    if not store_data():
        print("Couldn't store token.")
        return
    print("Token succesfully added.")


#  Check if Real-Debrid token is stored
#
#  @returns bool If true, token is stored
#
def token_check() -> bool:
    global auth_token
    global data

    # Check if token is in loaded data
    if load_data(True):
        if len(data["authToken"]) != 0:
            auth_token = data["authToken"]
            return True

    print(
        "Missing Real-Debrid authentication token. To enter auth token, use --token <value>")
    return False

#  Store RSS url
#
#  @param rss Url to RSS feed
#
def add_rss(rss):
    global data

    # Load data and add new rss
    load_data(True)
    data["rssUrls"].append(rss)

    # Store data
    if not store_data():
        print("Couldn't store RSS url.")
        return
    print("RSS url succesfully added.")

#  List stored RSS urls
#
def list_rss():
    global data

    if load_data(True):
        if ("rssUrls" in data) and (len(data["rssUrls"]) != 0):
            print("RSS urls stored:")

            # Loop through urls and print them numbered
            c = 0
            for rss in data["rssUrls"]:
                c += 1
                print(" [" + str(c) + "] " + rss)
            if (c > 0):
                return

    print("No RSS url added. To add RSS url, use --add <value>")

#  Remove stored RSS url number n
#
#  @param n Index of url to remove
def remove_rss(n):
    global data

    if not load_data(True):
        print("Configuration file is empty.")

    # Check if url at index exists
    if ("rssUrls" not in data) or (len(data["rssUrls"]) < n):
        print("No url at index " + str(n) + " found.")
        return

    # Remove url from data
    data["rssUrls"].pop(n-1)

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
else:
    ready_and_parse()
# !SECTION
