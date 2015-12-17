# -*- coding: utf-8 -*-
import asyncio
import configparser
import random
import discord
from discord import *
import hs_card_lookup

class Bot(Client):
	def __init__(self):
		super(Bot, self).__init__()
		self.set_config_vars()
		self.set_commands()

	def set_config_vars(self):
		config = configparser.ConfigParser()
		config.read("config.ini")
		self.email = config['LOGIN']['email']
		self.password = config['LOGIN']['password']

	def set_commands(self):
		self.commands = {
			"!acceptinvite": self.accept_invite_command,
			"!card": self.hearthstone_card_lookup_command,
			"!cuck": self.cuck_command,
			"!info": self.info_command,
			"!help": self.help_command,
			"(╯°□°）╯︵ ┻━┻": self.unflip_command,
			"┬─┬﻿ ノ( ゜-゜ノ)": self.flip_command}

	@asyncio.coroutine
	def accept_invite_command(self, message):
		if message.content.startswith("!acceptinvite "):
			print(message.content)
			yield from self.accept_invite(message.content[14:])

	@asyncio.coroutine
	def cuck_command(self, message):
		if message.content.startswith("!cuck "):
			name = message.content[6:]

			if random.randint(0, 99) < 50:
				yield from self.send_message(message.channel, "{} is a cuck".format(name))
			else:
				yield from self.send_message(message.channel, "{} is a cuck".format(message.author.name))
	
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
		yield from self.send_message(message.channel, text)

	@asyncio.coroutine
	def help_command(message):
		if message.content == "!help":
			help_message_base = "Commands: "
			help_message = ""

			for command in command_dict:
				help_message = help_message + ', ' + command

			help_message = help_message[2:]

			help_message = help_message_base + help_message + "\nFor more information about a command type !help <command>"

		elif message.content =="!help card":
			help_message = 'Usage: !card <query>\nLooks up a Hearthstone card by name and returns the best matching card. Can also be used by typing a query within square brackets. E.g. [Ragnaros]'
		elif message.content =="!help cuck":
			help_message = 'Usage: !cuck <name>\nRandomly decides if a person is a cuck. If they are not, then the user of the command is a cuck.'

		yield from self.send_message(message.channel, help_message)

	@asyncio.coroutine
	def unflip_command(self, message):
		yield from self.send_message(message.channel, "┬─┬﻿ ノ( ゜-゜ノ)")

	@asyncio.coroutine
	def flip_command(self, message):
		yield from self.send_message(message.channel, "(╯°□°）╯︵ ┻━┻")

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