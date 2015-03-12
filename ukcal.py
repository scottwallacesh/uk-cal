#!/usr/bin/env python

import sys
import urllib2
from lxml.html import fromstring
import datetime
import time

#===================
# Flask stuff for Google App Engine
#===================
#from flask import Flask
#app = Flask(__name__)
#===================

class Calendar:
    header = "BEGIN:VCALENDAR\nX-WR-CALNAME:UK Secular Calendar\nVERSION:2.0\nPRODID:-//Scott Wallace//NONSGML uk-cal//EN"
    footer = "END:VCALENDAR"

    def __init__(self):
        self.events = []

    def add(self, event):
        # Check it's a valid Event type and the fields are all correct:
        if isinstance(event, Event) and event.check_fields():
            self.events.append(event)

    def __str__(self):
        output = self.header + "\n"
        for event in self.events:
            output += str(event)
        output += self.footer + "\n"

        return output

class Event:
    mandatory_fields = [ "DTSTART", "SUMMARY", "LOCATION", "UID" ]

    header = "BEGIN:VEVENT"
    footer = "END:VEVENT"

    def __init__(self):
        self.fields = {}

    def check_fields(self):
        # Check the mandatory fields exist:
        for field in self.mandatory_fields:
            if field not in self.fields:
                return False

        # Check the time entries are the correct type:
        if not isinstance(self.fields["DTSTART"], time.struct_time):
            return False

        return True

    def __str__(self):
        # Check the basics exist
        if self.check_fields():
            output = self.header + "\n"

            # Output the fields added
            for key, val in self.fields.iteritems():
                # Format time values correctly
                if isinstance(val, time.struct_time):
                    key = "%s;VALUE=DATE" % key
                    val = time.strftime("%Y%m%d", val)

                output += "%s:%s\n" % (key, val)

            output += "DTSTAMP:%s" % time.strftime("%Y%m%dT%H%M00Z", time.localtime()) + "\n"
            output += self.footer + "\n"

            return output

req = urllib2.Request('http://www.timeanddate.com/holidays/uk/')
response = urllib2.urlopen(req)
page = response.read()

html = fromstring(page)
candidates = html.xpath('//*[@class="c0" or @class="c1"]')

calendar = Calendar()
for event in candidates:
    if event.xpath('td[3]/text()')[0] in ['Observance', 'Bank holiday', 'Common Local holidays']:
        new_event = Event()
        eventdate = datetime.datetime.strptime(event.xpath('th/text()')[0], '%b %d')

        new_event.fields["UID"] = event.xpath('@id')[0]
        new_event.fields['DTSTART'] = eventdate.replace(year=int(datetime.datetime.now().strftime('%Y'))).timetuple()
        new_event.fields['SUMMARY'] = event.xpath('td/a/text()')[0]
        new_event.fields['LOCATION'] = 'UK'
        new_event.fields['DURATION'] = 'PT1D'

        calendar.add(new_event)

print str(calendar)
