import sys
import urllib2
from lxml.html import fromstring

req = urllib2.Request('http://www.timeanddate.com/holidays/uk/')
response = urllib2.urlopen(req)
page = response.read()

print page

html = fromstring(page)
candidates = html.xpath('//*[@class="c0" or @class="c1"]')

events = []
for event in candidates:
    rawdate = event.xpath('th/text()')
    name = event.xpath('td/a/text()')
    type = event.xpath('td[3]/text()')

    if type[0] in ['Observance', 'Bank holiday']:
        events.append([name, rawdate, type[0]])

print events
