import checks
from discord.ext import commands
import discord
import re

class Invite():
    invite_regex_pattern = r'https?://discord((.gg/)|(app.com/invite/))[a-zA-Z0-9-]+'

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="join")
    async def accept_invite(self, invite : str):
        """Zonbot accepts an invite to a server

        Usage: !join <invite>
        """

        invite = invite.strip(' ')
        match = re.fullmatch(Invite.invite_regex_pattern, invite)
        if match:
            try:
                invite = await self.bot.get_invite(invite)
                if invite.server not in self.bot.servers:
                    await self.bot.accept_invite(invite)
                    await self.bot.say("Successfully joined server.\nZonBot's command prefix is !")
                else:
                    await self.bot.say( "Already in that server.")
            except (discord.HTTPException, discord.NotFound):
                await self.bot.say("Error joining server.")


    async def accept_private_invites(self, message):
        """On Message Event: Accepts PM invites"""

        if message.channel.is_private:
            invite = message.content.strip(' ')
            match = re.fullmatch(Invite.invite_regex_pattern, invite)
            if match:
                try:
                    invite = await self.bot.get_invite(invite)
                    if invite.server not in self.bot.servers:
                        await self.bot.accept_invite(invite)
                        await self.bot.send_message(message.channel, "Successfully joined server.\nZonBot's command prefix is !")
                    else:
                        await self.bot.send_message(message.channel, "Already in that server.")
                except (discord.HTTPException, discord.NotFound):
                    await self.bot.send_message(message.channel, "Error joining server.")

def setup(bot):
    invite = Invite(bot)
    bot.add_cog(invite)
    bot.add_listener(invite.accept_private_invites, 'on_message')