
"""This extension allows you to search for songs, albums and artists in your mpd (music player daemon, https://musicpd.org) \
library and add them to the queue and/or play them directly. Currently it's not possible to send other commands to mpd or search via filenames."""

import os
from albertv0 import *
from mpd import MPDClient


__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Music Player Daemon"
__version__ = "1.0"
__trigger__ = "mpd "
__author__ = "Markus Richter"
__dependencies__ = []

SERVER = "localhost"
PORT = 6600

# All included icons are part of the papirus icon theme by the Papirus Development Team and are licensed under the GPLv3.
# Link: https://github.com/PapirusDevelopmentTeam/papirus-icon-theme/ 

# Work which could still be done:
#   - mpd commands (e.g. play/pause, stop, repeat, random, skip, etcpp)
#   - search by path/path-completion
#   - more ways to start/add a song
#   - search playlists

def handleQuery(query):

    if query.isTriggered:# and len(query.string)>1:
        # set icons:
        song_icon=iconLookup("audio-x-generic") or os.path.join(os.path.dirname(__file__),"Papirus-Team-Papirus-Mimetypes-Audio-x-flac.svg")
        album_icon=iconLookup("music-album-default") or os.path.join(os.path.dirname(__file__),"folder-green-music.svg")
        artist_icon=iconLookup("music-artist-default") or os.path.join(os.path.dirname(__file__),"folder-green-image-people.svg")
        
        mpclient = MPDClient()
        mpclient.timeout = 10
        mpclient.connect(SERVER,PORT)
        artistmatches = mpclient.search("artist",query.string)
        albummatches = mpclient.search("album",query.string)
        titlematches = mpclient.search("title",query.string)
	
        # out: the outputted list of suggestions
        out = []
        if len(artistmatches)>0:
            artistalb = dict()
            for a in artistmatches:
                if a['artist'] not in artistalb:
                    artistalb[a['artist']] = set()
                if 'album' in a:
                    artistalb[a['artist']].add(a['album'])
            for i1,artist in enumerate(artistalb.keys()):
                out.append(Item(
                    id=" 1%05d" % (i1),
                    icon=artist_icon,
                    text="%s" % artist,
                    subtext="Matching artist. Press [alt] for more options.",
                    completion=__trigger__ + artist,
                    actions=[
                        FuncAction("Add all to end", lambda id=artist: addMultipleEnd(id,"artist")),
                        FuncAction("Play all and replace", lambda id=artist: addMultipleReplace(id,"artist")),
                        FuncAction("Play all next", lambda id=artist: addMultipleNext(id,"artist")),
                        FuncAction("Play all now", lambda id=artist: addMultipleNow(id,"artist"))
                    ]
                ))
                albs = artistalb[artist]
                out.extend([Item(
                    id=" 1%05d-%05d" % (i1,i2),
                    icon=album_icon,
                    text="·   %s" % a,
                    subtext="Album of matching artist. Press [alt] for more options.",
                    completion=__trigger__ + a,
                    actions=[
                        FuncAction("Add all to end", lambda id=a: addMultipleEnd(id)),
                        FuncAction("Play all and replace", lambda id=a: addMultipleReplace(id)),
                        FuncAction("Play all next", lambda id=a: addMultipleNext(id)),
                        FuncAction("Play all now", lambda id=a: addMultipleNow(id))
                    ]
                ) for i2, a in enumerate(albs)])

        if len(albummatches)>0:
            alb = set()
            for a in albummatches:
                alb.add((a['artist'],a['album']))
            out.extend([Item(
                id=" 3%05d" % i,
                icon=album_icon,
                text="%s - %s" % a,
                subtext="Matching album title. Press [alt] for more options.",
                completion=__trigger__ + a[1],
                actions=[
                    FuncAction("Add all to end", lambda id=a[1]: addMultipleEnd(id)),
                    FuncAction("Play all and replace", lambda id=a[1]: addMultipleReplace(id)),
                    FuncAction("Play all next", lambda id=a[1]: addMultipleNext(id)),
                    FuncAction("Play all now", lambda id=a[1]: addMultipleNow(id))
                ]
            ) for i, a in enumerate(alb)])
        if len(titlematches)>0:
            out.extend([Item(
            id=" 5%05d" % i,
            icon=song_icon,
            text="%s - %s" % (song["artist"],song["title"]),
            subtext=song["file"],
            completion=__trigger__ + song["title"],
            actions=[
                FuncAction("Add to end", lambda file=song["file"]:addSongEnd(file)),
                FuncAction("Play and replace",lambda file=song["file"]:addSongReplace(file)),
                FuncAction("Play next",lambda file=song["file"]:addSongNext(file)),
                FuncAction("Play now",lambda file=song["file"]:addSongNow(file))
            ]
        ) for i,song in enumerate(titlematches)])
        mpclient.close()
        mpclient.disconnect()
        return out


def addSongEnd(file):
    cl = MPDClient()
    cl.connect(SERVER,PORT)
    cl.add(file)
    if cl.status()["playlistlength"]==1:
        cl.play()
    cl.close()
    cl.disconnect()

def addSongNext(file):
    cl = MPDClient()
    cl.connect(SERVER, PORT)
    stat=cl.status()
    pos = 0
    print(stat)
    if "song" in stat:
        pos=int(stat["song"])+1
    print("POS == " + str(pos))
    cl.addid(file,pos)
    if stat["state"] =="stop":
        cl.play(pos)
    cl.close()
    cl.disconnect()

def addSongNow(file):
    cl = MPDClient()
    cl.connect(SERVER, PORT)
    stat=cl.status()
    pos=0
    if "song" in stat:
        #currently playing
        pos = stat["song"]
    cl.addid(file,pos)
    cl.play(pos)
    cl.close()
    cl.disconnect()

def addSongReplace(file):
    cl = MPDClient()
    cl.connect(SERVER, PORT)
    cl.clear()
    cl.add(file)
    cl.play()
    cl.close()
    cl.disconnect()

def addMultipleEnd(id,type="album"):
    cl = MPDClient()
    cl.connect(SERVER,PORT)
    l = cl.status()["playlistlength"]
    cl.findadd(type,id)
    if l==0:
        cl.play()
    cl.close()
    cl.disconnect()

def addMultipleNext(id,type="album"):
    cl = MPDClient()
    cl.connect(SERVER, PORT)
    # get position
    stat=cl.status()
    pos = 0
    print(stat)
    if "song" in stat:
        pos=int(stat["song"])+1
    print("POS == " + str(pos))

    # get songs
    ssongs = cl.find(type,id)
    #ssongs = sorted(songs,key=lambda e: e["track"])
    print(ssongs)
    for i,s in enumerate(ssongs):
        cl.addid(s["file"],pos+i)

    if stat["state"] =="stop":
        cl.play(pos)
    cl.close()
    cl.disconnect()

def addMultipleNow(id,type="album"):
    cl = MPDClient()
    cl.connect(SERVER, PORT)

    # get position
    stat=cl.status()
    pos=0
    if "song" in stat:
        #currently playing
        pos = stat["song"]

    # get songs
    songs = cl.find(type,id)
    ssongs = sorted(songs,key=lambda e: e["track"])
    print(ssongs)
    for i,s in enumerate(ssongs):
        cl.addid(s["file"],pos+i)
    cl.play(pos)
    cl.close()
    cl.disconnect()

def addMultipleReplace(id,type="album"):
    cl = MPDClient()
    cl.connect(SERVER, PORT)
    cl.clear()
    cl.findadd(type,id)
    cl.play()
    cl.close()
    cl.disconnect()
