# -*- coding: utf-8 -*-

"""Open man page in Yelp.

This extension provides a single item which opens yelp with man page of 'command'

Synopsis: <trigger> <command>"""

from shutil import which
from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Graphical man"
__version__ = "1.0"
__trigger__ = "man "
__author__ = "Juan Simón"
__dependencies__ = ["yelp"]
iconPath = iconLookup("help-browser")

for dep in __dependencies__:
	if not which(dep):
		raise Exception("'%s' is not in $PATH." % dep)
		
def handleQuery(query):
	if query.isTriggered:
		return Item(
			id=__prettyname__,
			icon=iconPath,
			text=__prettyname__,
			subtext="Showing man page in Yelp of '%s'" % query.string,
			completion=query.rawString,
			actions=[
				ProcAction("Showing man page in Yelp of '%s'" % query.string, ['yelp','man:'+query.string])
			]
		)
