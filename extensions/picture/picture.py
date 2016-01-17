from discord.ext import commands
import discord
import os

class Picture():

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def awoo(self):
        fp = os.path.join(os.path.dirname(os.path.realpath(__file__)) + '/awoo.jpg')
        with open(fp, 'rb') as f:
            try:
                await self.bot.upload(f)
            except discord.Forbidden:
                await self.bot.say("Error: bot does not have permission to upload pictures.")

    @commands.command()
    async def baka(self):
        fp = os.path.join(os.path.dirname(os.path.realpath(__file__)) + '/baka.jpg')
        with open(fp, 'rb') as f:
            try:
                await self.bot.upload(f)
            except discord.Forbidden:
                await self.bot.say("Error: bot does not have permission to upload pictures.")

    @commands.command()
    async def nobully(self):
        fp = os.path.join(os.path.dirname(os.path.realpath(__file__)) + '/nobully.jpg')
        with open(fp, 'rb') as f:
            try:
                await self.bot.upload(f)
            except discord.Forbidden:
                await self.bot.say("Error: bot does not have permission to upload pictures.")

    @commands.command()
    async def sad(self):
        fp = os.path.join(os.path.dirname(os.path.realpath(__file__)) + '/sad.jpg')
        with open(fp, 'rb') as f:
            try:
                await self.bot.upload(f)
            except discord.Forbidden:
                await self.bot.say("Error: bot does not have permission to upload pictures.")

def setup(bot):
    bot.add_cog(Picture(bot))