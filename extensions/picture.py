import asyncio
from discord.ext import commands
import checks
import discord
import json
import os
import random

class Picture():

    def __init__(self, bot):
        self.bot = bot
        self.picture_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/picture/")
        self.whitelist_path = os.path.join(self.picture_path + "whitelist.json")

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

    async def upload_picture(self, name, ctx):
        async with self.whitelist_lock:
            if not ctx.message.channel.is_private:
                if ctx.message.channel.id not in self.whitelist:
                    return

        dp = os.path.join(self.picture_path + "/{0}/".format(name))
        files = os.listdir(dp)
        if len(files) == 0:
            return
        fp = os.path.join(dp + files[random.randint(0, len(files) - 1)])
        with open(fp, 'rb') as f:
            try:
                await self.bot.upload(f)
            except discord.Forbidden:
                pass

    @commands.command(name="picture", pass_context=True)
    @checks.is_not_pvt_chan()
    @checks.can_manage_message()
    async def picture_toggle(self, ctx, enable : bool):
        """Enables/disable's bot ability to post pictures on a per channel basis.
        Requires manage messages permission.

        Usage: 
        !picture enable
        !picture disable
        """
        async with self.whitelist_lock:
            id = ctx.message.channel.id
            if enable:
                if id not in self.whitelist:
                    self.whitelist.append(id)
                    self._save_whitelist(self.whitelist)
                    await self.bot.say("Pictures Enabled")
                else:
                    await self.bot.say("Already Enabled")
            else:
                if id in self.whitelist:
                    self.whitelist.remove(id)
                    self._save_whitelist(self.whitelist)
                    await self.bot.say("Pictures Disabled")
                else:
                    await self.bot.say("Already Disabled")

    @commands.command(pass_context=True)
    async def awoo(self, ctx):
        """awoo"""

        await self.upload_picture("awoo", ctx)

    @commands.command(pass_context=True)
    async def baka(self, ctx):
        """baka baka"""

        await self.upload_picture("baka", ctx)

    @commands.command(pass_context=True)
    async def nobully(self, ctx):
        """No bullying allowed"""

        await self.upload_picture("nobully", ctx)

    @commands.command(pass_context=True)
    async def ohayou(self, ctx):
        """ohayou"""

        await self.upload_picture("ohayou", ctx)

    @commands.command(pass_context=True)
    async def sad(self, ctx):
        """Sad things are sad"""

        await self.upload_picture("sad", ctx)

def setup(bot):
    bot.add_cog(Picture(bot))