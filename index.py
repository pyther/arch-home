#!/usr/bin/env python

import web

import urllib
from BeautifulSoup import BeautifulSoup

import feedparser
import feedcache

import sys
import shelve

import pickle
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

#Downloads latest package listing from website
def getData():
    url="http://www.archlinux.org/packages/?sort=-last_update"
    try:
        data=urllib.urlopen(url)
    except IOError:
        data=''

    return data


def filterPackages(data):
    bs = BeautifulSoup(data)
    pkgs=bs.find('table', {"class" : "results"})
    pkgs=pkgs.findAll('tr', {"class": ["pkgr1","pkgr2"]})

    pkgname=[]
    pkgver=[]
    pkgarch=[]
    pkgrepo=[]
    pkgurl=[]
    pkgdesc=[]

    for x in range(len(pkgs)):
        # 0 - Arch         1 - Repo
        # 2 - URL          3 - Version
        # 4 - Description  5 - Date
        pkg=pkgs[x].findAll('td')
        
        arch=str(pkg[0].contents[0])
        repo=str(pkg[1].contents[0])
        name=str(pkg[2].a.contents[0])
        url='http://archlinux.org'+str(pkg[2].contents).split('"')[1]
        version=str(pkg[3].contents[0])
        desc=str(pkg[4].contents[0])
        date=str(pkg[5].contents[0])

        pkgarch.append(arch)
        pkgrepo.append(repo)
        pkgname.append(name)
        pkgurl.append(url)
        pkgver.append(version)
        pkgdesc.append(desc)


    pkglist=zip(pkgarch, pkgrepo, pkgname, pkgurl, pkgver, pkgdesc)        
    
    i686=Arch()
    x86_64=Arch()

    #Loop runs twice, once for i686 and once for x86_64
    for arch_name, arch_list in ( ('i686', i686), ('x86_64', x86_64) ):
        filtered_packages = [pkg for pkg in pkglist if (arch_name in pkg[0] or 'any' in pkg[0]) ]

        #print filtered_packages
        for pkg in filtered_packages[:5]:
            #Name, Version, URL, Repo
            arch_list.add_package(pkg[2],pkg[4],pkg[3],pkg[1],pkg[5])
    return (i686, x86_64) 


class index:
    def GET(self):

        #web.header('Content-Type','application/xhtml+xml; charset=utf-8')

        # Store title and url for news together, only store 4 entries
        nfeed = get_newsFeed();
        news = [(x.title, x.link) for x in nfeed.entries][:4]      
        
        pklFile='./cache/pkgdata.pkl'
        if os.path.isfile(pklFile):
            pkgCache = open(pklFile, 'rb')
            timestamp=pickle.load(pkgCache)
            expiredtimestamp=timestamp+datetime.timedelta(seconds=3600) #Take current timestamp and increase it by an hour

            # Is the current time an hour greater than orginal timestamp
            if datetime.datetime.now() > expiredtimestamp:
                getDataWrite=True
            else:
                getDataWrite=False
                i686=pickle.load(pkgCache)
                x86_64=pickle.load(pkgCache)
            pkgCache.close()
        else:
            getDataWrite=True
        
        if getDataWrite:
            #Fetches Website
            data=getData()
            if data:
                i686, x86_64 = filterPackages(data)
                pkgCache = open(pklFile, 'wb')
                pickle.dump(datetime.now(), pkgCache)
                pickle.dump(i686, pkgCache)
                pickle.dump(x86_64, pkgCache)
                pkgCache.close()
            else:
                i686=Arch()
                x86_64=Arch()

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
