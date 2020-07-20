import discord

from lib.tinyConnector import TinyConnector
from util.verboseErrors import VerboseErrors



async def ack_message(message: discord.Message):
    """Acknowledge the message to the user
    * DELETES the msg, when cleanup and when good permission
    * if not, add green-hook reaction, when good permission
    * if not, answer 'Ok'

    Args:
        message (discord.Message): message, could be deleted afterwards
    """

    server = TinyConnector.get_guild(message.guild.id)

    if VerboseErrors.can_react(message.channel):
        await message.add_reaction('✅') # green hook
    else:
        await message.channel.send('Ok')


