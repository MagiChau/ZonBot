from discord.ext import commands
import re

class Invite():

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join", help="Accepts an invite to a Discord server.")
    async def accept_invite(self, invite : str):
        invite = invite.strip(' ')
        try:
            invite = await self.box.get_invite(invite)
            if invite.server not in self.bot.servers:
                await self.bot.accept_invite(invite)
            else:
                await self.bot.say("Already in that server.")
        except (discord.HTTPException, discord.NotFound):
            await self.bot.say("Error joining server.")

    async def accept_carbon_invites(self, message):
        if message.channel.is_private and message.author.id == "90897174145044480":
            invite = message.content.strip(' ')
            regex_pattern = r'https?://discord((.gg/)|(app.com/invite/))[a-zA-Z0-9]+'
            match = re.fullmatch(regex_pattern, invite)
            if match:
                try:
                    invite = await self.box.get_invite(invite)
                    if invite.server not in self.bot.servers:
                        await self.bot.accept_invite(invite)
                    else:
                        await self.bot.say("Already in that server.")
                except (discord.HTTPException, discord.NotFound):
                    await self.bot.say("Error joining server.")

def setup(bot):
    invite = Invite(bot)
    bot.add_cog(invite)
    bot.add_listener(invite.accept_carbon_invites, 'on_message')