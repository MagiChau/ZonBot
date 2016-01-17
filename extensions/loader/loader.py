from discord.ext import commands
import checks

class Loader():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='load')
    @checks.is_owner()
    async def load_extension(self, name : str):
        name = name.strip(' ')
        try:
            self.bot.load_extension("extensions.{}.{}".format(name, name))
        except:
            await self.bot.say("Failed to load extension {}".format(name))
        await self.bot.say("Successfully loaded extension {}".format(name))

    @commands.command(name='unload')
    @checks.is_owner()
    async def unload_extension(self, name : str):
        name = name.strip(' ')
        try:
            self.bot.unload_extension("extensions.{}.{}".format(name, name))
        except:
            await self.bot.say("Failed to unload extension {}".format(name))
        await self.bot.say("Successfully unloaded extension {}".format(name))

def setup(bot):
    bot.add_cog(Loader(bot))