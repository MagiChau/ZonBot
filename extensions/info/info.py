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

    @info.command(name='user', pass_context=True)
    async def _user(self, ctx, user : str):
        msg = "No user found."
        found = None
        if re.fullmatch(r'<@[0-9]+>', user):
            if ctx.message.server is None:
                found = ctx.message.author if ctx.message.author.mention == user else None
            else:
                found = discord.utils.get(ctx.message.server.members, mention=user)
        elif re.fullmatch(r'[0-9]+', user):
            if ctx.message.server is None:
                found = ctx.message.author if ctx.message.author.id == user else None
            else:
                found = discord.utils.get(ctx.message.server.members, id=user)
        else:
            if ctx.message.server is None:
                found = ctx.message.author if user.lower() in ctx.message.author.name.lower() else None
            else:
                found = discord.utils.find(lambda m: user.lower() in m.name.lower(), ctx.message.server.members)

        if found:
            msg = "```User: {}\nID: {}\nAvatar: {}".format(found.name, found.id, found.avatar_url)
            if not hasattr(found, 'server'):
                msg += "```"
            else:
                roles_str = str()
                for role in found.roles:
                    role_name = role.name
                    if role_name.startswith('@'): 
                        role_name = role_name.replace('@', '@\u200B')
                    roles_str += role_name + ', '
                roles_str = roles_str[:-2] if roles_str[-2:] == ', ' else roles_str
                msg += "\nRoles: {}\nServer Join Date: {}/{}/{}```".format(roles_str, found.joined_at.month,
                    found.joined_at.day, found.joined_at.year)
        elif ctx.message.server is None:
            msg += " You can only use the command on yourself in a private channel."

        await self.bot.say(msg)

def setup(bot):
    bot.add_cog(Info(bot))