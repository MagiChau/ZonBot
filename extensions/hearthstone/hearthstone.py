from discord.ext import commands
import copy
import json
import requests
import time

class Hearthstone():

    def __init__(self, bot, lang="enUS", min_match=0.5):
        self.bot = bot
        self.lang = lang
        self.min_match = min_match
        self.cards = None
        self.cards = self._get_card_json()
        self._clean_cards_dict(self.cards)

    def _get_card_json(self, max_attempts=10):
        request_url = "https://api.hearthstonejson.com/v1/latest/{}/cards.json".format(self.lang)
        cards = None
        attempts = 0
        while cards is None and attempts <= max_attempts:
            try:
                response = requests.get(request_url)
                response.raise_for_status()
                cards = response.json()
            except Exception as e:
                print(e)
        return cards

    def _clean_cards_dict(self, cards, unwanted_sets=None):
        cards_copy = copy.deepcopy(cards)
        if unwanted_sets is None:
            unwanted_sets = [CardSet.CHEAT, CardSet.CREDITS, CardSet.HERO_SKINS, 
            CardSet.MISSIONS, CardSet.NONE, CardSet.TAVERNBRAWL]
        for card in cards_copy:
            type = card['type']
            set = card['set']
            if set in unwanted_sets:
                cards.remove(card)
            elif type not in [CardType.MINION, CardType.SPELL, CardType.WEAPON]:
                cards.remove(card)
        for card in cards:
            self._format_card(card)

    def _format_card(self, card):
        def replace_html_tag(text, tag, replace):
            start_tag = "<{}>".format(tag)
            end_tag = "</{}>".format(tag)

            text = text.replace(start_tag, replace)
            text = text.replace(end_tag, replace)

            return text

        def replace_spell_power_char(text):
            char = '$'
            pos = text.find(char)
            while pos != -1:
                text = text[:pos] + "\*" + text[pos+1:pos+2] + "\* " + text[pos+3:]
                pos = text.find(char)
            return text

        if 'text' in card:
            text = card['text']
            text = replace_spell_power_char(text)
            text = replace_html_tag(text, 'b', '**')
            text = replace_html_tag(text, 'i', '*')
            text = text.replace('\n', ' ')
            card['text'] = text
        if 'flavor' in card:
            text = card['flavor']
            text = replace_html_tag(text, 'b', '**')
            text = replace_html_tag(text, 'i', '*')
            text = text.replace('\n', ' ')
            card['flavor'] = text
        if card['type'] == CardType.MINION:
            if 'playerClass' not in card and 'collectible' in card:
                card['playerClass'] = 'Neutral'
        if 'playerClass' in card:
            card['playerClass'] = card['playerClass'].title()
        if 'set' in card:
            cset = card['set']
            if cset == CardSet.BASIC:
                card['set'] = 'Basic'
            elif cset == CardSet.CLASSIC:
                card['set'] = 'Classic'


    async def _find_card(self, query, min_match):
        def calc_levenshtein_distance(s1, s2):
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

        results = []
        query = query.strip(' ').lower()
        if len(query) < 1:
            return
        for card in self.cards:
            name = card['name'].lower()

            percent_match = 0.0

            search_words = {}

            for word in query.split(' '):
                search_words.update({word : {}})

            card_words = name.split(' ')

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

                percent_test_string_match = len(max_value_key) / len(name.replace(" ", ""))
                percent_string_match = len(search_word) / len(query.replace(" ", ""))

                percent_match += percent_string_match * max_value['match'] * .75 + percent_test_string_match * max_value['match'] * .25

            if percent_match >= min_match:
                results.append([card, percent_match])

        if len(results) < 1:
            return
        else:
            results.sort(key=lambda r: r[1], reverse=True)
            return results[0][0]

    def discord_card_message(self, card):
        name = card['name']
        type = card['type']
        cost = " Cost: {}".format(card['cost'])

        if type == CardType.MINION: stats = " {}/{}".format(card['attack'], card['health'])
        elif type == CardType.SPELL: stats = ""
        elif type == CardType.WEAPON: stats = " {}/{}".format(card['attack'], card['durability'])

        pclass = " - {}".format(card['playerClass']) if 'playerClass' in card else ""
        cset = " - {}".format(card['set'])
        text = card['text'] if 'text' in card else ""
        if 'flavor' in card:
            flavor = " - {}".format(card['flavor']) if len(text) > 0 else card['flavor']
        else:
            flavor = ""
        return "[{name}]:{stats}{cost}{pclass}{cset}\n{text}{flavor}".format(name=name, stats=stats, cost=cost,
            pclass=pclass, cset=cset, text=text, flavor=flavor)



    @commands.command()
    async def card(self, query : str):
        query = query.strip(' ')
        match = await self._find_card(query, self.min_match)
        if match:
            await self.bot.say(self.discord_card_message(match))
        else:
            await self.bot.say("Card not found.")

class CardType():
    MINION = "MINION"
    SPELL = "SPELL"
    WEAPON = "WEAPON"

class CardSet():
    BASIC = "CORE"
    BRM = "BRM"
    CLASSIC = "EXPERT1"
    CHEAT = "CHEAT"
    CREDITS = "CREDITS"
    GVG = "GVG"
    HERO_SKINS = "HERO_SKINS"
    LOE = "LOE"
    MISSIONS = "MISSIONS"
    NAXX = "NAXX"
    NONE = "NONE"
    PROMO = "PROMO"
    REWARD = "REWARD"
    TAVERNBRAWL = "TB"
    TGT = "TGT"

def setup(bot):
    start_time = time.time()
    bot.add_cog(Hearthstone(bot))
    print("Setup time: " + str(time.time() - start_time))

