from time import sleep
from albert import *
from geopy import geocoders, Nominatim
from geopy.exc import GeocoderUnavailable
import requests
import json
import os
"""
Shows the weather for the selected city.

The extension shows the main informations about the wheater of the selected city today.
Icon made by:
    Those Icons: https://www.flaticon.com/authors/those-icons from www.flaticon.com
    Pixel perfect: https://www.flaticon.com/authors/pixel-perfect from www.flaticon.com
    Free Pik: https://www.freepik.com" from www.flaticon.com
Synopsis: <trigger> [city]
"""
__doc__     = "Show the weather of the selected city"
__title__   = "weather"
__version__ = "0.1.0"
__triggers__ = "wt "
__authors__  = "elements72, adrianoRieti"
__py_deps__ = "geopy"

informations={}
dirName = os.path.dirname(__file__)
imgPath = dirName + "/images/"

# Initializes the informations used for generating the answers
def initialize():
    global informations
    f = open( dirName + "/data.json", "r")
    informations = json.load(f)
    f.close()

def handleQuery(query):
    if not query.isTriggered:
        return
    city = query.string.strip()
    if not city:
        return makeHelp()
    try:
        data = getData(city, query)
    except GeocoderUnavailable:
        return makeNetworkError()
    if query.isValid:
        return makeAnswer(data)


# Main function to get the weather 
def getData(city, query):
    data = None
    sleep(1)
    if query.isValid:
        geocoder = Nominatim(user_agent="albert-weather")
        location = geocoder.geocode(city, featuretype="city", language="en")
        if location != None:
            url = "http://www.7timer.info/bin/api.pl?lon={0}&lat={1}&lang=it&product=civillight&output=json".format(location.longitude, location.latitude)
            response = requests.get(url)
            data = json.loads(response.text)
            data = {"wtInfo": data["dataseries"][0], "city": location.address}
    return data

# Initial help if no query is provided 
def makeHelp():
    text = "Insert city name"
    subtext = "You may wait for a while..."
    icon = "sun.png"
    actions = []
    return makeItem(text, subtext, icon, actions)

# Function called if a network error occurred 
def makeNetworkError():
    text = "Connection error"
    subtext = "Check your network"
    icon = "error.png"
    actions = []
    return makeItem(text, subtext, icon, actions)

# Provides informations about the selected city 
def makeAnswer(data):
    text = "Nothing found"
    subtext = "Check your question"
    icon = "education.png"
    actions = []
    if data != None:
        wtInfo = data["wtInfo"]
        text = data["city"]
        icon = informations[wtInfo["weather"]]["iconPath"]
        subtext = informations[wtInfo["weather"]]["description"] + ", Max:{}° Min:{}°".format(wtInfo["temp2m"]["max"], wtInfo["temp2m"]["min"])
        actions = [
            UrlAction(text="OpenUrl", url="https://www.google.com/search?q=weather {}".format(text))
        ]
    return makeItem(text, subtext, icon, actions)


# Creates and returns item class object
def makeItem(text, subtext, icon,  actions):
    return [Item(
        id = __title__,
        text = text,
        subtext = subtext,
        icon = imgPath + icon,
        actions = actions
    )]  
