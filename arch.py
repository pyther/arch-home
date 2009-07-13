#!/usr/bin/env python


def cut(x):
    maxL = 24 #max charcaters before split
  
    p=['','']
    #pkgn = package name
    #pkgv = package version
    #pkgr = package release

    pkgn,pkgv=x.split(' ')[:2]
    pkgv,pkgr=pkgv.split('-')
    pkgr='-'+pkgr #addes a dash in front of release number
 
    p[0]=pkgn+' '+pkgv+pkgr #Tooltip

    #Remove the release number
    if len(x) > maxL:
        p[1]=pkgn+' '+pkgv

        #Remove the pkg version
        if len(p[1]) > maxL:
            p[1]=pkgn
       
            #In the unsual case that the pkgname is bigger than the allowed max characters
            #Cut the pkgname
            if len(p[1]) > maxL:
                p[0]=p[1][:maxL]

    else:
        p[1]=pkgn+' '+pkgv+pkgr

    return p

class arch:
    "Stores package information for architecture"
        
    packages=[]

    def add_package(self, pkgn, url):
        
        p = cut(pkgn)

        pkg_name = p[0]
        pkg_name_short = p[1]
        
        self.packages.append({'pkgn':pkg_name, 'short_pkgn':pkg_name_short, 'url':url})

        return

