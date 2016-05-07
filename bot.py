import asyncio
import config
import discord
from discord.ext import commands
import os
import sys
import time

class Bot(commands.Bot):
	def __init__(self, command_prefix, formatter=None, description=None, pm_help=False, **options):
		super().__init__(command_prefix, formatter, description, pm_help, **options)
		self._load_config_data()
		self._initialize_listeners()
		self._initialize_extensions()
		self.start_time = 0

	def _load_config_data(self):
		self.email = config.email
		self.password = config.password
		self.token = config.token
		self.owner_id = config.owner_id
		self.twitch_id = config.twitch_id
		self.carbon_key = config.carbon_key

	def _initialize_listeners(self):
		self.add_listener(self._startup_message, 'on_ready')

	def _initialize_extensions(self):
		def _load_extension(name):
			self.load_extension('extensions.{0}'.format(name))
		_load_extension('loader')
		_load_extension('util')
		_load_extension('info')
		_load_extension('picture')
		#_load_extension('invite')
		_load_extension('hearthstone')
		_load_extension('twitch')
		_load_extension('moderate')
		_load_extension('carbon')
		

	async def _startup_message(self):
		print("Logged in as {}".format(self.user.name))
		print("User ID: {}".format(self.user.id))
		print("Library: {} - {}".format(discord.__title__, discord.__version__))
		self.start_time = time.time()

	async def on_message(self, message):
		try:
			await self.process_commands(message)
		except Exception as e:
			print("Command Error Caught At Top Level")
			print(message.content)
			print(e)
