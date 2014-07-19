#!/usr/bin/env python2

import feedparser
import pickle
import time

from flask import Flask
from flask import render_template, abort

MAX_PKGS = 8

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

def format_pkg_name(pkg):
    maxL = 24

    name,ver = pkg.split(' ')[:2]
    ver,rel = ver.split('-')

    full_name = '{0} {1}-{2}'.format(name, ver, rel)

    if len(full_name) <= maxL:
        return (full_name, full_name)

    short_name = '{0} {1}'.format(name, ver)

    if (len(short_name) <= maxL):
        return (full_name, short_name)

    short_name = name

    if (len(short_name) <= maxL):
        return (full_name, short_name)

    return (full_name, short_name[:maxL])


@app.route('/feed/<feed>/<arch>')
def fetch_feed2(feed, arch):
    return arch

@app.route('/feed/<name>')
def fetch_feed(name):
    if name == 'news':
        rss_feed = 'http://www.archlinux.org/feeds/news/'
        cache_file = './cache/news'
    elif name == 'pkgs_x64':
        rss_feed = 'http://www.archlinux.org/feeds/packages/x86_64/'
        cache_file = './cache/pkgs_x64'
    elif name == 'pkgs_x86':
        rss_feed = 'http://www.archlinux.org/feeds/packages/i686/'
        cache_file = './cache/pkgs_x86'
    else:
        abort(404)

    def write_feed(cache_file, feed):
        data=(time.time(), feed)
        pickle.dump(data, open(cache_file, "wb"))
        return

    expire_cache = 3600
    mtime = None

    try:
        cache = pickle.load(open(cache_file, 'rb'))
    except (IOError, KeyError) as e:
        # nothing to do, this is expecte
        pass
    else:
        mtime, cached_feed = cache

    # we must have a valid cache file
    if mtime:
        now = time.time()
        diff = int(now - mtime)

        # if cache file is stale
        if diff > expire_cache:
            feed = feedparser.parse(rss_feed, etag=cached_feed.etag)
            # feed has not been modified, update mtime so we don't check again
            if d2.status == 304:
                feed = cached_feed
                # write updated mtime to pickle file
                write_feed(cache_file, feed)
            # feed has been modified, lets update our cache
            else:
                # write new data pickle file
                write_feed(cache_file, feed)
        # cache is not stale, use cache
        else:
            feed = cached_feed
    # no cache file, that is okay
    else:
        feed = feedparser.parse(rss_feed)
        # write data to pickle file
        write_feed(cache_file, feed)

    if name == 'news':
        items = [ (x.title, x.link) for x in feed.entries]
        return render_template('news.html', news = items)
    elif 'pkgs' in name:
        pkgs = []
        for x in feed.entries[:MAX_PKGS]:
            full,short = format_pkg_name(x.title)
            pkgs.append({'name':full, 'short_name':short, 'cat':x.category, 'link':x.link, 'summary':x.summary})
        return render_template('pkgs.html', pkgs = pkgs)

    return 'None'

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

