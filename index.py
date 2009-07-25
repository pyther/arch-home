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
    timeToLiveSeconds=3600   #60 Minutes

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


        # Store title and url for news together, only store 4 entries
        news = [(x.title, x.link) for x in nfeed.entries][:4]      
 
        
        # Feed for new packages
        #u = feedparser.parse('http://www.archlinux.org/feeds/packages/')
        u = get_pkgFeed()

        pkg = [(x.title, x.link) for x in u.entries]

        i686 = arch()
        x86_64 = arch()

        #Loop goes though two times... one for i686 and one for x86_64
        for arch_name, arch_list in ( ('i686', i686), ('x86_64', x86_64) ):
            #Looking for pkgs with name of i686 or name of x86_64
            filtered_packages = [p for p in pkg if arch_name in p[0]]
            for p in filtered_packages[:5]:
                arch_list.add_package(p[0], p[1])

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
    app.run()
