import aiohttp
import asyncio
from discord.ext import commands
import checks
import config
import copy
import discord
import os
import sqlite3
import sys
import time


class Twitch():
    TWITCH_API_BASE_URL = 'https://api.twitch.tv/kraken/'

    def __init__(self, bot):
        self.bot = bot

        self.database_path = os.path.join(sys.path[0] + "/extensions/twitch/streams.db")
        self.database_connection = self._init_database()
        self.streams = self._load_database()

        self.twitch_id = config.twitch_id
        self.headers = self._init_headers(self.twitch_id)

        self.streams_lock = asyncio.Lock()

        self.notifier_lock = asyncio.Lock()
        self.notifier_bg_task = bot.loop.create_task(self.notifier_task())
        self.notifier_enabled = True

    def __del__(self):
        self.database_connection.close()
        self.notifier_bg_task.cancel()

    def _init_headers(self, client_id):
        """Creates a header dict for Twitch.tv API and returns it"""

        headers = dict()
        headers.update({'Client-ID': client_id})
        headers.update({'version': 'Accept: application/vnd.twitchtv.v3+json'})
        return headers

    def _init_database(self):
        """Creates a stream database if it doesn't already exist and returns the connection"""

        conn = sqlite3.connect(self.database_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS streams (cid TEXT, stream TEXT, status INTEGER, PRIMARY KEY(cid, stream)) WITHOUT ROWID;")
        conn.commit()
        return conn

    def _load_database(self):
        """Loads data from a stream database into a dict and return the dict"""

        streams = dict()
        # load database values into streams dict
        for row in self.database_connection.execute("SELECT * FROM streams ORDER BY stream;"):
            cid = row[0]
            stream = row[1]
            status = bool(row[2])
            if stream in streams:
                streams[stream]['channels'].append(cid)
            else:
                streams[stream] = {'channels': [cid], 'status': status}
        return streams

    def _add_stream_database(self, channel_id, stream, status=False):
        """Adds a stream notifier to the database. Throws sqlite3.IntegrityError if stream is invalid"""

        row = (channel_id, stream, int(status))  # status converted since sqlite3 doesn't have booleans
        self.database_connection.execute("INSERT INTO streams VALUES(?,?,?);", row)
        self.database_connection.commit()

    def _del_stream_database(self, channel_id, stream):
        """Removes a stream notifier from the database. Raises exception if failed"""

        row = (channel_id, stream)  # status converted since sqlite3 doesn't have booleans
        self.database_connection.execute("DELETE FROM streams WHERE cid = ? AND stream = ?;", row)
        self.database_connection.commit()

    def _update_stream_status_database(self, stream, status):
        """Updates all rows in the streams database of one stream new values."""
        try:
            row = (int(status), stream)
            self.database_connection.execute("UPDATE streams SET status=? WHERE stream=?;", row)
            self.database_connection.commit()
        except Exception as e:
            print(e)
            print(stream)

    async def is_stream_valid(self, stream):
        """Returns if a twitch stream is valid. Returns None if there was an error connecting."""

        url = Twitch.TWITCH_API_BASE_URL + 'channels/' + stream
        try:
            response = await aiohttp.get(url, headers=self.headers)
            data = await response.json()
            response.release()
            if 'error' not in data:
                return True
        except:
            return None

        return False

    async def is_stream_online(self, stream):
        """Returns if a stream is online. Returns None if invalid stream or failed to connect."""

        if not (await self.is_stream_valid(stream)):
            return

        url = Twitch.TWITCH_API_BASE_URL + 'streams/' + stream

        try:
            async with aiohttp.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['stream'] is None:
                        return False
                    else:
                        return True
        except aiohttp.errors.ClientOSError:
            pass
        return None

    async def get_stream(self, stream):
        """Returns a stream's response dict. Returns None if any errors occurred. Returns false if offline."""

        url = Twitch.TWITCH_API_BASE_URL + 'streams/' + stream

        try:
            async with aiohttp.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['stream'] is None:
                        return False
                    else:
                        return data
        except Exception as e:
            print("Error Occurred for {}: {}.".format(stream, str(e)))
        return None

    def format_stream_notification(self, stream):
        """Takes a stream dict and returns a formatted message for Discord"""

        stream_data = stream['stream']
        channel_data = stream['stream']['channel']
        return "{0} is now playing {1}: {2} at <{3}>".format(channel_data['display_name'],
                                                             stream_data['game'], channel_data['status'],
                                                             channel_data['url'])

    @commands.group(pass_context=True, invoke_without_command=True)
    async def twitch(self, ctx, stream: str):
        """Do !help twitch for info
        Twitch.tv related commands

        Check A Twitch Stream Status:
        Usage: !twitch <stream>

        Using Twitch Commands
        Usage: !twitch <command> [parameter]
        """

        is_valid = await self.is_stream_valid(stream)

        if is_valid is None:
            await self.bot.say("Error connecting to twitch. Try again.")
            return
        elif is_valid is False:
            await self.bot.say("Invalid stream.")
            return

        stream_status = await self.get_stream(stream)

        if stream_status is None:
            await self.bot.say("Error connecting to twitch. Try again.")
        elif stream_status is False:
            await self.bot.say("{0} is currently offline.".format(stream))
        else:
            await self.bot.say(self.format_stream_notification(stream_status))

    @twitch.command(name="add", pass_context=True)
    async def twitch_add(self, ctx, stream: str):
        """Adds a Twitch stream to the notification list

        Usage: !twitch add <stream>
        stream: name of a non-banned Twitch stream e.g. summit1g
        """

        stream = stream.lower()
        is_valid = await self.is_stream_valid(stream)
        if is_valid is None:
            await self.bot.say("Error connecting to twitch. Try again.")
            return
        elif is_valid is False:
            await self.bot.say("Invalid stream.")
            return

        async with self.streams_lock:
            cid = ctx.message.channel.id

            if stream in self.streams:
                if cid in self.streams[stream]['channels']:
                    await self.bot.say(stream + " is already in the notification list.")
                    return
                else:
                    self.streams[stream]['channels'].append(cid)
            else:
                self.streams[stream] = {'channels': [cid], 'status': False}
        try:
            self._add_stream_database(ctx.message.channel.id, stream)
            await self.bot.say(stream + " added to the notification list.")
        except sqlite3.IntegrityError:
            print("Integrity Error: {} {}".format(stream, ctx.message.channel.id))
            await self.bot.say("Error adding stream to the database")

    @twitch.command(name="del", pass_context=True)
    async def twitch_del(self, ctx, stream: str):
        """Deletes a Twitch stream from the notification list

        Usage: !twitch del <stream>
        stream: name of a non-banned Twitch stream e.g. summit1g
        """

        stream = stream.lower()
        cid = ctx.message.channel.id

        async with self.streams_lock:
            if stream not in self.streams or cid not in self.streams[stream]['channels']:
                await self.bot.say(stream + " is not in the notification list.")
                return

            if len(self.streams[stream]['channels']) == 1:
                del self.streams[stream]
            else:
                self.streams[stream]['channels'].remove(cid)

        self._del_stream_database(cid, stream)
        await self.bot.say(stream + " removed from the notification list.")

    @twitch.command(name="list", pass_context=True)
    async def twitch_list(self, ctx):
        """Lists all streams for this channel and their status"""

        convert_boot = lambda b: "Online" if b == True else "Offline"

        cid = ctx.message.channel.id
        msg = "```"
        count = 0
        for stream in self.streams:
            if cid in self.streams[stream]['channels']:
                count += 1
                msg += "\n{0}: {1}".format(stream, convert_boot(self.streams[stream]['status']))
        msg += "```"

        if count == 0:
            await self.bot.say("No streams on the notification list for this channel")
            return

        await self.bot.say(msg)

    @commands.group(name="notifier")
    @checks.is_owner()
    async def _notifier(self):
        """Used to enable or disable the Twitch Notifier

        Usage: !notifier <command>
        """

        pass

    @_notifier.command()
    @checks.is_owner()
    async def enable(self):
        """Enables the Twitch Notifier"""

        async with self.notifier_lock:
            if not self.notifier_enabled:
                await self.bot.say("Twitch Notifier Enabled")
            elif self.notifier_enabled:
                await self.bot.say("Twitch Notifier Already Enabled")
            self.notifier_enabled = True

    @_notifier.command()
    @checks.is_owner()
    async def disable(self):
        """Disables the Twitch Notifier"""

        async with self.notifier_lock:
            if self.notifier_enabled:
                await self.bot.say("Twitch Notifier Disabled")
            elif not self.notifier_enabled:
                await self.bot.say("Twitch Notifier Already Disabled")
            self.notifier_enabled = False

    async def notifier_task(self):
        """Runs a Twitch Notifier background task."""
        await self.bot.wait_until_ready()
        start_time = time.time()
        while not self.bot.is_closed:
            async with self.notifier_lock:
                streams_copy = copy.deepcopy(self.streams)
                for stream in streams_copy:
                    data = await self.get_stream(stream)
                    try:
                        if data is None:
                            pass
                        elif data == False and self.streams[stream]['status']:
                            self.streams[stream]['status'] = False
                            self._update_stream_status_database(stream, False)
                        elif data and not self.streams[stream]['status']:
                            self.streams[stream]['status'] = True
                            self._update_stream_status_database(stream, True)
                            msg = self.format_stream_notification(data)
                            async with self.streams_lock:
                                for cid in self.streams[stream]['channels']:
                                    if self.notifier_enabled:
                                        try:
                                            await self.bot.send_message(discord.Object(cid), msg)
                                        except Exception as e:
                                            print(e)
                    except Exception as e:
                        print("Error Occurred In Notifier Task")
                        print(e)
                    #await asyncio.sleep(1)
                #total_time = time.time() - start_time
                #print("Notifier Loop Time: {}".format(total_time))
                #start_time = time.time()

def setup(bot):
    twitch = Twitch(bot)
    bot.add_cog(twitch)
