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
            async for msg in self.logs_from(ctx.message.channel):
                if count == num:
                    break
                elif ctx.message.author.id == self.bot.user.id:
                    count += 1
                    del_flag = True
                    await self.bot.delete_message(msg)

            if not del_flag: break