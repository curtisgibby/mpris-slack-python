from ansimarkup import ansiprint
import calendar
import datetime
import dbus
import json
import random
import re
import requests

def getPlayingPlayer():
	session_bus = dbus.SessionBus()
	for service in session_bus.list_names():
		if re.match('org.mpris.MediaPlayer2.', service):
			player = session_bus.get_object(service, '/org/mpris/MediaPlayer2')
			interface = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
			playbackStatus = interface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
			if playbackStatus == 'Playing':
				ansiprint('<yellow>Currently playing:</yellow> ' + interface.Get('org.mpris.MediaPlayer2', 'Identity'))
				return interface

	ansiprint('<red>No players playing!</red>')
	quit()

interface = getPlayingPlayer()
metadata = interface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
print(metadata) # debug!
exit() # debug!

status_text = 'Now Playing: ' + ','.join(metadata['xesam:artist']) + ' - ' + metadata['xesam:title']
expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
profile = {
	'status_text': status_text,
	'status_emoji': random.choice([
		':cd:',
		':headphones:',
		':musical_note:',
		':notes:',
		':radio:',
	]),
	'status_expiration': calendar.timegm(expiration_time.timetuple()),
}

token = 'xoxp-2985676589-2988733898-571683094245-15016a48f3800b71c3c0a0ef308ca5f3'
postBody = {
	'profile': json.dumps(profile),
	'token': token,
}

url = 'https://slack.com/api/users.profile.set'

ansiprint('<yellow>Attempting to set status:</yellow> ' + status_text)

r = requests.post(url, data = postBody)

if(r.ok):
	parsed = json.loads(r.text)
	if parsed['ok']:
		ansiprint('<green>Success</green>')
	else:
		ansiprint('<red>Error setting status : ' + parsed['error'] + '</red>')
else:
	r.raise_for_status()
