# -*- coding: utf-8 -*-
import asyncio
import configparser
from os import path
import random
import re
import sys
import time
import discord
from twitch_stream_notifier import TwitchStreamNotifier
import hs_card_lookup

class Bot(discord.Client):
	def __init__(self):
		super().__init__()
		self.set_config_vars()
		self.set_commands()
		self.twitch_notifier = TwitchStreamNotifier(self)
		self.start_time = None

	def set_config_vars(self):
		config = configparser.ConfigParser()
		config.read(path.join(sys.path[0] + "/config.ini"))
		self.email = config['LOGIN']['email']
		self.password = config['LOGIN']['password']
		self.ownerID = config['OWNER']['id']

	def set_commands(self):
		self.commands = {
			"!acceptinvite": self.accept_invite_command,
			"!addstream": self.addstream_command,
			"!baka": self.baka_command,
			"!card": self.hearthstone_card_lookup_command,
			"!channelinfo": self.channelinfo_command,
			"!cuck": self.cuck_command,
			"!eval": self.eval_command,
			"!help": self.help_command,
			"!info": self.info_command,
			"!nobully": self.nobully_command,			
			"!setgame": self.setgame_command,
			"!uptime": self.uptime_command,
			"!whois": self.whois_command,
			"(╯°□°）╯︵ ┻━┻": self.unflip_command,
			"┬─┬﻿ ノ( ゜-゜ノ)": self.flip_command}

	async def accept_invite_command(self, message):
		if self.ownerID == message.author.id:
			if message.content.startswith("!acceptinvite "):
				await self.accept_invite(message.content[14:])

	async def addstream_command(self, message):
		if message.content.startswith("!addstream "):
			stream = message.content[len("!addstream "):]
			if (await self.twitch_notifier.does_stream_exist(stream)):
				output = await self.twitch_notifier.add_stream(message.channel.id, stream)
				if output is not None:
					await self.send_message(message.channel, output)
			else:
				await self.send_message(message.channel, "Channel does not exist")

	async def baka_command(self, message):
		filepath = path.join((sys.path[0] + '/res/baka.jpg'))
		with open(filepath, 'rb') as picture:
			await self.send_file(message.channel, picture)

	async def nobully_command(self, message):
		filepath = path.join((sys.path[0] + '/res/nobully.jpg'))
		with open(filepath, 'rb') as picture:
			await self.send_file(message.channel, picture)

	async def channelinfo_command(self, message):
		if message.server is not None:
			output = "```Channel Name: {}\nChannel ID: {}".format(message.channel.name, message.channel.id)
			output = output + "\nServer Name: {}\nServer ID: {}```".format(message.server.name, message.server.id)
		else:
			output = "```Channel ID: {}```".format(message.channel.id)
		await self.send_message(message.channel, output)

	async def cuck_command(self, message):
		if message.content.startswith("!cuck "):
			name = message.content[6:]

			if random.randint(0, 99) < 50:
				await self.send_message(message.channel, "{} is a cuck".format(name))
			else:
				await self.send_message(message.channel, "{} is a cuck".format(message.author.name))

	async def eval_command(self, message):
		if self.ownerID == message.author.id:
			if message.content.startswith("!eval "):
				try:
					code = eval(message.content[6:])
					if asyncio.iscoroutine(code):
						code = await code
				except Exception as e:
					code = e
				output = '```python\n' + str(code) + '```'
				await self.send_message(message.channel, output)

	
	async def hearthstone_card_lookup_command(self, message):
		if message.content.startswith("!card "):
			query = message.content[6:]
			results = hs_card_lookup.find_matches(query, 0.5)
			if len(results) > 0:
				results.sort(key=lambda x: x[1], reverse = True)
				output = await self.format_hearthstone_card(results[0][0])
			else:
				output = "Card not found"

			await self.send_message(message.channel, output)

	async def format_hearthstone_card(self, card):
		card_type = card['type']
		card_text = ""
		flavor_text = ""
		player_class = ""

		async def remove_tags(text):
			new_text = text

			#Remove Spell Damage Character
			while '$' in new_text:
				pos = new_text.find('$')
				new_text = new_text[pos + 1:]

			def remove_html_tag(text, tag, replace):
				new_text = text

				start_tag = '<' + tag + '>'
				end_tag = '</' + tag + '>'

				new_text = new_text.replace(start_tag, replace)
				new_text = new_text.replace(end_tag, replace)

				return new_text

			new_text = remove_html_tag(new_text, 'b', '**')
			new_text = remove_html_tag(new_text, 'i', '*')

			return new_text

		if 'text' in card:
			card_text = await remove_tags(card['text'])
		if 'flavor' in card:
			flavor_text = await remove_tags(card['flavor'])
			if card_text != "":
				flavor_text = ' - ' + flavor_text
		if card_type == 'Minion':
			if 'playerClass' in card:
				player_class = card['playerClass']
			else:
				player_class = 'Neutral'
			output = "[{}]: {}/{} Cost: {} - {} - {}\n{}{}".format(card['name'], card['attack'], card['health'], card['cost'],
				player_class, card['expansion'], card_text, flavor_text)
		elif card_type == 'Spell':
			if 'playerClass' in card:
				player_class = " - " + card['playerClass']
			output = "[{}]: Cost: {}{} - {}\n{}{}".format(card['name'], card['cost'], player_class, card['expansion'],
				card_text, flavor_text)
		elif card_type == 'Weapon':
			if 'playerClass' in card:
				player_class = " - " + card['playerClass']
			output = "[{}]: {}/{} Cost: {}{} - {}\n{}{}".format(card['name'], card['attack'], card['durability'],
				card['cost'], player_class, card['expansion'], card_text, flavor_text)
		return output

	async def info_command(self, message):
		text = "Bot owned by ZonMachi\nDeveloped using the Discord.py library https://github.com/Rapptz/discord.py/"
		text = text + '\nCurrently connected to {} servers'.format(str(len(self.servers))) 
		await self.send_message(message.channel, text)

	async def help_command(self, message):
		if message.content == "!help":
			help_message_base = "Commands: "
			help_message = ""

			for command in self.commands:
				if command.startswith('!'):
					help_message = help_message + ', ' + command

			help_message = help_message[2:]

			help_message = help_message_base + help_message + "\nFor more information about a command type !help <command>"

		elif message.content == "!help acceptinvite":
			help_message = "Usage: !acceptinvite <URL>\nMakes the bot join the specified Discord server. Only owner can use this command."
		elif message.content =="!help card":
			help_message = 'Usage: !card <query>\nLooks up a Hearthstone card by name and returns the best matching card. Can also be used by typing a query within square brackets. E.g. [Ragnaros]'
		elif message.content =="!help cuck":
			help_message = 'Usage: !cuck <name>\nRandomly decides if a person is a cuck. If they are not, then the user of the command is a cuck.'
		elif message.content == "!help info":
			help_message = 'Usage: !info\nDisplays information about the bot.'

		await self.send_message(message.channel, help_message)

	async def unflip_command(self, message):
		await self.send_message(message.channel, "┬─┬﻿ ノ( ゜-゜ノ)")

	async def flip_command(self, message):
		await self.send_message(message.channel, "(╯°□°）╯︵ ┻━┻")

	async def setgame_command(self, message):
		if message.author.id == self.ownerID and message.content.startswith("!setgame "):
			game_name = message.content[len("!setgame "):]
			await self.change_status(discord.Game(name=game_name))

	async def uptime_command(self, message):
		seconds = int(time.time() - self.start_time)
		minutes = seconds // 60
		seconds -= minutes * 60
		hours = minutes // 60
		minutes -= hours * 60
		days = hours // 24
		hours -= days * 24

		#takes a numerical time and what it corresponds to e.g. hours and return a string
		def parse_time(time, time_type):
			if time > 0:
				return ' ' + str(time) + ' ' + time_type
			else:
				return ''

		seconds = parse_time(seconds, 'seconds')
		minutes = parse_time(minutes, 'minutes')
		hours = parse_time(hours, 'hours')
		days = parse_time(days, 'days')

		output = "ZonBot has been up for{}{}{}{}".format(days, hours, minutes, seconds)
		await self.send_message(message.channel, output)

	async def whois_command(self, message):
		if message.content.startswith('!whois '):
			user = message.content[len('!whois '):]
			match = re.fullmatch(r'<@[0-9]+>', user)
			if match:
				user = match.string[2:-1]
				found_user = utils.get(message.server.members, id = user)
			else:
				if re.fullmatch(r'[0-9]+', user):
					found_user = utils.get(message.server.members, id = user)
				else:
					found_user = utils.get(message.server.members, name = user)

			if found_user:
				output = "```Name: {}\nID: {}\nJoined Server On: {}/{}/{}```".format(found_user.name, found_user.id, \
					found_user.joined_at.month, found_user.joined_at.day, found_user.joined_at.year)
				await self.send_message(message.channel, output)


	async def list_delimited_text(self, message, delimiter1, delimiter2):
		result_list = []
		search_text = message.content
		while delimiter1 in search_text and delimiter2 in search_text:
			pos_first_delimiter = search_text.find(delimiter1)
			pos_second_delimiter = search_text.find(delimiter2)

			if pos_first_delimiter < pos_second_delimiter:
				result_list.append(search_text[pos_first_delimiter + 1: pos_second_delimiter])
				search_text = search_text[pos_second_delimiter + 1:]
		return result_list

	async def on_ready(self):
		self.start_time = time.time()
		print("Bot is connected")

	async def on_message(self, message):
		if message.author != self.user:
			command = message.content
			if command in self.commands:
				await self.commands[command](message)
			else:
				command = message.content.split(' ')[0]
				if command in self.commands:
					await self.commands[command](message)
				else:
					#search for delimited text
					hearthstone_queries = await self.list_delimited_text(message, '[', ']')
					output = ""
					for query in hearthstone_queries:
						results = hs_card_lookup.find_matches(query, 0.5)
						if len(results) > 0:
							results.sort(key=lambda x: x[1], reverse = True)
							output  = output + (await self.format_hearthstone_card(results[0][0])) +'\n\n'
					if output != "":
						await self.send_message(message.channel, output[:-2])

	def run(self):
		yield from self.start(self.email, self.password)

def main():
	bot = Bot()
	loop = asyncio.get_event_loop()
	loop.create_task(bot.twitch_notifier.run())
	loop.run_until_complete(bot.run())
	loop.close()

if __name__ == "__main__": main()