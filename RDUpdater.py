import requests
import sys
import getopt

# VARIABLES
authToken = ""

# METHODS
def addToRD(magnet):
    if tokenCheck():
        addMagnet(magnet)

def addMagnet(magnet):
    headers = {"Authorization": "Bearer " + authToken}
    data = {"magnet": magnet, "host": "real-debrid.com"}
    result = requests.post("https://api.real-debrid.com/rest/1.0/torrents/addMagnet", headers = headers, data = data)
    id = result.json()["id"]
    selectData = {"files": "all"}
    selectUrl = "https://api.real-debrid.com/rest/1.0/torrents/selectFiles/" + id
    selectResult = requests.post(selectUrl, headers = headers, data = selectData)
    print("Added magnet to Real-Debrid.")

def newToken(token):
    tokenFile = open("auth.txt","w")
    tokenFile.write(token)
    tokenFile.close()
    print("Token successfully saved")

def displayHelp():
    print("Help")

def tokenCheck():
    tokenFile = open("auth.txt","r+")
    tokenContents = tokenFile.readline()

    if len(tokenContents) > 0:
        global authToken
        authToken = tokenContents
        return True
    else:
        print("Missing Real-Debrid token. To enter authToken, use --token <value>")
        return False

    tokenFile.close()
    
# ARGUMENT PROCESSING

fullCmdArguments = sys.argv
argumentList = fullCmdArguments[1:]
unixOptions = "ht:m:"
gnuOptions = ["help", "token=", "magnet="]

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
    elif currentArgument in ("-t", "--token"):
        newToken(currentValue)
    elif currentArgument in ("-m", "--magnet"):
        addToRD(currentValue)