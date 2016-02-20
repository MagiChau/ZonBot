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

    @commands.command(name='eval', pass_context=True)
    @checks.is_owner()
    async def eval(self, ctx, *, code : str):
        """Evaluates code
        Usage: !eval <code>
        """

        try:
            f = eval(code)
            if asyncio.iscoroutine(f):
                f = await f
        except Exception as e:
            f = e
        try:
            await self.bot.say("```py\n{}```".format(f))
        except discord.errors.HTTPException:
            splits = int(len(f) / 2000)
            f = str(f)
            for i in range(0, splits):
                await self.bot.say(f[i*2000:(i*2000)+1999])

    @commands.command(name='setstatus', help ="Changes bot game status.")
    @checks.is_owner()
    async def set_status(self, *, game : str):
        game = game.strip()
        await self.bot.change_status(discord.Game(name=game))

    @commands.command()
    @checks.is_owner()
    async def logout(self):
        await self.bot.logout()

def setup(bot):
    bot.add_cog(Loader(bot))
