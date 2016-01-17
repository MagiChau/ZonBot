from discord.ext import commands
import time

class Info():
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, help="Displays various information.")
    async def info(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = "Bot created by ZonMachi.\nDeveloped using the discord.py library."
            msg += "\nCurrently connected to {} servers.".format(str(len(self.bot.servers)))
            await self.bot.say(msg)

    @info.command(name='channel', pass_context=True, help="Lists information about a channel.")
    async def _channel(self, ctx):
        if ctx.message.channel.is_private:
            msg = "```Channel ID: {}```".format(ctx.message.channel.id)
        else:
            msg = "```Channel: {}\nChannel ID: {}".format(ctx.message.channel.name, ctx.message.channel.id)
            msg += "\nServer: {}\nServer ID: {}```".format(ctx.message.server.name, ctx.message.server.id)
        await self.bot.say(msg)

    @info.command(name='server', pass_context=True, help = "Lists information about a server.")
    async def _server(self, ctx):
        try:
            s = ctx.message.server
            msg = "Server: {}\nID: {}\nOwner: {}\nRegion: {}\nMembers: {}\nIcon: {}".format(s.name, s.id,
                s.owner.name, s.region, str(len(s.members)), s.icon_url)
            await self.bot.say(msg)
        except AttributeError:
            await self.bot.say("Command cannot be used in private channels.")

    @info.command(name='user', pass_context=True, help="Lists information about a user.")
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

    @commands.command(help="States bot total running time.")
    async def uptime(self):
        seconds = int(time.time() - self.bot.start_time)
        minutes = seconds // 60
        seconds -= minutes * 60
        hours = minutes // 60
        minutes -= hours * 60
        days = hours // 24
        hours -= days * 24

        #takes a numerical time and what it corresponds to e.g. hours and return a string
        def parse_time(time, time_type):
            if time > 1:
                return ' ' + str(time) + ' ' + time_type
            elif time == 1:
                return ' ' + str(time) + ' ' + time_type[:-1]
            else:
                return ''

        seconds = parse_time(seconds, 'seconds')
        minutes = parse_time(minutes, 'minutes')
        hours = parse_time(hours, 'hours')
        days = parse_time(days, 'days')

        output = "ZonBot has been up for{}{}{}{}".format(days, hours, minutes, seconds)
        await self.bot.say(output)

def setup(bot):
    bot.add_cog(Info(bot))