import asyncio
from discord.ext import commands
import checks
import discord

class Util():
    def __init__(self, bot):
        self.bot = bot

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
    bot.add_cog(Util(bot))