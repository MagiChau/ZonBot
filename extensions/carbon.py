import aiohttp
import asyncio
import checks
from discord.ext import commands
import config

class Carbon():
    CARBON_BOT_DATA_URL = "https://www.carbonitex.net/discord/data/botdata.php"

    def __init__(self, bot):
        self.bot = bot
        self.update_enabled = True
        bot.loop.create_task(self.update_servercount())

    @commands.command(name="carbon")
    @checks.is_owner()
    async def carbon_updates(self, enable: bool):
        if self.update_enabled:
            if enable:
                self.bot.say("Carbon Updates Already Enabled")
            else:
                self.bot.say("Carbon Updates Disabled")
        else:
            if enable:
                self.bot.say("Carbon Updates Enabled")
            else:
                self.bot.say("Carbon Updates Already Disabled")
        self.update_enabled = enable

    async def update_servercount(self):
        payload = {"key":config.carbon_key}
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            await asyncio.sleep(60*60)
            if self.update_enabled:
                payload["servercount"] = str(len(self.bot.servers))
                with aiohttp.ClientSession() as session:
                    async with session.post(Carbon.CARBON_BOT_DATA_URL, data=payload) as resp:
                        print(await resp.text())



def setup(bot):
    bot.add_cog(Carbon(bot))