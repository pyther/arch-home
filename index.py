#!/usr/bin/env python2

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

import os
import datetime

from arch import Arch

urls = (
  '/', 'index',
  '/fetch', 'fetchFeeds'
)

web.config.debug = True

render = web.template.render('templates')

app = web.application(urls, globals())
web.template.Template.globals['render'] = render

#Time until cached feeds expire
timeToLiveSeconds=3600   #60 Minutes

# Feeds
newsRss='http://www.archlinux.org/feeds/news/'
x86Rss='http://www.archlinux.org/feeds/packages/i686/'
x64Rss='http://www.archlinux.org/feeds/packages/x86_64/'

newsFile='./cache/news_cache'
x86File='./cache/i686_cache'
x64File='./cache/x86_64_cache'

class index:
    def GET(self):

        #web.header('Content-Type','application/xhtml+xml; charset=utf-8')

        return render.index()

    #This function will get the search query and process it...
    def POST(self):
        i = web.input()

        sub = int(i.sub)
        query = i.q

        url=None

        if sub == 1:
            url="http://google.com/search?q="+query
        elif sub == 2:
            url='https://bbs.archlinux.org/search.php?action=search&keywords='+query+'&show_as=topics'
        elif sub == 3:
            url='https://wiki.archlinux.org/index.php/Special:Search?search='+query
        elif sub == 4:
            url='https://aur.archlinux.org/packages.php?K='+query
        elif sub == 5:
            url='https://bugs.archlinux.org/index.php?string='+query

        #Redirect if we have a url
        if url:
            return web.Found(url)
        else:
            return web.badrequest()

class fetchFeeds:
    def GET(self):
        # Corrupt Cache
        #  * Importing bsddb fails on many 2.7 instances,
        #    python tries to import corrupt cached using bsddb, this fails
        #  * DBPageNotFoundError, since python tried to import corrupt cache
        #    as a bsddb file, and it is not, it will error out

        i = web.input()
        feed = web.websafe(i.feed)

        if feed == 'news':
            try:
                newsCache = shelve.open(newsFile)
            except ImportError:
                os.remove(newsFile)
                newsCache = shelve.open(newsFile)

            try:
                newsFeed = feedcache.Cache(newsCache,timeToLiveSeconds).fetch(newsRss)
            except:
                newsCache.close()
                newsCache = shelve.open(newsFile)
                os.remove(newsFile)
                newsFeed = feedcache.Cache(newsCache,timeToLiveSeconds).fetch(newsRss)
            newsCache.close()

            news = [(x.title, x.link) for x in newsFeed.entries][:maxNEWS]
            return render.news(news)
        elif feed == 'i686':
            try:
                x86Cache = shelve.open(x86File)
            except:
                os.remove(x86File)
                x86Cache = shelve.open(x86File)

            try:
                x86Feed = feedcache.Cache(x86Cache,timeToLiveSeconds).fetch(x86Rss)
            except:
                x86Cache.close()
                os.remove(x86File)
                x86Cache = shelve.open(x86File)
                x86Feed = feedcache.Cache(x86Cache,timeToLiveSeconds).fetch(x86Rss)
            x86Cache.close()

            x86Pkgs = [(x.title, x.category, x.link, x.summary) for x in x86Feed.entries][:maxPKGS]
            x86=Arch()
            x86.add_packages(x86Pkgs)

            return render.packages(x86)
        elif feed == 'x86_64':
            try:
                x64Cache = shelve.open(x64File)
            except ImportError:
                os.remove(x64File)
                x64Cache = shelve.open(x64File)

            try:
                x64Feed = feedcache.Cache(x64Cache,timeToLiveSeconds).fetch(x64Rss)
            except:
                x64Cache.close()
                os.remove(x64File)
                x64Cache = shelve.open(x64File)
                x64Feed = feedcache.Cache(x64Cache,timeToLiveSeconds).fetch(x64Rss)
            x64Cache.close()

            x64Pkgs = [(x.title, x.category, x.link, x.summary) for x in x64Feed.entries][:maxPKGS]
            x64=Arch()
            x64.add_packages(x64Pkgs)
        return render.packages(x64)


if __name__ == "__main__":
    if SERVER is "webpy" or SERVER is "lighttpd":
        app.run()
    elif SERVER is "apache":
        #Tells apache we want the script to act as a fastcgi server
        web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
        app.run()
    else:
        print "Unkown web server: " + SERVER
