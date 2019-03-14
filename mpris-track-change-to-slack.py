#!/usr/bin/python

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
import os

slack_token = 'xoxs-2985676589-2988733898-571622474405-ea253df1662401a78a2c0f0310f0f76a93c9ef39d532a5496c7b2cb34587ede4'
# slack_token = os.environ["SLACK_API_TOKEN"]
emoji_name = 'curtis-album-art'

def download(url):
	get_response = requests.get(url, stream=True)
	with open(emoji_name, 'wb') as f:
		for chunk in get_response.iter_content(chunk_size=1024):
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)
		return emoji_name
	
	return False

def get_default_status_emoji():
	return random.choice([
		':cd:',
		':headphones:',
		':musical_note:',
		':notes:',
		':radio:',
	])

def get_local_file(art_url):
	if "file:///" in art_url:
		return art_url.replace('file://', '')
	
	return download(art_url)

def delete_slack_emoji():
	postBody = {
		'token': slack_token,
		'name': emoji_name,
	}
	
	r = requests.post(
		'https://slack.com/api/emoji.remove',
		data = postBody
	)

	if(r.ok):
		parsed = json.loads(r.text)
		if parsed['ok']:
			return True
		else:
			return False
	else:
		r.raise_for_status()
	
	return False

def ensure_slack_does_not_have_emoji():
	r = requests.get(
		'https://slack.com/api/emoji.list',
		params = {'token': slack_token}
	)

	if(r.ok):
		parsed = json.loads(r.text)
		
		if parsed['ok']:
			if emoji_name in parsed['emoji']:
				return delete_slack_emoji()
			else:
				return True
		else:
			return False
	else:
		r.raise_for_status()
	
	return False

def upload_file_to_slack(local_file):
	slack_does_not_have_emoji = ensure_slack_does_not_have_emoji()
	if not slack_does_not_have_emoji:
		return False
	with open(local_file, 'rb') as f:
		postBody = {
			'token': slack_token,
			'mode': 'data',
			'name': emoji_name,
		}
		
		files = {'image': f}

		r = requests.post(
			'https://slack.com/api/emoji.add',
			data = postBody, files = files
		)
	
	if os.path.exists(local_file):
		  os.remove(local_file)

	if(r.ok):
		parsed = json.loads(r.text)
		if parsed['ok']:
			return emoji_name
		else:
			return False
	else:
		r.raise_for_status()
	
	return False

def get_status_emoji(metadata):
	if (not metadata['mpris:artUrl']) or ("default_album_med" in metadata['mpris:artUrl']):
		return get_default_status_emoji()
	
	local_file = get_local_file(metadata['mpris:artUrl'])
	
	if local_file:
		uploaded_file_to_slack = upload_file_to_slack(local_file)
		if uploaded_file_to_slack:
			return ':' + uploaded_file_to_slack + ':'
	return get_default_status_emoji()

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
		status_text = status_text[:97] + ('...' if len(status_text) > 97 else '')
		try:
			length = metadata['mpris:length'] / 1000000 # comes in as microseconds
		except:
			length = 180 # 3 minutes
			
		expiration_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=length)
		status_emoji = get_status_emoji(metadata)
		profile = {
			'status_text': status_text,
			'status_emoji': status_emoji,
			'status_expiration': calendar.timegm(expiration_time.timetuple()),
		}

		postBody = {
			'profile': json.dumps(profile),
			'token': slack_token,
		}

		print('Attempting to set status: ' + status_text)

		r = requests.post(
			'https://slack.com/api/users.profile.set',
			data = postBody
		)

		if(r.ok):
			parsed = json.loads(r.text)
			if parsed['ok']:
				print('Success')
			else:
				print('Error setting status : ' + parsed['error'])
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
				print('Currently playing: ' + interface.Get('org.mpris.MediaPlayer2', 'Identity'))
				return interface
				
				print('No players playing!')
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
