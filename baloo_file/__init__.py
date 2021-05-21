# -*- coding: utf-8 -*-

"""Search KDE's Baloo File Indexer.

Synopsis: <trigger> <searchquery>

Many thanks to https://github.com/briceio who helped make this possible!
I've seen that a module like this was requested on Github and cause I myself
am using KDE's builtin indexer I thought why not give it a try.
With that said don't expect the cleanest Python code since I am by no means a pro at it!"""

from albert import *
from subprocess import check_output
from xdg import Mime
import os.path

__title__ = "Baloo File"
__version__ = "0.4.0"
__triggers__ = "? "
__authors__ = "XanderCode"
__exec_deps__ = ["baloosearch","xdg-open"]
__py_deps__ = "pyxdg"

icon_path = os.path.dirname(__file__) + "/baloo.svg"

### user defined settings ###
icon_theme_path = "/usr/share/icons/breeze/mimetypes/64"

############################################################################################

# Not needed
def initialize():
    pass


# Not needed
def finalize():
    pass


def handleQuery(query):
    if query.isTriggered:
        query.disableSort()
    
        strip_query = query.string.strip()
        
        if strip_query:
            items = []
            
            if '#' in strip_query: 
                # prepare query for tags
                strip_query = strip_query.replace("#f",     "type:Folder")
                strip_query = strip_query.replace("#img",   "type:Image")
                strip_query = strip_query.replace("#doc",   "type:Document")
                strip_query = strip_query.replace("#txt",   "type:Text")
                strip_query = strip_query.replace("#audio", "type:Audio")
                strip_query = strip_query.replace("#z",     "type:Archive")
                strip_query = strip_query.replace("#video", "type:Video")
                strip_query = strip_query.replace("#pres",  "type:Presentation")
                strip_query = strip_query.replace("#ss",    "type:Spreadsheet")
            
            # search
            out = check_output(["baloosearch", strip_query])
            results = out.splitlines()
            
            # remove duplicates
            lines = list(dict.fromkeys(results))
            
            for line in lines:
                
                # extract path
                path = line.decode("UTF-8")
                
                # properties
                name = os.path.basename(path)
                mime = Mime.get_type2(path)
                
                # icon
                query_icon_path = "%s/%s.svg" % (icon_theme_path, str(mime).replace("/", "-"))
                query_icon = query_icon_path if os.path.exists(query_icon_path) else icon_path
                
                # items
                item_name = name.replace("&", "&amp;")
                item_description = path.replace("&", "&amp;")
            
                # add item to searchresult list
                items.append(Item(  id=__title__,
                                    icon=query_icon,
                                    text=item_name,
                                    subtext=item_description,
                                    actions=[
                                        TermAction(text="Open File", 
                                                   script="xdg-open '%s'" % path, 
                                                   behavior=TermAction.CloseBehavior.CloseOnSuccess),
                                        
                                        TermAction(text="Open Dir", 
                                                   script="dbus-send --session --print-reply --dest=org.freedesktop.FileManager1 --type=method_call /org/freedesktop/FileManager1 org.freedesktop.FileManager1.ShowItems array:string:'" + path + "' string:''", 
                                                   behavior=TermAction.CloseBehavior.CloseOnSuccess),
                                        
                                        ClipAction("Copy Path", path)
                                    ]))
            
            # return searchresults to albert
            if items:
                return items
            
            else:
                return Item(id=__title__,
                            icon=icon_path,
                            text="Search '%s'" % query.string,
                            subtext="No results. Check if baloo indexer is configured correctly",
                            actions=[UrlAction("Baloo Indexer Documentation", "https://community.kde.org/Baloo")])
            
        else:
            return Item(id=__title__,
                        icon=icon_path,
                        text=__title__,
                        subtext="Enter a query to search for files with baloosearch")