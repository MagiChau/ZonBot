import asyncio
from discord.ext import commands
import checks
import discord

class Loader():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='load')
    @checks.is_owner()
    async def load_extension(self, ext : str):
        """Loads an extension
        Usage: !load <ext>
        """

        ext = ext.strip(' ')
        try:
            self.bot.load_extension("extensions.{}".format(ext))
            await self.bot.say("Successfully loaded extension {}".format(ext))
        except Exception as e:
            await self.bot.say("Failed to load extension {}".format(ext))
            print(e)

    @commands.command(name='unload')
    @checks.is_owner()
    async def unload_extension(self, ext : str):
        """Unloads an extension
        Usage: !unload <ext>
        """

        ext = ext.strip(' ')
        try:
            self.bot.unload_extension("extensions.{}".format(ext))
            await self.bot.say("Successfully unloaded extension {}".format(ext))
        except:
            await self.bot.say("Failed to unload extension {}".format(ext))

def setup(bot):
    bot.add_cog(Loader(bot))
