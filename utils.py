from icalendar import Calendar, Event
from datetime import datetime
import pytz
import uuid

def groupme_json_to_ics(groupme_json):
    cal = Calendar()
    cal.add('version', '2.0')
    cal.add('prodid', '-//Andrew Mussey//GroupMe-to-ICS 0.1//EN')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', 'GroupMe: Athletics Mercado 16U')
    cal.add('x-wr-timezone', 'America/Los_Angeles')

    for event in groupme_json.get('response', {}).get('events', []):
        if event.get('deleted_at'):
            continue
        ical_event = Event()
        ical_event.add('summary', event.get('name', 'Unnamed Event'))
        ical_event.add('uid', event.get('event_id', str(uuid.uuid4())))
        start_time = datetime.fromisoformat(event.get('start_at').replace('Z', '+00:00'))
        ical_event.add('dtstart', start_time)
        end_time = datetime.fromisoformat(event.get('end_at', start_time.isoformat()).replace('Z', '+00:00'))
        ical_event.add('dtend', end_time)
        ical_event.add('description', event.get('description', ''))
        if event.get('location'):
            ical_event.add('location', event.get('location'))
        updated_at = datetime.fromisoformat(event.get('updated_at', start_time.isoformat()).replace('Z', '+00:00'))
        ical_event.add('last-modified', updated_at)
        ical_event.add('dtstamp', updated_at)  # Add DTSTAMP
        cal.add_component(ical_event)

    return cal.to_ical()
