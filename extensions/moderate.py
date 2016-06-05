import asyncio
import checks
from discord.ext import commands
import discord

class Moderate():

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, hidden=True)
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

    @commands.command(pass_context=True, hidden=True)
    @checks.is_not_pvt_chan()
    @checks.can_manage_message()
    async def prune(self, ctx, name : str, amount : int=10):
        """Deletes messages of a specified user.
        By default 10 messages from recent history will be deleted.

        Usage: !prune <user> [amount]
        user: Person to prune
        amount: number of messages to delete
        """

        try:
            found = discord.utils.find(lambda m: name.lower() in m.display_name.lower(), ctx.message.server.members)
        except:
            found = None

        if found is None:
            found = discord.utils.find(lambda m: name == m.mention, ctx.message.server.members)

        if found is None:
            await self.bot.say("{} not found".format(name))
            return

        if not ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages:
            #await self.bot.say("Bot does not have permission to delete messages.")
            return

        delete_list = []
        async for msg in self.bot.logs_from(ctx.message.channel, limit=(amount*5)):
                if len(delete_list) == amount:
                    break
                if msg.author.id == found.id:
                    delete_list.append(msg)

        if len(delete_list) == 1:
            await self.bot.delete_message(delete_list[0])
        elif len(delete_list) >= 2:
            for i in range(len(delete_list)//100 + 1):
                await self.bot.delete_messages(delete_list[100*i:100*(i+1)])
                await asyncio.sleep(0.5)

def setup(bot):
    bot.add_cog(Moderate(bot))