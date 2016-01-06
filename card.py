import re, json

def json_file_to_dict(inputfile):
	f_read = open(inputfile, 'r', encoding="utf8")
	cards_dict = json.loads(str(f_read.read()))
	f_read.close()
	return cards_dict

def remove_non_collectible_cards(cards):
	del cards['Credits']
	del cards['Debug']
	del cards['Hero Skins']
	del cards['Missions']
	del cards['System']
	del cards['Tavern Brawl']

	for exp in cards:
		list_copy = list(cards[exp])
		for card in list_copy:
			if 'type' not in card.keys() or card['type'] == 'Hero' or card['type'] == 'Enchantment'\
			or card['type'] == 'Hero Power' or 'cost' not in card:
				cards[exp].remove(card)
			else: 
				card.update(expansion = exp)

def remove_cards_with_regex(cards, pattern, expansion=None):
	if expansion is not None:
		cards_copy = list(cards[expansion])
		for card in cards_copy:
			if (re.match(pattern, card['id'])):
				cards[expansion].remove(card)
	else:
		for exp in cards:
			cards_copy = list(cards[exp])
			for card in cards_copy:
				if re.match(pattern, card['id']):
					cards[exp].remove(card)

def remove_card_ids(cards, cards_to_remove):
	for exp in cards:
		for exp in cards:
			cards_copy = list(cards[exp])
			for card in cards_copy:
				if card['id'] in cards_to_remove:
					cards[exp].remove(card)

def flatten_cards_dict(cards):
	cards_copy = {}
	for exp in cards:
		for card in cards[exp]:
			card_dict = dict(card)
			del card_dict['id']
			cards_copy[card['id']] = card_dict

	return cards_copy

def return_collectible_cards(inputfile):
	cards = json_file_to_dict(inputfile)
	remove_non_collectible_cards(cards)
	#cards = flatten_cards_dict(cards)

	return cards