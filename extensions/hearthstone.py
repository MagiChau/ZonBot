import asyncio
import checks
from discord.ext import commands
import copy
from datetime import datetime
import json
import os
import requests
import sys

class Hearthstone():
    """Card searches through square brackets disabled by default"""

    def __init__(self, bot, lang="enUS", min_match=0.55):
        self.whitelist_path = os.path.join(sys.path[0] + "/extensions/hearthstone/whitelist.json")
        self.cards_path = os.path.join(sys.path[0] + "/extensions/hearthstone/cards.json")

        self.cards_url = "https://api.hearthstonejson.com/v1/latest/{}/cards.json".format(lang)

        self.bot = bot
        self.lang = lang
        self.min_match = min_match
        self.cards = self._set_cards()
        self._clean_cards_dict(self.cards)
        self.whitelist = self._set_whitelist()

        self.whitelist_lock = asyncio.Lock()

    def _set_whitelist(self):
        """Retrieves whitelist from a JSON file and return it. Empty list if file is not found."""

        whitelist = []
        try:
            file = open(self.whitelist_path, 'r', encoding='utf8')
            try:
                whitelist = json.loads(file.read())
            except ValueError:
                pass
        except FileNotFoundError:
            file = open(self.whitelist_path, 'w+', encoding='utf8')
        finally:
            file.close()
            self._save_whitelist(whitelist)
        return whitelist

    def _save_whitelist(self, whitelist):
        """Saves a whitelist to whitelist.json"""

        file = open(self.whitelist_path, 'w', encoding='utf8')
        json.dump(whitelist, file)
        file.close()

    @commands.command(name="hs", pass_context = True)
    @checks.is_not_pvt_chan()
    async def whitelist_toggle(self, ctx, enabled : bool):
        """!help hs for info
        Enables/Disables card lookup through "[query]\"
        Only enabled for the channel command is used in

        Usage:
        !hs enable
        !hs disable
        """

        async with self.whitelist_lock:
            id = ctx.message.channel.id
            if enabled:
                if id not in self.whitelist:
                    self.whitelist.append(id)
                    self._save_whitelist(self.whitelist)
                    await self.bot.say("Hearthstone Card Lookup Detection Enabled")
                else:
                    await self.bot.say("Already Enabled")
            else:
                if id in self.whitelist:
                    self.whitelist.remove(id)
                    self._save_whitelist(self.whitelist)
                    await self.bot.say("Hearthstone Card Lookup Detection Disabled")
                else:
                    await self.bot.say("Already Disabled")

    def _get_server_mod_time(self):
        """Retrieves last modified time from hsjson's server in seconds since the Epoch"""

        time = 0
        try:
            response = requests.head(self.cards_url)
            response.raise_for_status()
            time = response.headers['Last-Modified']
            time = datetime.strptime(time, "%a, %d %b %Y %X %Z").timestamp()
        except Exception as e:
            print(e)
        return time

    def _download_card_json(self):
        """Retrieves cards.json from hsjson and returns the dictionary"""

        cards = None
        try:
            response = requests.get(self.cards_url)
            response.raise_for_status()
            cards = response.json()
        except Exception as e:
            print(e)
        return cards

    def _load_card_json(self):
        """Loads cards.json from file and returns the dictionary"""

        file = open(self.cards_path, 'r', encoding='utf8')
        cards = json.loads(file.read())
        file.close()
        return cards

    def _save_card_json(self, cards):
        """Saves a cards dictionary to cards.json file"""

        file = open(self.cards_path, 'w', encoding='utf8')
        json.dump(cards, file)
        file.close()

    def _set_cards(self):
        """Retrieves the most up to date cards.json file and returns the dictionary.
        cards.json will be downloaded if there is no local file or it is out of date."""

        local_time = 0
        try:
            local_time = os.stat(self.cards_path).st_mtime
        except Exception as e:
            print(e)

        server_time = self._get_server_mod_time()

        if server_time > local_time:
            cards = self._download_card_json()
            self._save_card_json(cards)
        else:
            cards = self._load_card_json()

        return cards

    def _clean_cards_dict(self, cards, unwanted_sets=None):
        """Formats cards dict to remove unwanted cards and reformat text"""

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
        """Takes a card dict and format its fields"""

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
                text = text[:pos] + "\*" + text[pos+1] + "\*" + text[pos+2:] #backslashes escapes markdown italics
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


    async def _find_card(self, query, min_match, break_threshold=0.85):
        """Retrieves the best matching card. Returns None if no card found"""

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
                if percent_match > break_threshold:
                    break

        if len(results) < 1:
            return
        else:
            results.sort(key=lambda r: r[1], reverse=True)

            def detect_tokens(lst):
                #detects if card has tokens with the same name and return main card
                #e.g. Druid of the Claw
                pass

            #guarantees exact matches are always returned. Edge case: mortal coil and mortal strike
            for index, result in enumerate(results):
                if result[0]['name'].lower() == query: return results[index][0]

            return results[0][0]

    def discord_card_message(self, card):
        """Formats a card into a string for a discord message"""

        name = card['name']
        type = card['type']
        cost = " Cost: {}".format(card['cost'])

        if type == CardType.MINION: stats = " {}/{}".format(card['attack'], card['health'])
        elif type == CardType.SPELL: stats = ""
        elif type == CardType.WEAPON: stats = " {}/{}".format(card['attack'], card['durability'])

        rarity= "{} ".format(card['rarity']) if 'rarity' in card else ""
        pclass = " - {}".format(card['playerClass']) if 'playerClass' in card else ""
        race = " {}".format(card['race']) if 'race' in card else ""
        cset = " - {}".format(card['set'])
        text = card['text'] if 'text' in card else ""
        if 'flavor' in card:
            flavor = " - {}".format(card['flavor']) if len(text) > 0 else card['flavor']
        else:
            flavor = ""
        output = """[{name}]: {rarity}{type} {stats}{cost}{pclass}{race}{cset}\n{text}{flavor}"""
        return output.format(name=name, rarity=rarity.title(), type=type.title(),
                             stats=stats, cost=cost, pclass=pclass, race=race.title(), cset=cset,
                             text=text, flavor=flavor)

    @commands.command()
    async def card(self, query : str):
        """Searches for a card

        Usage: !card <query>
        """

        query = query.strip(' ')
        match = await self._find_card(query, self.min_match)
        if match:
            await self.bot.say(self.discord_card_message(match))
        else:
            await self.bot.say("Card not found.")

    async def scan_card_queries(self, message, delimiters=['[',']']):
        """on_message event that parses for queries within delimiters and display cards"""

        if message.author.id == self.bot.user.id:
            return
        with (await self.whitelist_lock):
            if not message.channel.is_private:
                if message.channel.id not in self.whitelist:
                    return
        msg = message.content
        if '`' in msg: return

        #adds all text contained in the delimiters to the queries list
        queries = []
        index = 0
        msg_len = len(msg)
        while index != -1:
            index = msg.find(delimiters[0], index, msg_len)
            close_index = msg.find(delimiters[1], index, msg_len)

            if (index == -1 or close_index == -1):
                break

            queries.append(msg[index+1:close_index])
            index = close_index + 1
        output = ""
        for query in queries:
            card = await self._find_card(query, self.min_match)

            if card:
                data = self.discord_card_message(card)
                output = "{0}{1}\n".format(output, data)

        output = output[:-1] if output[-1:] == "\n" else output

        if len(output) > 0:
            await self.bot.send_message(message.channel, output)

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
    hs = Hearthstone(bot)
    bot.add_cog(hs)
    bot.add_listener(hs.scan_card_queries, "on_message")

