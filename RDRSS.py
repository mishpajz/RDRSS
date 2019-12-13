import json
import feedparser
import sys
import getopt
import time
import RDUpdater

# VARIABLES
rssUrl = ""

# METHODS
def readyAndParse():
    if rssCheck():
        parse()

def parse():
    feed = feedparser.parse(rssUrl)

    with open('rss.json', 'r') as f:
        data = json.load(f)
        for entry in feed.entries:
            if time.strftime('%Y-%m-%d %H:%M:%S', entry.updated_parsed) >= str(data["updated"]):
                if entry.id != str(data["id"]):
                    RDUpdater.addToRD(entry.link)
        print("Added your updated feed to Real-Debrid.")
        lastItem = feed.entries[0]
        data["updated"] = time.strftime('%Y-%m-%d %H:%M:%S', lastItem.updated_parsed)
        data["id"] = lastItem.id
        with open('rss.json', 'w') as g:
            json.dump(data, g, indent=4)

def setRSS(rss):
    with open('rss.json', 'w') as f:
        data = json.load(f)
        data["rssUrl"] = rss
        data["updated"] = "0000-00-00 00:00:00"
        data["id"] = ""
        with open('rss.json', 'w') as g:
            json.dump(data, g, indent=4)
            print("RSS url successfully saved")

def displayHelp():
    print("Help")

def rssCheck():
    with open('rss.json', 'r') as jsonFile:
        data = json.load(jsonFile)
        if len(data["rssUrl"]) > 0:
            global rssUrl
            rssUrl = data["rssUrl"]
            if data["updated"] == "":
                data["updated"] = "0000-00-00 00:00:00"
                with open('rss.json', 'w') as g:
                    json.dump(data, g, indent=4)
            return True
        else:
            print("Missing rss url. To enter rssUrl, use --rss <value>")
            return False
        
# ARGUMENT PROCESSING

fullCmdArguments = sys.argv
argumentList = fullCmdArguments[1:]
unixOptions = "hr:"
gnuOptions = ["help", "rss="]

try:
    arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))
    sys.exit(2)

for currentArgument, currentValue in arguments:
    if currentArgument in ("-h", "--help"):
        displayHelp()
        tokenCheck()
    elif currentArgument in ("-r", "--rss"):
        setRSS(currentValue)
readyAndParse()