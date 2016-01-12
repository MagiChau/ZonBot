import asyncio
import configparser
import discord
from discord.ext import commands

class Bot(commands.Bot):
	def __init__(self, config_filepath, command_prefix):
		super().__init__(command_prefix)
		self._load_config_data(config_filepath)

	def _load_config_data(self, filepath):
		config = configparser.ConfigParser()
		config.read(filepath)
		self.email = config['LOGIN']['email']
		self.password = config['LOGIN']['password']
		self.owner_ID = config['OWNER']['id']
		self.twitch_ID = config['TWITCH']['client_id']
		self.carbon_key = config['CARBON']['key']

	async def on_ready(self):
		print("Logged in as {}".format(self.user.name))
		print("User ID: {}".format(self.user.id))
		print("Library: {} - {}".format(discord.__title__, discord.__version__))

	def run(self):
		try:
			self.loop.run_until_complete(self.start(self.email, self.password))
		except KeyboardInterrupt:
			self.loop.run_until_complete(self.logout())
		finally:
			self.loop.close()