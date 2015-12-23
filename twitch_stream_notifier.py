import asyncio
import configparser
import discord
import json
import requests
import sys

class TwitchStreamNotifier():
	def __init__(self, client, client_id=None):
		self.client = client
		if client_id is None:
			self.set_client_id()
		else:
			self.client_id = client_id

		self.TWITCH_API_BASE_URL = 'https://api.twitch.tv/kraken/'
		self.header = dict()
		self.header.update({'Client-ID':self.client_id})
		self.header.update({'version':'Accept: application/vnd.twitchtv.v3+json'})
		self.update_stream_list(sys.path[0] + '/stream_list')
		self.notified_channels = ["96378857971531776"]

	def set_client_id(self):
		config = configparser.ConfigParser()
		config.read(sys.path[0] + "/config.ini")
		self.client_id = config['TWITCH']['client_id']

	def update_stream_list(self, filepath):
		"""Retrieves the list of streams to check from a config file"""
		self.streams = {}
		with open(filepath, 'r') as stream_file:
			for line in stream_file:
				self.streams.update({line.strip():False})

	@asyncio.coroutine
	def check_stream_online(self, stream_name):
		url = self.TWITCH_API_BASE_URL + 'streams/' + stream_name
		response = requests.get(url, headers=self.header)
		self.check_for_http_error(response)
		response = json.loads(response.text)

		if response['stream'] is None: 
			return False 
		else: 
			return True

	def check_for_http_error(self, response):
		"""Checks the status code of a Response for a HTTP error and prints the error

		Args:
			response (Response): Twitch API Response obj
		"""
		try:
			response.raise_for_status()
		except requests.exceptions.HTTPError:
			req_error = json.loads(response.text)
			print ('HTTP Error ' + str(response.status_code) + ': ' + req_error['error'] + ', ' + req_error['message'])

	@asyncio.coroutine
	def notify_stream_online(self, stream):
		current_status = (yield from self.check_stream_online(stream))
		if self.streams[stream] == False and current_status == True:
			self.streams[stream] = True
			for channel in self.notified_channels:
				output = stream + ' is now online at http://www.twitch.tv/' + stream 
				yield from self.client.send_message(discord.Object(channel), output)
		elif current_status == False:
			self.streams[stream] = False

	@asyncio.coroutine
	def run(self):
		while True:
			#Runs the noitifiers
			for stream in self.streams:
				yield from self.notify_stream_online(stream)
			yield from asyncio.sleep(60)
