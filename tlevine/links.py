# -*- encoding: utf-8 -*-
import os
import re
import sys
import itertools
import json
try:
    import xmlrpclib as xmlrpc_client
except ImportError:
    import xmlrpc.client as xmlrpc_client

import lxml.html
import requests

try:
    unicode
except NameError:
    unicode = str

use_cache = True
if use_cache:
    import datetime

    from vlermv import cache

    cachedir = os.path.expanduser('~/.tlevine/%s' % datetime.date.today().isoformat())
    get = cache(cachedir)(requests.get)
    def pypi_packages():
        @cache(cachedir)
        def _pypi_packages(_):
            client = xmlrpc_client.ServerProxy('http://pypi.python.org/pypi')
            try:
                return client.user_packages('tlevine')
            except Exception as e:
                sys.stderr.write('Error from PyPI:\n%s\n' % e)
                raise
        return _pypi_packages('pypi')
else:
    def get(url):
        try:
            return requests.get(url)
        except Exception as e:
            sys.stderr.write('Error at %s:\n%s\n' % (url, e))
            raise
    def pypi_packages():
        try:
            return xmlrpc_client.ServerProxy('http://pypi.python.org/pypi').user_packages('tlevine')
        except Exception as e:
            sys.stderr.write('Error from PyPI:\n%s\n' % e)
            raise

def github(username):
    def pages():
        for page_number in itertools.count(1):
            url = 'https://api.github.com/users/%s/repos?page=%d' % (username, page_number)
            try:
                response = get(url)
            except:
                pass
            else:
                if response.ok:
                    yield json.loads(response.text)
                else:
                    sys.stderr.write('%d response at %s\n' % (response.status_code, url))

    for page in itertools.takewhile(lambda r: r != [], pages()):
        for repository in page:
            yield repository['html_url']

def thomaslevine():
    url = 'http://thomaslevine.com/!/'
    try:
        response = get(url)
    except:
        return []
    else:
        html = lxml.html.fromstring(response.text)
        html.make_links_absolute(url)
        return (unicode(link) for link in html.xpath('//a/@href') if link.startswith(url))

def scraperwiki(url = 'https://classic.scraperwiki.com/profiles/tlevine/index.html'):
    try:
        response = get(url)
    except:
        pass
    else:
        html = lxml.html.fromstring(response.text)
        html.make_links_absolute(url)
        for href in html.xpath('//li[@class="code_object_line"]/descendant::h3/a[position()=2]/@href'):
            yield re.sub(r'index.html$', '', unicode(href))
        nexts = html.xpath(u'//a[text()="Next »"]/@href')
        if nexts != []:
            for scraper in scraperwiki(nexts[0]):
                yield scraper

def gitorious():
    url = 'https://gitorious.org/tlevine.xml'
    try:
        response = get(url)
    except:
        pass
    else:
        project = lxml.html.fromstring(response.text.encode('utf-8'))
        project.make_links_absolute(url)
        for repository in project.xpath('//repository[owner[text()="tlevine"]]'):
            yield 'https' + repository.xpath('clone_url/text()')[0][3:-4]
 
def npm():
    url = 'https://www.npmjs.org/~tlevine'
    try:
        response = get(url)
    except:
        return []
    else:
        html = lxml.html.fromstring(response.text)
        html.make_links_absolute(url)
        return map(unicode, html.xpath('id("profile")/ul/li/a/@href'))
 
def pypi():
    for role, package in pypi_packages():
        yield 'https://pypi.python.org/pypi/%s' % package

def manual():
    return [
        'https://chrome.google.com/webstore/detail/simple-webcam/cejgmnpegppdhkmmgmdobfelcdgfhkmo?hl=en',
    ]

def main(fp = sys.stdout):
    iter_github = list(map(github, ['tlevine', 'csv', 'csvsoundsystem', 'appgen', 'risley', 'mapshit']))
    iter_other  = [npm(), pypi(), gitorious(), scraperwiki(), thomaslevine(), manual()]
    args = iter_other + iter_github
    for link in itertools.chain(*args):
        try:
            fp.write('%s\n' % link)
        except BrokenPipeError:
            break
