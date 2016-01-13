from discord.ext import commands

class Info():
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def info(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = "Bot created by ZonMachi.\nDeveloped using the discord.py library."
            msg += "\nCurrently connected to {} servers.".format(str(len(self.bot.servers)))
            await self.bot.say(msg)

    @info.command(name='channel', pass_context=True)
    async def _channel(self, ctx):
        if ctx.message.channel.is_private:
            msg = "```Channel ID: {}```".format(ctx.message.channel.id)
        else:
            msg = "```Channel Name: {}\nChannel ID: {}".format(ctx.message.channel.name, ctx.message.channel.id)
            msg += "\nServer Name: {}\nServer ID: {}```".format(ctx.message.server.name, ctx.message.server.id)
        await self.bot.say(msg)

def setup(bot):
    bot.add_cog(Info(bot))