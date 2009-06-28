#!/usr/bin/env python

import web
import feedparser
import feedcache

import sys
import shelve

urls = (
  '/', 'index'
)

web.config.debug = True

render = web.template.render('templates')

app = web.application(urls, globals())
web.template.Template.globals['render'] = render

#Time until cached feeds expire
timeToLiveSeconds=900   #15 Minutes

#Truncates pkg name if it is to long...
def cut(x):
    if len(x) > 23:
        x=x[:23]
    return x

# Gets and stores a cached copy of the news feed
def get_newsFeed():
    
    #Stores file as .nfeed_cache in CWD
    storage = shelve.open('./cache/nfeed_cache')
    
    fc = feedcache.Cache(storage)
    
    #Fetches the feed from cache or from the website
    nfeed = fc.fetch('http://www.archlinux.org/feeds/news/')
    
    #Closes feed
    storage.close()
    
    return nfeed

def get_pkgFeed():
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

        pkg = [x.title for x in u.entries]

        i686 = []
        x86_64 = []

        # This adds the truncated and full package name
        # The i686 or x86_64 gets removed from the package name:
        for x in pkg:
            if x.find('i686') > 0:
                if len(i686) < 5:
                    i686.append( (cut(x.rstrip(' i686')), x.rstrip(' i686')) )
            elif x.find('x86_64') > 0:
                if len(x86_64) < 5:
                    x86_64.append( (cut(x.rstrip(' x86_64')), x.rstrip(' x86_64')) )
            else:
                #Huh why are we here what changed?
                pass
 

        return render.index(news, i686, x86_64)

    #This function will get the search query and process it...
    def POST(self):
        i = web.input()

        sub = int(i.sub)
        query = i.q
 
        if sub == 1:
            url="http://google.com/search?q="+query
        elif sub == 2:
            url='http://bbs.archlinux.org/search.php?action=search&keywords='+query+'&show_as=topics'
        elif sub == 3:
            url='http://wiki.archlinux.org/index.php/Special:Search?search='+query
        elif sub == 4:
            url='http://aur.archlinux.org/packages.php?K='+query 
        web.Found(url)
        return

if __name__ == "__main__":
    app.run()
