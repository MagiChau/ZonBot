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

	def run(self):
		pass