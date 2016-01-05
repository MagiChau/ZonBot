import aiohttp
import asyncio
import configparser
import copy
import discord
import json
import memory_profiler
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

	async def clean_streams_database(self):
		"""Removes all streams from the database if the bot cannot see the Discord channel it belongs to"""
		channels = list()
		streams_copy = copy.deepcopy(self.streams)
		conn = sqlite3.connect(self.streamdb_filepath)
		for server in self.client.servers:
			channels.extend(list(map(lambda x: x.id, server.channels)))
		for cid in streams_copy:
			if cid not in channels:
				del self.streams[cid]
				try:
					conn.execute("DELETE FROM streams WHERE cid = ?", (cid,))
					conn.commit()
				except:
					print("Error deleting Channel {} from the database.".format(cid))
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

	async def remove_stream(self, cid, stream):
		"""
		Remove a stream from the streams dictionary and the database. If an error has occurred
		return an error message string, else return None
		"""
		if not isinstance(stream, str) or not isinstance(cid, str):
			return None
		if cid not in self.streams:
			return "Error: there are no streams for this channel."
		if stream not in self.streams[cid]:
			return "Error: {} is not in the stream list for this channel.".format(stream)
		elif stream in self.streams[cid]:
			del self.streams[cid][stream]
			try:
				row = (cid, stream)
				conn = sqlite3.connect(self.streamdb_filepath)
				conn.execute("DELETE FROM streams WHERE cid = ? AND stream = ?;", row)
				conn.commit()
				conn.close()
				return "{} has been successfully removed from the stream list".format(stream)
			except:
				return "Error removing {} from the streams database".format(stream)

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
		except aiohttp.errors.ClientOSError as e:
			return None

	async def get_stream(self, stream):
		"""Returns a stream dictionary of a Twitch stream. Returns None if request fails."""
		url = self.TWITCH_API_BASE_URL + 'streams/' + stream
		try:
			response = await aiohttp.get(url, headers=self.headers)
			if response.status == 200:
				raw = await response.json()
				return raw
				response.close()
			response.close()
		except aiohttp.errors.ClientOSError as e:
			return None

	async def list_stream(self, channelID):
		sep = ','
		if channelID not in self.streams or not self.streams[channelID]:
			return "No streams found."
		output = '```'
		for stream in self.streams[channelID]:
			output += stream + sep + ' '
		return output[:-(len(sep) + 1)] + '```'


	async def notify_stream_online(self, cid, stream):
		if cid in self.streams and stream in self.streams[cid]: #prevents error on checking a deleted stream
			stream_dict = await self.get_stream(stream)
			
			if stream_dict is None:
				print("Error connecting to the Twitch API. Channel:{} Stream: {}".format(cid, stream))
			elif stream_dict['stream'] is None:
				self.streams[cid][stream] = False
			elif self.streams[cid][stream] == False and stream_dict['stream'] is not None:
				self.streams[cid][stream] = True
				output = "{} is now playing {}: {} at {}".format(stream_dict['stream']['channel']['display_name'], 
					stream_dict['stream']['game'], stream_dict['stream']['channel']['status'],stream_dict['stream']['channel']['url'])
				try:
					await self.client.send_message(discord.Object(cid), output)
				except (discord.errors.Forbidden, discord.errors.NotFound) as e:
					print("Unable to send message in specified channel")
					if isinstance(e, discord.errors.NotFound):
						for stream in self.streams[cid]:
							self.remove_stream(cid, stream)

	async def run(self):
		await self.client.wait_until_ready()
		await self.clean_streams_database()
		while not self.client.is_closed:
			await asyncio.sleep(60)
			streams_copy = copy.deepcopy(self.streams) #prevents collision on streams dictionary
			for cid in streams_copy:
				for stream in streams_copy[cid]:
					await self.notify_stream_online(cid, stream)