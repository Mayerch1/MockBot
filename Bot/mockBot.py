import os
import sys
import logging
import traceback
import discord

from pathlib import Path
from discord.ext.servercount import ServerCount

from lib.tinyConnector import TinyConnector

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
intents.guilds = True # non-privileged, required for on_guild_remove (data deletion)

bot: discord.AutoShardedBot = discord.AutoShardedBot(intents=intents)


# ###########
# Methods
# ###########
async def log_exception(ctx: discord.ApplicationContext, error: Exception):
    
    if isinstance(error, discord.NotFound):
        log.warning('interaction timed out (not found)')
    else:
        t = (type(error), error, error.__traceback__)
        log.error(''.join(traceback.format_exception(*t)))


def cleanup_removed_guilds():
    """delete stored data of all guilds the bot is no longer part of
       catches removals which happened while the bot was offline

       only requires the (non-privileged) guilds intent
    """
    if bot.shard_ids is not None and bot.shard_count and len(bot.shard_ids) < bot.shard_count:
        # this process only knows the guilds of its own shards
        log.warning('process does not run all shards, skipping data cleanup')
        return

    joined = {g.id for g in bot.guilds} # includes unavailable guilds (outages)
    if not joined:
        # never wipe everything because of an empty/failed cache
        log.warning('guild cache is empty, skipping data cleanup')
        return

    for g_id in TinyConnector.get_guild_ids() - joined:
        TinyConnector.delete_guild(g_id)
        log.info(f'deleted data of removed guild {g_id}')


###########
# Eevents 
###########

@bot.event
async def on_ready():
    log.info('Logged in as')
    log.info(bot.user)
    log.info(bot.user.id)
    log.info('----------------')
    cleanup_removed_guilds()


@bot.event
async def on_guild_remove(guild: discord.Guild):
    TinyConnector.delete_guild(guild.id)
    log.info(f'removed from guild {guild.id}, deleted its data')


@bot.event
async def on_shard_connect(shard_id):
    log.debug(f'shard {shard_id} connected')


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: Exception):
    await log_exception(ctx, error)


@bot.event
async def on_error(event_method, *args, **kwargs):
    exc_info = sys.exc_info()
    log.critical('non-application error occurred', exc_info=exc_info)


#############
# Commands
############

def set_tokens():
    ServerCount.init(bot, 'mockBot (https://github.com/Mayerch1/MockBot)')
    ServerCount.set_token_dir('tokens')


def main():
    for filename in os.listdir(Path(__file__).parent / 'cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

    bot.load_extension('discord.ext.servercount.servercount')

    set_tokens()
    bot.run(token)


if __name__ == '__main__':
    main()

