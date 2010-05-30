#!/usr/bin/env python

############################################################################################
#  User Settings:                                                                          #
#    maxPKGS = Maximum Number of Packages to show                                          #
#    maxNEWS = Maxium Number of News Items to show                                         #
#    SERVER  = The server that you'll be running  the script through. Some servers         #
#               such as apache require webpy to explictly to tell it to run the script as  #
#               fastcgi app. Possible values are: lighttpd, apache, webpy                  #
#                                                                                          #
############################################################################################

maxPKGS=6
maxNEWS=4
SERVER='webpy'

################################### END OF USER SETTINGS ###################################

import web

import feedparser
import feedcache

import sys
import shelve

import os.path
import datetime

from arch import Arch

urls = (
  '/', 'index'
)

web.config.debug = True

render = web.template.render('templates')

app = web.application(urls, globals())
web.template.Template.globals['render'] = render

#Downloads RSS for news feed items
def getFeeds():

    #Time until cached feeds expire
    timeToLiveSeconds=3600   #60 Minutes

    #Stores file as .nfeed_cache in CWD
    newsPath = shelve.open('./cache/news_cache')
    i686Path = shelve.open('./cache/i686_cache')
    x86_64Path = shelve.open('./cache/x86_64_cache')

    #Fetches the feed from cache or from the website
    news = feedcache.Cache(newsPath).fetch('http://www.archlinux.org/feeds/news/')
    i686 = feedcache.Cache(i686Path).fetch('http://www.archlinux.org/feeds/packages/i686/')
    x86_64 = feedcache.Cache(x86_64Path).fetch('http://www.archlinux.org/feeds/packages/x86_64/')

    #Closes feed
    newsPath.close()
    i686Path.close()
    x86_64Path.close()

    return news, i686, x86_64



class index:
    def GET(self):

        #web.header('Content-Type','application/xhtml+xml; charset=utf-8')

        # Store title and url for news together, only store 4 entries
        newsFeed, i686Feed, x86_64Feed = getFeeds();
        
        news = [(x.title, x.link) for x in newsFeed.entries][:maxNEWS]      
        i686PKGs = [(x.title, x.category, x.link, x.summary) for x in i686Feed.entries][:maxPKGS]
        x86_64PKGs = [(x.title, x.category, x.link, x.summary) for x in x86_64Feed.entries][:maxPKGS]

        i686=Arch()
        x86_64=Arch()

        i686.add_packages(i686PKGs)
        x86_64.add_packages(x86_64PKGs)
 
        return render.index(news, i686, x86_64)

    #This function will get the search query and process it...
    def POST(self):
        i = web.input()

        sub = int(i.sub)
        query = i.q

        url=None
 
        if sub == 1:
            url="http://google.com/search?q="+query
        elif sub == 2:
            url='http://bbs.archlinux.org/search.php?action=search&keywords='+query+'&show_as=topics'
        elif sub == 3:
            url='http://wiki.archlinux.org/index.php/Special:Search?search='+query
        elif sub == 4:
            url='http://aur.archlinux.org/packages.php?K='+query 
        elif sub == 5:
            url='http://bugs.archlinux.org/index.php?string='+query
        
        #Redirect if we have a url
        if url:
            return web.Found(url)
        else:
            return web.badrequest()

if __name__ == "__main__":
    if SERVER is "webpy" or SERVER is "lighttpd":
        app.run()
    elif SERVER is "apache":
        #Tells apache we want the script to act as a fastcgi server
        web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    else:
        print "Unkown web server: " + SERVER
