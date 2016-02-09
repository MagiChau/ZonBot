from discord.ext import commands
import config

def is_owner():
    def predicate(ctx):
        return ctx.message.author.id == config.owner_id
    return commands.check(predicate)

def is_not_pvt_chan():
    def predicate(ctx):
        return not ctx.message.channel.is_private
    return commands.check(predicate)

def can_manage_message():
    def predicate(ctx):
        try:
            return ctx.message.channel.permissions_for(ctx.message.author).manage_messages
        except:
            return False
    return commands.check(predicate)
