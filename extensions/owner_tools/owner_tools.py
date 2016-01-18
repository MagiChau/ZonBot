from discord.ext import commands
import checks
import discord

class Loader():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='load', help="Loads an extension.")
    @checks.is_owner()
    async def load_extension(self, name : str):
        name = name.strip(' ')
        try:
            self.bot.load_extension("extensions.{}.{}".format(name, name))
            await self.bot.say("Successfully loaded extension {}".format(name))
        except Exception as e:
            await self.bot.say("Failed to load extension {}".format(name))
            print(e)

    @commands.command(name='unload', help='Unloads an extension.')
    @checks.is_owner()
    async def unload_extension(self, name : str):
        name = name.strip(' ')
        try:
            self.bot.unload_extension("extensions.{}.{}".format(name, name))
            await self.bot.say("Successfully unloaded extension {}".format(name))
        except:
            await self.bot.say("Failed to unload extension {}".format(name))

    @commands.command(name='eval', help="Evaluates code.")
    @checks.is_owner()
    async def eval(self, code : str):
        try:
            f = eval(code)
            if asyncio.iscoroutine(f):
                f = await f
        except Exception as e:
            f = e
        await self.bot.say("```py\n{}```".format(f))

    @commands.command(name='setstatus', help ="Changes bot game status.")
    @checks.is_owner()
    async def set_status(self, game : str):
        game = game.strip()
        await self.bot.change_status(discord.Game(name=game))

def setup(bot):
    bot.add_cog(Loader(bot))
