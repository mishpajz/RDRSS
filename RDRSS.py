#!/usr/bin/python3

import json
import requests
import feedparser
import sys
import argparse
import datetime
import time
import os

# VARIABLES
rss_url = ""
auth_token = ""
_save_file_name = "rdrss.json"
_base_date_string = "2000-01-01 00:00:00"

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

_save_file_path = os.path.join(__location__, _save_file_name)

# METHODS
def ready_and_parse():
    if rss_check():
        parse_feed()

def parse_feed():
    feed = feedparser.parse(rss_url)

    with open(_save_file_path, 'r') as f:
        data = json.load(f)
        if len(feed.entries) == 0:
            print("Fetch from RSS failed")
        else:
            added = True
            if token_check():
                for entry in feed.entries:
                    updated_date = datetime.datetime.strptime(str(data["updated"]), '%Y-%m-%d %H:%M:%S').timetuple()
                    if (entry.updated_parsed >= updated_date):
                        if entry.id != str(data["id"]):
                            if not add_magnet(entry.link):
                                added = False
            else:
                added = False
            if added:
                last_item = feed.entries[0]
                data["updated"] = time.strftime('%Y-%m-%d %H:%M:%S', last_item.updated_parsed)
                data["id"] = last_item.id
                with open(_save_file_path, 'w') as g:
                    json.dump(data, g, indent=4)
                    print("Successfully added RSS to RD")
            else:
                print("Could not add RSS to RD")

def set_rss(rss):
    try:
        json_file = open(_save_file_path, 'r+')
        data = json.load(json_file)
        data["rssUrl"] = rss
        with open(_save_file_path, 'w') as g:
            json.dump(data, g, indent=4)
    except IOError:
        with open(_save_file_path, 'w') as json_file:
            data = {}
            data["rssUrl"] = rss
            data["updated"] = _base_date_string
            data["id"] = ""
            data["authToken"] = ""
            json.dump(data, json_file, indent=4)
    print("RSS url succesfully added")

def rss_check():
    global rss_url
    try:
        json_file = open(_save_file_path, 'r+')
        data = json.load(json_file)
        if len(data["rssUrl"]) > 0:
            rss_url = data["rssUrl"]
            with open(_save_file_path, 'w') as g:
                json.dump(data, g, indent=4)
            return True
        else:
            print("Missing rss url. To enter rssUrl, use --rss <value>")
            return False
    except IOError:
        with open(_save_file_path, 'w') as json_file:
            data = {}
            data["rssUrl"] = ""
            data["updated"] = _base_date_string
            data["id"] = ""
            data["authToken"] = ""
            json.dump(data, json_file, indent=4)
            print("Missing rss url. To enter rssUrl, use --rss <value>")
            return False

def add_magnet(magnet):
    headers = {"Authorization": "Bearer " + auth_token}
    data = {"magnet": magnet, "host": "real-debrid.com"}
    result = requests.post("https://api.real-debrid.com/rest/1.0/torrents/addMagnet", headers = headers, data = data)
    if result.status_code == 400:
        print("Failed adding magnet to RD")
        return False
    elif result.status_code == 401:
        print("Failed adding magnet to RD: Invalid token, to enter authToken, use --token <value>")
        return False
    elif result.status_code == 402:
        print("Failed adding magnet to RD: User not premium")
        return False
    elif result.status_code == 503:
        print("Failed adding magnet to RD: Service not available")
        return False
    else:
        id = result.json()["id"]
        select_data = {"files": "all"}
        select_url = "https://api.real-debrid.com/rest/1.0/torrents/selectFiles/" + id
        select_result = requests.post(select_url, headers = headers, data = select_data)
        print("Added magnet to Real-Debrid.")
        return True

def set_token(token):
    try:
        json_file = open(_save_file_path, 'r+')
        data = json.load(json_file)
        data["authToken"] = token
        with open(_save_file_path, 'w') as g:
            json.dump(data, g, indent=4)
    except IOError:
        with open(_save_file_path, 'w') as json_file:
            data = {}
            data["rssUrl"] = ""
            data["updated"] = _base_date_string
            data["id"] = ""
            data["authToken"] = token
            json.dump(data, json_file, indent=4)
    print("Token succesfully added")

def token_check():
    global auth_token
    try:
        json_file = open(_save_file_path, 'r+')
        data = json.load(json_file)
        if len(data["authToken"]) > 0:
            auth_token = data["authToken"]
            with open(_save_file_path, 'w') as g:
                json.dump(data, g, indent=4)
                return True
        else:
            print("Missing Real-Debrid auth token. To enter authToken, use --token <value>")
            return False
    except IOError:
        with open(_save_file_path, 'w') as json_file:
            data = {}
            data["rssUrl"] = ""
            data["updated"] = _base_date_string
            data["id"] = ""
            data["authToken"] = ""
            json.dump(data, json_file, indent=4)
            print("Missing Real-Debrid auth token. To enter authToken, use --token <value>")
            return False
            
# ARGUMENT PROCESSING
parser = argparse.ArgumentParser(description='RSS feed to Real-Debrid.')
parser.add_argument('-r', '--rss', type=str, help='set rss url')
parser.add_argument('-t', '--token', type=str, help='set RD token url (acquire token at https://real-debrid.com/apitoken)')
parser.add_argument('-m', '--magnet', type=str, help='add magnet to RD')

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
