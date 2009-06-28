feedcache - Maintain a cache of RSS and Atom Feed Data
---------------------------------------------

The feedcache package implements a class to wrap Mark Pilgrim's
Universal Feed Parser module so that parameters can be used to cache
the feed results locally instead of fetching the feed every time it is
requested. Uses both etag and modified times for caching. The cache is
parameterized to use different backend storage options.

Cache
-----

The Cache class manages feed data, fetching updates when the local
contents have expired.  It uses 'feedparser' to retrieve the data, and
supports both ETag and If-Modified-Since headers.

Storage API
---------

Each Cache uses a storage object to hold on to the data.  The storage
object must support the dictionary API.  Keys are the URLs of the
feed.  The data stored includes, but is not limited to, the parsed
result of the feed.

Cache + shelve
------------

Using shelve by itself works in a simple single-threaded case but it
isn't clear from its documentation whether shelve supports write
access from multiple concurrent threads. To ensure the shelf is not
corrupted, a thread lock should be used. 'CacheStorageLock' is a
simple wrapper around shelve that uses a lock to prevent more than one
thread from accessing the shelf simultaneously. 

See 'feedcache/cachestoragelock.py' and 'feedcache/example.py' for
more details.

Cache + shove
------------

Using 'CacheStorageLock' protects against corruption caused by
multiple threads in the same process, but shelve still only allows one
process to open a shelf file to write to it. In applications with
multiple processes that need to modify the cache, the 'shove' module,
by L. C. Rees, is an excellent alternative.  shove offers support for
a variety of back-end storage options, including: relational
databases, BSD-style databases, Amazon's S3 storage service, pickle
files, and others.

See 'feedcache/example_threads.py' for more details.

References
---------

http://www.doughellmann.com/articles/feedcache/index.html - Article from Python Magazine about using the module to build http://www.castsampler.com/.

http://www.feedparser.org/ - Mark Pilgrim's Universal Feed Parser

http://pypi.python.org/pypi/shove - shove, from L.C. Rees
