#!/usr/bin/env python
import web
import feedparser

urls = (
  '/', 'index'
)

web.config.debug = True

render = web.template.render('templates')

app = web.application(urls, globals())
web.template.Template.globals['render'] = render

def cut(x):
    if len(x) > 23:
        x=x[:23]
    return x

class index:
    def GET(self):
        n = feedparser.parse('http://www.archlinux.org/feeds/news/')
        ntitle = [x.title for x in n.entries]
        nurl = [x.link for x in n.entries]
        news = [ntitle, nurl]
        
        u = feedparser.parse('http://www.archlinux.org/feeds/packages/')
        pkg = [x.title for x in u.entries]

        i686 = []
        x86_64 = []

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

if __name__ == "__main__":
    app.run()
