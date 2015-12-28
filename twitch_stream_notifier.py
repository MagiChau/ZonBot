import aiohttp
import asyncio
import configparser
import copy
import discord
import json
from os import path
import sqlite3
import sys

class TwitchStreamNotifier():
	def __init__(self, client, client_id=None):
		self.client = client
		self.streams = dict()
		if client_id is None:
			self.set_client_id()
		else:
			self.client_id = client_id

		self.TWITCH_API_BASE_URL = 'https://api.twitch.tv/kraken/'
		self.headers = dict()
		self.headers.update({'Client-ID':self.client_id})
		self.headers.update({'version':'Accept: application/vnd.twitchtv.v3+json'})
		self.streamdb_filepath = path.join(sys.path[0] + '/streams.db')
		self.create_stream_database()
		self.create_streams_dict()

	def set_client_id(self):
		config = configparser.ConfigParser()
		config.read(path.join(sys.path[0] + "/config.ini"))
		self.client_id = config['TWITCH']['client_id']

	def create_stream_database(self):
		"""Creates a stream database if it doesn't already exist"""
		conn = sqlite3.connect(self.streamdb_filepath)
		conn.execute("CREATE TABLE IF NOT EXISTS streams (cid text, stream text, PRIMARY KEY(cid, stream)) WITHOUT ROWID;")
		conn.commit()
		conn.close()

	def create_streams_dict(self):
		"""Creates a streams dictionary using the streams database, the previous dictionary will be deleted"""
		self.streams = dict()
		conn = sqlite3.connect(self.streamdb_filepath)
		for row in conn.execute("SELECT * FROM streams ORDER BY cid"):
			cid = row[0]
			stream = row[1]
			if cid in self.streams.keys():
				self.streams[cid].update({stream:False})
			else:
				self.streams[cid] = {stream:False}
		conn.close() 

	async def add_stream(self, cid, stream):
		"""
		Add a stream to the streams dictionary and the database. If an error has occurred
		return an error message string, else return None
		"""
		if not isinstance(stream, str) or not isinstance(cid, str):
			return None
		if cid not in self.streams:
			self.streams[cid] = {stream:False}
		else:
			if not stream in self.streams[cid]:
				self.streams[cid].update({stream:False})
		try:
			row = (cid, stream)
			conn = sqlite3.connect(self.streamdb_filepath)
			conn.execute("INSERT INTO streams VALUES(?,?);", row)
			conn.commit()
			conn.close()
			return "{} has been successfully added to the stream list".format(stream)
		except sqlite3.IntegrityError:
			return "Error: {} has already been added for this channel.".format(stream)

		return None

	async def does_stream_exist(self, stream):
		"""Returns whether a channel exists. Any error will result in False."""
		url = self.TWITCH_API_BASE_URL + 'channels/' + stream
		try:
			response = await aiohttp.get(url, headers=self.headers)
			raw = await response.json()
			response.close()
			if 'error' not in raw:
				return True
		except aiohttp.errors.ClientOSError:
			pass

		return False

	async def check_stream_online(self, stream):
		"""Returns whether a stream is online or not. If the request fails return None instead"""
		url = self.TWITCH_API_BASE_URL + 'streams/' + stream
		try:
			response = await aiohttp.get(url, headers=self.headers)
			if response.status == 200:
				raw = await response.json()
				response.close()
				if raw['stream'] is None: 
					return False 
				else: 
					return True
			response.close()
		except aiohttp.errors.ClientOSError:
			return None

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

	async def notify_stream_online(self, cid, stream):
		current_status = (await self.check_stream_online(stream))
		if self.streams[cid][stream] == False and current_status == True:
			self.streams[cid][stream] = True
			output = stream + ' is now online at http://www.twitch.tv/' + stream 
			await self.client.send_message(discord.Object(cid), output)
		elif current_status == False:
			self.streams[cid][stream] = False
		elif current_status is None:
			print("Error connecting to the Twitch API")

	async def run(self):
		await self.client.wait_until_ready()
		while not self.client.is_closed:
			streams_copy = copy.deepcopy(self.streams) #prevents collision on streams dictionary
			for cid in streams_copy:
				for stream in streams_copy[cid]:
					await self.notify_stream_online(cid, stream)
			await asyncio.sleep(60)
