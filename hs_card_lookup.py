import card
import sys
card_list = card.return_collectible_cards(sys.path[0] + "/cards.json")

def find_matches(query, min_match):
	result_list = []
	l_query = query.lower()

	for exp in card_list:
		for card in card_list[exp]:
			l_cardname = card['name'].lower()

			percent_match = 0.0

			search_words = {}

			for word in l_query.split(' '):
				search_words.update({word : {}})

			card_words = l_cardname.split(' ')

			for search_word in search_words:
				for card_word in card_words:
					match = 1 - (calc_levenshtein_distance(search_word, card_word) / max(len(search_word), len(card_word)))
					if search_word not in search_words.keys():
						search_words[search_word] = {card_word: { 'match' : match} }
					else:
						search_words[search_word].update( {card_word: { 'match' : match} } )

			for search_word in search_words:

				max_value_key = list(search_words[search_word].keys())[0]
				max_value = search_words[search_word][max_value_key]

				for card_word in search_words[search_word]:
					if search_words[search_word][card_word]['match'] > max_value['match']:
						max_value_key = card_word
						max_value = search_words[search_word][card_word]

				percent_test_string_match = len(max_value_key) / len(l_cardname.replace(" ", ""))
				percent_string_match = len(search_word) / len(l_query.replace(" ", ""))

				percent_match += percent_string_match * max_value['match'] * .75 + percent_test_string_match * max_value['match'] * .25

			if percent_match >= min_match:
				result_list.append([card, percent_match])

	return result_list

def calc_levenshtein_distance(s1,s2):
    if len(s1) < len(s2):
        return calc_levenshtein_distance(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]