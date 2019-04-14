# -*- coding: utf-8 -*-

"""Get Google suggestions"""
from albertv0 import *
from locale import getlocale
from urllib import request, parse
import xml.etree.ElementTree as etree
import os

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Google Suggest"
__version__ = "0.1"
__trigger__ = "g "
__author__ = "Hans C. Jørgensen"
__dependencies__ = []

iconPath = iconLookup('google_suggest')
if not iconPath:
    iconPath = os.path.dirname(__file__)+"/google_suggest.svg"
google_search_baseurl = 'http://www.google.com/search'
google_suggest_baseurl = 'http://google.com/complete/search'
user_agent = "Mozilla/5.0"
limit = 20


def initialize():
    global baseurl

def handleQuery(query):
    if query.isTriggered:

        stripped = query.string.strip()

        if stripped:
            results = []

            google_suggest_params = {
                'output': 'toolbar',
                'q': stripped,
            }
            get_url = "%s?%s" % (google_suggest_baseurl, parse.urlencode(google_suggest_params))
            req = request.Request(get_url, headers={'User-Agent': user_agent})

            with request.urlopen(req) as response:

                if response.msg != 'OK' :
                    return [Item(id=__prettyname__,
                        icon=iconPath,
                        text=__prettyname__,
                        subtext="Something went wrong with the query",
                        completion=query.rawString)]
                else :
                    suggestions = etree.fromstring(response.read().decode('utf-8'))

                    for suggestion in suggestions :

                        suggestion_data = suggestion[0].get('data')

                        google_search_params = {
                            'q': suggestion_data
                        }

                        suggestion_url = "%s?%s" % (google_search_baseurl, parse.urlencode(google_search_params))
                        suggestion_description = 'Search for \'{0}\' on Google'.format(suggestion_data)

                        results.append(Item(id=__prettyname__,
                                            icon=iconPath,
                                            text=suggestion_data,
                                            subtext=suggestion_description,
                                            completion=suggestion_data,
                                            actions=[UrlAction(suggestion_description, suggestion_url)]))

                suggestion_url = "%s?%s" % (google_search_baseurl, parse.urlencode({'q': stripped}))

                results.append(Item(id=__prettyname__,
                                    icon=iconPath,
                                    text=stripped,
                                    subtext='Search for \'{0}\' on Google'.format(stripped),
                                    completion=stripped,
                                    actions=[UrlAction('Search for \'{0}\' on Google'.format(stripped), suggestion_url)]))

                return results
        else:
            return [Item(id=__prettyname__,
                         icon=iconPath,
                         text=__prettyname__,
                         subtext="Enter a query for Google Suggest",
                         completion=query.rawString)]