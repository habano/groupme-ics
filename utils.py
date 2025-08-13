from icalendar import Calendar, Event
   from datetime import datetime
   import pytz
   import uuid
   from flask import current_app
   import requests

   def load_groupme_json(app, groupme_api_key, groupme_group_id):
       url_group_info = f'https://api.groupme.com/v3/groups/{groupme_group_id}'
       url_calendar = f'https://api.groupme.com/v3/conversations/{groupme_group_id}/events/list'
       headers = {'X-Access-Token': groupme_api_key}

       response = requests.get(url_calendar, headers=headers)
       if response.status_code != 200:
           current_app.groupme_load_successfully = False
           current_app.groupme_calendar_json_cache = {}
           app.logger.error(f'Events API failed: {response.status_code}: {response.text}')
           return False

       current_app.groupme_calendar_json_cache = response.json()
       app.logger.info(f'Events API response: {current_app.groupme_calendar_json_cache}')

       response = requests.get(url_group_info, headers=headers)
       if response.status_code == 200:
           if response.json().get('response', {}).get('name'):
               current_app.groupme_calendar_name = response.json()['response']['name']
               app.logger.info(f'Group name: {current_app.groupme_calendar_name}')
       else:
           app.logger.error(f'Group info API failed: {response.status_code}: {response.text}')

       current_app.groupme_load_successfully = True
       return True

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