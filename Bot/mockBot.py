import os
import logging
import discord

from pathlib import Path


logging.basicConfig(level=logging.INFO) # general 3rd party

handler = logging.FileHandler(filename='./logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

dc_logger = logging.getLogger('discord')
dc_logger.setLevel(logging.WARNING) # discord lib
log = logging.getLogger('MockBot')
log.setLevel(logging.DEBUG) # own code

dc_logger.addHandler(handler)
log.addHandler(handler)


token = os.getenv('BOT_TOKEN')
token: str = os.getenv('BOT_TOKEN')
intents = discord.Intents.none()
intents.guilds = True
intents.messages = True

bot: discord.AutoShardedBot = discord.AutoShardedBot(intents=intents)


###########
# Eevents 
###########

@bot.event
async def on_ready():
    log.info('Logged in as')
    log.info(bot.user)
    log.info(bot.user.id)
    log.info('----------------')


#############
# Commands
############


def main():
    for filename in os.listdir(Path(__file__).parent / 'cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

    bot.run(token)


if __name__ == '__main__':
    main()

