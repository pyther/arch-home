#!/usr/bin/env python


def cut(pkgname):
    maxL = 24 #max charcaters before split

    pkgname,pkgver=pkgname.split(' ')[:2]

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

    # Takes PKG Name, URL, Repo, and Description and adds to it packages
    def add_package(self, pkgname, pkgurl, pkgrepo, pkgdesc):

        pkg_name, pkg_name_short = cut(pkgname)

        self.packages.append({'pkgname':pkg_name, 'short_pkgname':pkg_name_short, 'pkgurl':pkgurl, 'pkgrepo':pkgrepo, "pkgdesc":pkgdesc})

        return

    # Takes a list of tuples in the formant of (Package Name, Repo, Link, and Description)
    def add_packages(self, pkgs):
        for p in pkgs:
            self.add_package(p[0],p[2],p[1],p[3])
        return


    def length(self):
        return len(self.packages)
