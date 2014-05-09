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
from picklecache import cache

use_cache = True
if use_cache:
    get = cache(os.path.expanduser('~/.tlevine'))(requests.get)
else:
    get = requests.get

def github(username):
    def pages():
        for page_number in itertools.count(1):
            url = 'https://api.github.com/users/%s/repos?page=%d' % (username, page_number)
            response = get(url)
            yield json.loads(response.text)

    for page in itertools.takewhile(lambda r: r != [], pages()):
        for repository in page:
            yield repository['html_url']

def thomaslevine():
    url = 'http://thomaslevine.com/!/'
    response = get(url)
    html = lxml.html.fromstring(response.text)
    html.make_links_absolute(url)
    return (str(link) for link in html.xpath('//a/@href') if link.startswith(url))

def scraperwiki(url = 'https://classic.scraperwiki.com/profiles/tlevine/index.html'):
    response = get(url)
    html = lxml.html.fromstring(response.text)
    html.make_links_absolute(url)
    for href in html.xpath('//li[@class="code_object_line"]/descendant::h3/a[position()=2]/@href'):
        yield re.sub(r'index.html$', '', str(href))
    nexts = html.xpath(u'//a[text()="Next »"]/@href')
    if nexts != []:
        for scraper in scraperwiki(nexts[0]):
            yield scraper

def gitorious():
    url = 'https://gitorious.org/tlevine.xml'
    response = get(url)
    project = lxml.html.fromstring(response.text.encode('utf-8'))
    project.make_links_absolute(url)
    for repository in project.xpath('//repository[owner[text()="tlevine"]]'):
        yield 'https' + repository.xpath('clone_url/text()')[0][3:-4]

def pypi():
    client = xmlrpc_client.ServerProxy('http://pypi.python.org/pypi')
    for role, package in client.user_packages('tlevine'):
        yield 'https://pypi.python.org/pypi/%s' % package

def manual():
    return [
        'https://chrome.google.com/webstore/detail/simple-webcam/cejgmnpegppdhkmmgmdobfelcdgfhkmo?hl=en',
    ]

def main(fp = sys.stdout):
    iter_github = list(map(github, ['tlevine', 'csv', 'csvsoundsystem', 'appgen', 'risley', 'mapshit']))
    iter_other  = [gitorious(), scraperwiki(), thomaslevine(), manual()]
    args = iter_other + iter_github
    for link in itertools.chain(*args):
        try:
            fp.write('%s\n' % link)
        except BrokenPipeError:
            break
