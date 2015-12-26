import aiohttp
import asyncio
import configparser
from os import path
import re
import sys
CARBON_BOT_ID = "109338686889476096"
CARBON_URL = "https://www.carbonitex.net/discord/data/botdata.php"
class InviteManager():

	def __init__(self, client):
		self.client = client
		self.key = self.get_config_key()
		self.servercount = -1 #should never be in the POST
		self.payload = {'key': self.key, 'servercount': self.servercount}

	def get_config_key(self):
		config = configparser.ConfigParser()
		config.read(path.join(sys.path[0] + "/config.ini"))
		return config['CARBON']['key']

	async def update_servercount(self):
		self.servercount = len(self.client.servers)
		self.payload.update({'servercount':self.servercount})

	async def await_invite(self, message):
		if message.author.id == CARBON_BOT_ID and message.channel.is_private:
			regex_pattern = r'^https?://discord((.gg/)|(app.com/invite/))[a-zA-Z0-9]+$'
			match = re.match(regex_pattern, message.content)
			if match:		
				try:
					invite = await self.client.get_invite(message.content)
					if invite.server not in self.client.servers:
						await self.client.accept_invite(message.content)
						await self.client.send_message(message.channel, "server joined")
					else:
						await self.client.send_message(message.channel, "already in server")
				except (discord.HTTPException, discord.NotFound):
					await self.client.send_message(message.channel, "error joining server")

	async def post_alive(self):
		await self.update_servercount()
		async with aiohttp.post(CARBON_URL, params=self.payload):
			return

	async def run_alive_loop(self):
		await self.client.wait_until_ready()
		while not self.client.is_closed:
			await self.post_alive()
			await asyncio.sleep(800)
		


