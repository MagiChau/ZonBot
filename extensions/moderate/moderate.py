from discord.ext import commands

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
                    print("msg del")

            if not del_flag: break

def setup(bot):
    bot.add_cog(Moderate(bot))