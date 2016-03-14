from discord.ext import commands
import discord
import os

class Picture():

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def awoo(self):
        """awoo"""

        fp = os.path.join(os.path.dirname(os.path.realpath(__file__)) + '/picture/awoo.jpg')
        with open(fp, 'rb') as f:
            try:
                await self.bot.upload(f)
            except discord.Forbidden:
                pass
                #await self.bot.say("Error: bot does not have permission to upload pictures.")

    @commands.command()
    async def baka(self):
        """Baka baka"""

        fp = os.path.join(os.path.dirname(os.path.realpath(__file__)) + '/picture/baka.jpg')
        with open(fp, 'rb') as f:
            try:
                await self.bot.upload(f)
            except discord.Forbidden:
                pass
                #await self.bot.say("Error: bot does not have permission to upload pictures.")

    @commands.command()
    async def nobully(self):
        """No bullying allowed"""

        fp = os.path.join(os.path.dirname(os.path.realpath(__file__)) + '/picture/nobully.jpg')
        with open(fp, 'rb') as f:
            try:
                await self.bot.upload(f)
            except discord.Forbidden:
                pass
                #await self.bot.say("Error: bot does not have permission to upload pictures.")

    @commands.command()
    async def sad(self):
        """Sad things are sad"""
        fp = os.path.join(os.path.dirname(os.path.realpath(__file__)) + '/picture/sad.jpg')
        with open(fp, 'rb') as f:
            try:
                await self.bot.upload(f)
            except discord.Forbidden:
                pass
                #await self.bot.say("Error: bot does not have permission to upload pictures.")

def setup(bot):
    bot.add_cog(Picture(bot))