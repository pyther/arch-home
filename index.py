#!/usr/bin/env python

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
    anyPath = shelve.open('./cache/any_cache')
    i686Path = shelve.open('./cache/i686_cache')
    x86_64Path = shelve.open('./cache/x86_64_cache')

    #Fetches the feed from cache or from the website
    news = feedcache.Cache(newsPath).fetch('http://www.archlinux.org/feeds/news/')
    Any = feedcache.Cache(anyPath).fetch('http://www.archlinux.org/feeds/packages/any/')
    i686 = feedcache.Cache(i686Path).fetch('http://www.archlinux.org/feeds/packages/i686/')
    x86_64 = feedcache.Cache(x86_64Path).fetch('http://www.archlinux.org/feeds/packages/x86_64/')

    #Closes feed
    newsPath.close()
    anyPath.close()
    i686Path.close()
    x86_64Path.close()

    return news, Any, i686, x86_64



class index:
    def GET(self):

        #web.header('Content-Type','application/xhtml+xml; charset=utf-8')

        # Store title and url for news together, only store 4 entries
        newsFeed, AnyFeed, i686Feed, x86_64Feed = getFeeds();
        
        news = [(x.title, x.link) for x in newsFeed.entries][:4]      
        anyPKG = [(x.title, x.category, x.link, x.summary, datetime.datetime.strptime(x.updated, "%a, %d %b %Y %H:%M:%S -0400")) for x in AnyFeed.entries]
        i686PKG = [(x.title, x.category, x.link, x.summary, datetime.datetime.strptime(x.updated, "%a, %d %b %Y %H:%M:%S -0400")) for x in i686Feed.entries]
        x86_64PKG = [(x.title, x.category, x.link, x.summary, datetime.datetime.strptime(x.updated, "%a, %d %b %Y %H:%M:%S -0400")) for x in x86_64Feed.entries]

        i686PKG = anyPKG + i686PKG
        #Sort packages by date
        i686PKG=sorted(i686PKG, key=lambda l: l[4], reverse=True)

        x86_64PKG = anyPKG + x86_64PKG
        #Sort Packages by Date
        x86_64PKG=sorted(x86_64PKG, key=lambda l: l[4], reverse=True)

        i686=Arch()
        x86_64=Arch()

        for p in i686PKG:
            i686.add_package(p[0],p[2],p[1],p[3])

        for p in x86_64PKG:
            x86_64.add_package(p[0],p[2],p[1],p[3])
        
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
    #Tells apache we want the script to act as a fastcgi server
    #web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
