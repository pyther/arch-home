#!/usr/bin/env python


def cut(pkgname,pkgver):
    maxL = 24 #max charcaters before split

    pkgver,pkgrel=pkgver.split('-')

    pkgfull=pkgname+' '+pkgver+'-'+pkgrel #Tooltip
    # p[0] = tooltip
    # p[1] = display name
    p=[pkgfull,pkgfull]

    #Remove the release number
    if len(p[1]) > maxL:
        p[1]=pkgname+' '+pkgver

        #Remove the pkg version
        if len(p[1]) > maxL:
            p[1]=pkgname

            #In the unsual case that the pkgname is bigger than the allowed max characters
            #Cut the pkgname
            if len(p[1]) > maxL:
                p[1]=p[1][:maxL]

    return p

class Arch:
    "Stores package information for architecture"

    def __init__(self):
        self.packages=[]

    def add_package(self, pkgname, pkgver, pkgurl, pkgrepo, pkgdesc):

        pkg_name, pkg_name_short = cut(pkgname, pkgver)

        self.packages.append({'pkgname':pkg_name, 'short_pkgname':pkg_name_short, 'pkgurl':pkgurl, 'pkgrepo':pkgrepo, "pkgdesc":pkgdesc})

        return

    def length(self):
        return len(self.packages)
