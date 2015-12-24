import aiohttp
import asyncio
import configparser
import copy
import discord
import json
import sys

async def create_TwitchStreamNotifier(client, client_id):
	ret

class TwitchStreamNotifier():
	def __init__(self, client, client_id=None):
		self.client = client
		if client_id is None:
			self.set_client_id()
		else:
			self.client_id = client_id

		self.TWITCH_API_BASE_URL = 'https://api.twitch.tv/kraken/'
		self.headers = dict()
		self.headers.update({'Client-ID':self.client_id})
		self.headers.update({'version':'Accept: application/vnd.twitchtv.v3+json'})
		self.stream_filepath = sys.path[0] + '/stream_list'
		self.create_stream_list(self.stream_filepath)
		self.notified_channels = ["96378857971531776"]

	def set_client_id(self):
		config = configparser.ConfigParser()
		config.read(sys.path[0] + "/config.ini")
		self.client_id = config['TWITCH']['client_id']

	def create_stream_list(self, filepath):
		"""Retrieves the list of streams to check from a config file"""
		self.streams = {}
		with open(filepath, 'r') as stream_file:
			for line in stream_file:
				self.streams.update({line.strip():False})

	async def update_stream_list(self, filepath):
		"""Retrieves the list of streams to check from a config file"""
		copy_streams = copy.deepcopy(self.streams)
		self.streams = {}
		with open(filepath, 'r') as stream_file:
			for line in stream_file:
				self.streams.update({line.strip():False})

		for stream in self.streams:
			if stream in copy_streams:
				self.streams.update([(stream, copy_streams[stream])])

	async def check_stream_online(self, stream_name):
		url = self.TWITCH_API_BASE_URL + 'streams/' + stream_name
		async with aiohttp.get(url, headers=self.headers) as response:
			assert response.status == 200
			raw = await response.text()
			raw = json.loads(raw)
			if raw['stream'] is None: 
				return False 
			else: 
				return True

	async def check_for_http_error(self, response):
		"""Checks the status code of a Response for a HTTP error and prints the error

		Args:
			response (Response): Twitch API Response obj
		"""
		try:
			response.raise_for_status()
		except requests.exceptions.HTTPError:
			req_error = json.loads(response.text)
			print ('HTTP Error ' + str(response.status_code) + ': ' + req_error['error'] + ', ' + req_error['message'])

	async def notify_stream_online(self, stream):
		current_status = (await self.check_stream_online(stream))
		if self.streams[stream] == False and current_status == True:
			self.streams[stream] = True
			for channel in self.notified_channels:
				output = stream + ' is now online at http://www.twitch.tv/' + stream 
				await self.client.send_message(discord.Object(channel), output)
		elif current_status == False:
			self.streams[stream] = False

	# async def update_stream_list_command(self, message):
	# 	if message.content.startswith('!addstream ':
	# 		channel = message.content[len('!addstream '):]
	# 		url = self.TWITCH_API_BASE_URL + 'channels/' + channel
	# 		async with aiohttp.get(url, headers=self.headers) as response:
	# 			assert response.status == 200
	# 			#add stream to stream list

	async def run(self):
		while True:
			await self.update_stream_list(self.stream_filepath)
			for stream in self.streams:
				await self.notify_stream_online(stream)
			await asyncio.sleep(60)
