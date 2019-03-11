#!/usr/bin/python

from ansimarkup import ansiprint
import calendar
import datetime
import dbus
import dbus.mainloop.glib
import glib
import json
import random
import re
import requests
import time

def get_status_emoji(metadata):
	return random.choice([
		':cd:',
		':headphones:',
		':musical_note:',
		':notes:',
		':radio:',
	]);

# This gets called whenever the player sends the PropertiesChanged signal
def playing_song_changed (Player,two,three):
	time.sleep(3) # to allow enough time to get the correct metadata (specifically length)
	global interface
	global track
	metadata = interface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
	track2 = ','.join(metadata['xesam:artist']) + ' - ' + metadata['xesam:title']

	if track != track2:
		track = ','.join(metadata['xesam:artist']) + ' - ' + metadata['xesam:title']
		status_text = 'Now Playing: ' + ','.join(metadata['xesam:artist']) + ' - ' + metadata['xesam:title']
		try:
			length = metadata['mpris:length'] / 1000000 # comes in as microseconds
		except:
			length = 180 # 3 minutes
			
		expiration_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=length)
		profile = {
			'status_text': status_text,
			'status_emoji': get_status_emoji(metadata),
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

dbus.mainloop.glib.DBusGMainLoop (set_as_default = True)

interface = getPlayingPlayer()
metadata = interface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
track = ','.join(metadata['xesam:artist']) + ' - ' + metadata['xesam:title']

interface.connect_to_signal ('PropertiesChanged', playing_song_changed)

# Run the GLib event loop to process DBus signals as they arrive
mainloop = glib.MainLoop ()
mainloop.run ()
