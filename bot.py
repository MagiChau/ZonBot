# -*- coding: utf-8 -*-
import asyncio
import configparser
import random
import re
import sys
from discord import *
from twitch_stream_notifier import TwitchStreamNotifier
import hs_card_lookup

class Bot(Client):
	def __init__(self):
		super(Bot, self).__init__()
		self.set_config_vars()
		self.set_commands()
		self.twitch_notifier = TwitchStreamNotifier(self)

	def set_config_vars(self):
		config = configparser.ConfigParser()
		config.read(sys.path[0] + "/config.ini")
		self.email = config['LOGIN']['email']
		self.password = config['LOGIN']['password']
		self.ownerID = config['OWNER']['id']

	def set_commands(self):
		self.commands = {
			"!acceptinvite": self.accept_invite_command,
			"!baka": self.baka_command,
			"!card": self.hearthstone_card_lookup_command,
			"!cuck": self.cuck_command,
			"!eval": self.eval_command,
			"!info": self.info_command,
			"!help": self.help_command,
			"!whois": self.whois_command,
			"(╯°□°）╯︵ ┻━┻": self.unflip_command,
			"┬─┬﻿ ノ( ゜-゜ノ)": self.flip_command}

	@asyncio.coroutine
	def accept_invite_command(self, message):
		if self.ownerID == message.author.id:
			if message.content.startswith("!acceptinvite "):
				yield from self.accept_invite(message.content[14:])

	@asyncio.coroutine
	def baka_command(self, message):
		filepath = (sys.path[0] + '/res/baka.jpg')
		print(filepath)
		with open(filepath, 'rb') as picture:
			yield from self.send_file(message.channel, picture)

	@asyncio.coroutine
	def cuck_command(self, message):
		if message.content.startswith("!cuck "):
			name = message.content[6:]

			if random.randint(0, 99) < 50:
				yield from self.send_message(message.channel, "{} is a cuck".format(name))
			else:
				yield from self.send_message(message.channel, "{} is a cuck".format(message.author.name))

	@asyncio.coroutine
	def eval_command(self, message):
		white_listed_channels = ["119882119898988546", "96378857971531776"]
		if self.ownerID == message.author.id and message.channel.id in white_listed_channels:
			if message.content.startswith("!eval "):
				output = '```python\n' + str(eval(message.content[6:])) + '```'
				yield from self.send_message(message.channel, output)

	
	@asyncio.coroutine
	def hearthstone_card_lookup_command(self, message):
		if message.content.startswith("!card "):
			query = message.content[6:]
			results = hs_card_lookup.find_matches(query, 0.5)
			if len(results) > 0:
				results.sort(key=lambda x: x[1], reverse = True)
				output = yield from self.format_hearthstone_card(results[0][0])
			else:
				output = "Card not found"

			yield from self.send_message(message.channel, output)

	@asyncio.coroutine
	def format_hearthstone_card(self, card):
		card_type = card['type']
		card_text = ""
		flavor_text = ""
		player_class = ""

		def remove_tags(text):
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
			card_text = remove_tags(card['text'])
		if 'flavor' in card:
			flavor_text = remove_tags(card['flavor'])
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

	@asyncio.coroutine
	def info_command(self, message):
		text = "Bot owned by ZonMachi\nDeveloped using the Discord.py library https://github.com/Rapptz/discord.py/"
		text = text + '\nCurrently connected to {} servers'.format(str(len(self.servers))) 
		yield from self.send_message(message.channel, text)

	@asyncio.coroutine
	def help_command(self, message):
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

		yield from self.send_message(message.channel, help_message)

	@asyncio.coroutine
	def unflip_command(self, message):
		yield from self.send_message(message.channel, "┬─┬﻿ ノ( ゜-゜ノ)")

	@asyncio.coroutine
	def flip_command(self, message):
		yield from self.send_message(message.channel, "(╯°□°）╯︵ ┻━┻")

	@asyncio.coroutine
	def set_gameid_command(self, message):
		pass

	@asyncio.coroutine
	def whois_command(self, message):
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
				yield from self.send_message(message.channel, output)


	@asyncio.coroutine
	def list_delimited_text(self, message, delimiter1, delimiter2):
		result_list = []
		search_text = message.content
		while delimiter1 in search_text and delimiter2 in search_text:
			pos_first_delimiter = search_text.find(delimiter1)
			pos_second_delimiter = search_text.find(delimiter2)

			if pos_first_delimiter < pos_second_delimiter:
				result_list.append(search_text[pos_first_delimiter + 1: pos_second_delimiter])
				search_text = search_text[pos_second_delimiter + 1:]
		return result_list

	@asyncio.coroutine
	def on_ready(self):
		print("Bot is connected")
		#yield from self.twitch_notifier.run()

	@asyncio.coroutine
	def on_message(self, message):
		if message.author != self.user:
			command = message.content
			if command in self.commands:
				yield from self.commands[command](message)
			else:
				command = message.content.split(' ')[0]
				if command in self.commands:
					yield from self.commands[command](message)
				else:
					#search for delimited text
					hearthstone_queries = yield from self.list_delimited_text(message, '[', ']')
					output = ""
					for query in hearthstone_queries:
						results = hs_card_lookup.find_matches(query, 0.5)
						if len(results) > 0:
							results.sort(key=lambda x: x[1], reverse = True)
							output  = output + (yield from self.format_hearthstone_card(results[0][0])) +'\n\n'
					if output != "":
						yield from self.send_message(message.channel, output[:-2])

	def run(self):
		yield from self.start(self.email, self.password)

def main():
	bot = Bot()
	loop = asyncio.get_event_loop()
	#asyncio.BaseEventLoop.set_debug(loop, True)
	loop.run_until_complete(bot.run())
	loop.close()

if __name__ == "__main__": main()