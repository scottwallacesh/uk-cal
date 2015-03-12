#!/usr/bin/env python

import sys
import urllib2
from lxml.html import fromstring

req = urllib2.Request('http://www.timeanddate.com/holidays/uk/')
response = urllib2.urlopen(req)
page = response.read()

print page

html = fromstring(page)
candidates = html.xpath('//*[@class="c0" or @class="c1"]')

events = {}
for event in candidates:
    rawdate = event.xpath('th/text()')[0]
    name = event.xpath('td/a/text()')[0]
    type = event.xpath('td[3]/text()')[0]

    print repr(name)
    if type in ['Observance', 'Bank holiday']:
        events[name] = {"date": rawdate, "type":  type}

print events
