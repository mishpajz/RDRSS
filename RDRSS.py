import json
import requests
import feedparser
import sys
import argparse
import datetime
import time

# VARIABLES
rssUrl = ""
_baseDateString = "2000-01-01 00:00:00"
authToken = ""

# METHODS
def readyAndParse():
    if rssCheck():
        parseFeed()

def parseFeed():
    feed = feedparser.parse(rssUrl)

    with open('rss.json', 'r') as f:
        data = json.load(f)
        if len(feed.entries) == 0:
            print("Fetch from RSS failed")
        else:
            added = True
            if tokenCheck:
                for entry in feed.entries:
                    updatedDate = datetime.datetime.strptime(str(data["updated"]), '%Y-%m-%d %H:%M:%S').timetuple()
                    if (entry.updated_parsed >= updatedDate):
                        if entry.id != str(data["id"]):
                            if not addMagnet(entry.link):
                                added = False
            else:
                added = False
            if added:
                lastItem = feed.entries[0]
                data["updated"] = time.strftime('%Y-%m-%d %H:%M:%S', lastItem.updated_parsed)
                data["id"] = lastItem.id
                with open('rss.json', 'w') as g:
                    json.dump(data, g, indent=4)
                    print("Successfully added RSS to RD")
            else:
                print("Could not add RSS to RD")

def setRSS(rss):
    try:
        jsonFile = open('rss.json', 'r+')
        data = json.load(jsonFile)
        data["rssUrl"] = rss
        with open('rss.json', 'w') as g:
            json.dump(data, g, indent=4)
    except IOError:
        with open('rss.json', 'w') as jsonFile:
            data = {}
            data["rssUrl"] = rss
            data["updated"] = _baseDateString
            data["id"] = ""
            data["authToken"] = ""
            json.dump(data, jsonFile, indent=4)
    print("RSS url succesfully added")

def rssCheck():
    try:
        jsonFile = open('rss.json', 'r+')
        data = json.load(jsonFile)
        if len(data["rssUrl"]) > 0:
            global rssUrl
            rssUrl = data["rssUrl"]
            with open('rss.json', 'w') as g:
                json.dump(data, g, indent=4)
            return True
        else:
            print("Missing rss url. To enter rssUrl, use --rss <value>")
            return False
    except IOError:
        with open('rss.json', 'w') as jsonFile:
            data = {}
            data["rssUrl"] = ""
            data["updated"] = _baseDateString
            data["id"] = ""
            data["authToken"] = ""
            json.dump(data, jsonFile, indent=4)
            print("Missing rss url. To enter rssUrl, use --rss <value>")
            return False

def addMagnet(magnet):
    headers = {"Authorization": "Bearer " + authToken}
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
        selectData = {"files": "all"}
        selectUrl = "https://api.real-debrid.com/rest/1.0/torrents/selectFiles/" + id
        selectResult = requests.post(selectUrl, headers = headers, data = selectData)
        print("Added magnet to Real-Debrid.")
        return True

def setToken(token):
    try:
        jsonFile = open('rss.json', 'r+')
        data = json.load(jsonFile)
        data["authToken"] = token
        with open('rss.json', 'w') as g:
            json.dump(data, g, indent=4)
    except IOError:
        with open('rss.json', 'w') as jsonFile:
            data = {}
            data["rssUrl"] = ""
            data["updated"] = _baseDateString
            data["id"] = ""
            data["authToken"] = token
            json.dump(data, jsonFile, indent=4)
    print("Token succesfully added")

def tokenCheck():
    try:
        jsonFile = open('rss.json', 'r+')
        data = json.load(jsonFile)
        if len(data["authToken"]) > 0:
            global authToken
            authToken = data["authToken"]
            with open('rss.json', 'w') as g:
                json.dump(data, g, indent=4)
                return True
        else:
            print("Missing Real-Debrid auth token. To enter authToken, use --token <value>")
            return False
    except IOError:
        with open('rss.json', 'w') as jsonFile:
            data = {}
            data["rssUrl"] = ""
            data["updated"] = _baseDateString
            data["id"] = ""
            data["authToken"] = ""
            json.dump(data, jsonFile, indent=4)
            print("Missing Real-Debrid auth token. To enter authToken, use --token <value>")
            return False
            
# ARGUMENT PROCESSING
parser = argparse.ArgumentParser(description='RSS feed to Real-Debrid.')
parser.add_argument('-r', '--rss', type=str, help='set rss url')
parser.add_argument('-t', '--token', type=str, help='set RD token url (acquire token at https://real-debrid.com/apitoken)')
parser.add_argument('-m', '--magnet', type=str, help='add magnet to RD')

args = parser.parse_args()
if args.rss:
    setRSS(args.rss)
elif args.token:
    setToken(args.token)
elif args.magnet:
    addToRD(args.magnet)
else:
    readyAndParse()
