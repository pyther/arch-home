#!/usr/bin/env python

import web
import feedparser
import feedcache

import sys
import shelve

from arch import arch

urls = (
  '/', 'index'
)

web.config.debug = True

render = web.template.render('templates')

app = web.application(urls, globals())
web.template.Template.globals['render'] = render


# Gets and stores a cached copy of the news feed
def get_newsFeed():
    
    #Time until cached feeds expire
    timeToLiveSeconds=1800   #30 Minutes

    #Stores file as .nfeed_cache in CWD
    storage = shelve.open('./cache/nfeed_cache')
    
    fc = feedcache.Cache(storage)
    
    #Fetches the feed from cache or from the website
    nfeed = fc.fetch('http://www.archlinux.org/feeds/news/')
    
    #Closes feed
    storage.close()
    
    return nfeed

def get_pkgFeed():
   
    #Time until cached feeds expire
    timeToLiveSeconds=900   #15 Minutes

    storage=shelve.open('./cache/pkgfeed_cache')
    fc = feedcache.Cache(storage)

    pkgs = fc.fetch('http://www.archlinux.org/feeds/packages/')
    storage.close()

    return pkgs

class index:
    def GET(self):

        # Gets the current RSS news feed
        # nfeed = news feed
        #nfeed = feedparser.parse('http://www.archlinux.org/feeds/news/')
        nfeed = get_newsFeed();


        # ntitle = title of news feeds
        ntitle = [x.title for x in nfeed.entries]
        
        # nurl = url of news feed
        nurl = [x.link for x in nfeed.entries]
        
        #Stores title and url together into a tuple
        news = [ntitle, nurl]
        
        # Feed for new packages
        #u = feedparser.parse('http://www.archlinux.org/feeds/packages/')
        u = get_pkgFeed()

        pkgn = [x.title for x in u.entries]
        purl = [x.link for x in u.entries]

        pkg=zip(pkgn,purl)

        i686 = arch()
        x86_64 = arch()

        # This adds the truncated and full package name
        # The i686 or x86_64 gets removed from the package name:
        for x in pkg:
            if 'i686' in x[0]:
                if i686.length() < 5:
                    i686.add_package(x[0], x[1])
            
            elif x[0].find('x86_64') > 0:
                if x86_64.length() < 5:
                    x86_64.add_package(x[0], x[1])
                    
            else:
                #Huh why are we here what changed?
                pass


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
            web.Found(url)
            return
        else:
            web.badrequest()
            return "<h1>400 - Bad Request</h1>"

if __name__ == "__main__":
    app.run()
