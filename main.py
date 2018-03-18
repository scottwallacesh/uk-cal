#!/usr/bin/env python

"""
Google App Engine app to output iCal format of observed holidays
in England.
"""

import sys
import urllib2
from datetime import datetime
import time
from BeautifulSoup import BeautifulSoup


# ===================
# Stuff for Google App Engine
# ===================
from flask import Flask
APP = Flask(__name__)
# ===================


USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) ' +
              'AppleWebKit/537.36 (KHTML, like Gecko) ' +
              'Chrome/64.0.3282.186 Safari/537.36')


class Calendar(object):
    """ Class to represent a whole iCAL calendar. """
    header = """BEGIN:VCALENDAR
X-WR-CALNAME:UK Secular Calendar
VERSION:2.0
PRODID:-//Scott Wallace//NONSGML uk-cal//EN"""
    footer = 'END:VCALENDAR'

    def __init__(self):
        self.events = []

    def add(self, event):
        """ Method to add an Entry object to the Calendar """
        # Check it's a valid Event type and the fields are all correct
        if isinstance(event, Event) and event.check_fields():
            self.events.append(event)

    def __str__(self):
        """ Output calendar as iCal string. """
        output = self.header + '\n'
        for event in self.events:
            output += str(event)
        output += self.footer + '\n'

        return output


class Event(object):
    """ Class to represent an event """
    mandatory_fields = ['DTSTART', 'SUMMARY', 'LOCATION', 'UID']

    header = 'BEGIN:VEVENT'
    footer = 'END:VEVENT'

    def __init__(self):
        self.fields = {}

    def check_fields(self):
        """ Method to check mandatory iCal event fields exist """
        # Check the mandatory fields exist
        for field in self.mandatory_fields:
            if field not in self.fields:
                return False

        # Check the time entries are the correct type:
        if not isinstance(self.fields['DTSTART'], time.struct_time):
            return False

        return True

    def __str__(self):
        """ Output an event in iCal format """
        # Check the basics exist
        if self.check_fields():
            output = self.header + '\n'

            # Output the fields added
            for key, val in self.fields.iteritems():
                # Format time values correctly
                if isinstance(val, time.struct_time):
                    key = '%s;VALUE=DATE' % key
                    val = time.strftime('%Y%m%d', val)

                output += '%s:%s\n' % (key, val)

            output += 'DTSTAMP:%s\n' % time.strftime('%Y%m%dT%H%M00Z',
                                                     time.localtime())
            output += self.footer + '\n'

            return output
        return None


@APP.route('/')
def build_calendar():
    """
    Function to scrape and parse data from timeanddate.com and return it as
    as iCal calendar
    """
    calendar = Calendar()

    try:
        request = urllib2.Request('https://www.timeanddate.com/holidays/uk/')
        request.add_header('User-Agent', USER_AGENT)
        page = (urllib2
                .urlopen(request)
                .read())
    except urllib2.URLError as errmsg:
        APP.logger.error(errmsg)
    else:
        soup = BeautifulSoup(page)
        candidates = soup.findAll('tr', {'class': ['c0', 'c1']})
        for event in candidates:
            if event.findAll('td')[2].text in [
                    'Observance',
                    'Clock change/Daylight Saving Time'
            ]:
                new_event = Event()
                eventdate = (datetime.strptime(event.findAll('th')[0].text,
                                               '%b %d'))

                new_event.fields['UID'] = event['id']
                new_event.fields['DTSTART'] = (eventdate.replace(
                    year=int(datetime.now().strftime('%Y'))).timetuple())
                new_event.fields['SUMMARY'] = event.find('a').text
                new_event.fields['LOCATION'] = 'UK'
                new_event.fields['DURATION'] = 'PT1D'

                calendar.add(new_event)

    return str(calendar)


if __name__ == '__main__':
    print build_calendar()
    sys.exit(0)
