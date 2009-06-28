#
# $Id$
#

PROJECT=FeedCache
VERSION=1.3.1
RELEASE=$(PROJECT)-$(VERSION)

help:
	@echo "package - build source distro"
	@echo "register - update pypi index"

package: setup.py
	python setup.py sdist --force-manifest
	mv dist/*tar.gz ~/Desktop/

register: setup.py
	python setup.py register

%: %.in
	cat $< | sed 's/VERSION/$(VERSION)/g' > $@

tags:
	find . -name '*.py' | etags -l auto --regex='/[ \t]*\def[ \t]+\([^ :(\t]+\)/\1/' -
