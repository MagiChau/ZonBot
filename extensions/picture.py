from discord.ext import commands
import discord
import os
import random

class Picture():

    def __init__(self, bot):
        self.bot = bot
        self.picture_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/picture/")

    async def upload_picture(self, name):
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

    @commands.command()
    async def awoo(self):
        """awoo"""

        await self.upload_picture("awoo")

    @commands.command()
    async def baka(self):
        """baka baka"""

        await self.upload_picture("baka")

    @commands.command()
    async def nobully(self):
        """No bullying allowed"""

        await self.upload_picture("nobully")

    @commands.command()
    async def ohayou(self):
        """ohayou"""

        await self.upload_picture("ohayou")

    @commands.command()
    async def sad(self):
        """Sad things are sad"""

        await self.upload_picture("sad")

def setup(bot):
    bot.add_cog(Picture(bot))