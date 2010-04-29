#!/usr/bin/env python


def cut(pkgname,pkgver):
    maxL = 24 #max charcaters before split

    p=['','']

    pkgver,pkgrel=pkgver.split('-')
    pkgrel='-'+pkgrel #addes a dash in front of release number

    p[0]=pkgname+' '+pkgver+pkgrel #Tooltip

    #Remove the release number
    if len(pkgname) > maxL:
        p[1]=pkgname+' '+pkgver

        #Remove the pkg version
        if len(p[1]) > maxL:
            p[1]=pkgname

            #In the unsual case that the pkgname is bigger than the allowed max characters
            #Cut the pkgname
            if len(p[1]) > maxL:
                p[0]=p[1][:maxL]

    else:
        p[1]=pkgname+' '+pkgver+pkgrel

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
