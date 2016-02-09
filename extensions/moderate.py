import checks
from discord.ext import commands
import discord

class Moderate():

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def prunebot(self, ctx, num : int):
        """Deletes ZonBot's recent messages

        Usage: !prunebot <num>
        num: amount of messages to delete
        """

        count = 0

        if num < 0:
            return

        while count <= num:
            del_flag = False
            async for msg in self.bot.logs_from(ctx.message.channel, limit=100):
                if count == num:
                    break
                elif msg.author.id == self.bot.user.id:
                    count += 1
                    del_flag = True
                    await self.bot.delete_message(msg)

            if not del_flag: break

    @commands.command(pass_context=True)
    @checks.is_not_pvt_chan()
    @checks.can_manage_message()
    async def prune(self, ctx, name : str, amount : int=10):
        """Deletes messages of a specified user
        By default 10 messages from recent history will be deleted.

        Usage: !prune <user> [amount]
        user: Person to prune
        amount: number of messages to delete
        """

        try:
            found = discord.utils.find(lambda x: name.lower() in x.name.lower(), ctx.message.server.members)
        except:
            found = None

        if found is None:
            await self.bot.say("{} not found".format(name))
            return

        if not ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages:
            await self.bot.say("Bot does not have permission to delete messages.")
            return

        count = 0
        async for msg in self.bot.logs_from(ctx.message.channel, limit=(amount*10)):
                if count == amount:
                    return
                if msg.author.id == found.id:
                    count += 1
                    await self.bot.delete_message(msg)

def setup(bot):
    bot.add_cog(Moderate(bot))