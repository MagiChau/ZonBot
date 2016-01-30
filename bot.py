import asyncio
import config
import discord
from discord.ext import commands
import os
import sys
import time

class Bot(commands.Bot):
	def __init__(self, command_prefix):
		super().__init__(command_prefix)
		self._load_config_data()
		self._initialize_listeners()
		self._initialize_extensions()
		self.start_time = 0

	def _load_config_data(self):
		self.email = config.email
		self.password = config.password
		self.owner_id = config.owner_id
		self.twitch_id = config.twitch_id
		self.carbon_key = config.carbon_key

	def _initialize_listeners(self):
		self.add_listener(self._startup_message, 'on_ready')

	def _initialize_extensions(self):
		def _load_extension(name):
			self.load_extension('extensions.{0}.{0}'.format(name))
		_load_extension('owner_tools')
		_load_extension('info')
		_load_extension('picture')
		_load_extension('invite')
		_load_extension('hearthstone')
		_load_extension('twitch')
		_load_extension('moderate')
		

	async def _startup_message(self):
		print("Logged in as {}".format(self.user.name))
		print("User ID: {}".format(self.user.id))
		print("Library: {} - {}".format(discord.__title__, discord.__version__))
		self.start_time = time.time()

	def run(self):
		try:
			self.loop.run_until_complete(self.start(self.email, self.password))
		except KeyboardInterrupt:
			self.loop.run_until_complete(self.logout())
		finally:
			self.loop.close()