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
            msg = "```Channel: {}\nChannel ID: {}".format(ctx.message.channel.name, ctx.message.channel.id)
            msg += "\nServer: {}\nServer ID: {}```".format(ctx.message.server.name, ctx.message.server.id)
        await self.bot.say(msg)

    @info.command(name='server', pass_context=True)
    async def _server(self, ctx):
        try:
            s = ctx.message.server
            msg = "Server: {}\nID: {}\nOwner: {}\nRegion: {}\nMembers: {}\nIcon: {}".format(s.name, s.id,
                s.owner.name, s.region, str(len(s.members)), s.icon_url)
            await self.bot.say(msg)
        except AttributeError:
            await self.bot.say("Command cannot be used in private channels.")

def setup(bot):
    bot.add_cog(Info(bot))