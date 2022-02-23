import os
import logging
import discord

from pathlib import Path
from lib.tinyConnector import TinyConnector


logging.basicConfig(level=logging.INFO) # general 3rd party

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

dc_logger = logging.getLogger('discord')
dc_logger.setLevel(logging.WARNING) # discord lib
log = logging.getLogger('MockBot')
log.setLevel(logging.DEBUG) # own code

dc_logger.addHandler(handler)
log.addHandler(handler)

# from util.verboseErrors import VerboseErrors
#from lib.tinyConnector import TinyConnector


token = os.getenv('BOT_TOKEN')
token: str = os.getenv('BOT_TOKEN')
intents = discord.Intents.none()
intents.guilds = True
intents.messages = True

bot: discord.AutoShardedBot = discord.AutoShardedBot(intents=intents)


# ###########
# Methods
# ###########


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


# @bot.command(
#     type=interactions.ApplicationCommandType.MESSAGE,
#     name='Mock',
#     scope=140150091607441408
# )
# async def mock_ctx(ctx: interactions.ComponentContext):
#     messages = ctx.data.resolved.messages
#     if not messages:
#         await ctx.send('There was an issue locating your message', ephemeral=True)
#         return

#     ctx.send()
#     message = next(iter(messages.values()))
#     await mock.mock_message(ctx, message=message)


"""
@client.command(name='mock', description='mock command', scope=140150091607441408,
                options=[
                    interactions.Option(
                        name="last",
                        description="sub desc",
                        type=interactions.OptionType.SUB_COMMAND
                    ),
                    interactions.Option(
                        name="user",
                        description="take the last message of a user",
                        type=interactions.OptionType.SUB_COMMAND,
                        options=[
                            interactions.Option(
                                name='user',
                                description='the user to mock',
                                type=interactions.OptionType.USER,
                                required=True
                            )
                        ]
                    )
                ])
async def mock_last(ctx, sub_command, user=None):

    if sub_command == 'last':
        await mockModule.mock_last(ctx)
    elif sub_command == 'user':
        await mockModule.mock_user(ctx, user)


@client.command(name='automock', description='manage the auto-mocked users', scope=140150091607441408,
                options=[
                    interactions.Option(
                        name="add",
                        description="add a new user to the list",
                        type=interactions.OptionType.SUB_COMMAND,
                        options=[
                            interactions.Option(
                                name='user',
                                description='the user to add',
                                type=interactions.OptionType.USER,
                                required=True
                            )
                        ]
                    ),
                    interactions.Option(
                        name="remove",
                        description="remove a user from the list",
                        type=interactions.OptionType.SUB_COMMAND,
                        options=[
                            interactions.Option(
                                name='user',
                                description='the user to remove',
                                type=interactions.OptionType.USER,
                                required=True
                            )
                        ]
                    ),
                    interactions.Option(
                        name="list",
                        description="list all automocked users",
                        type=interactions.OptionType.SUB_COMMAND
                    )
                ])
async def automock(ctx, sub_command, user=None):
    await mockModule.mock_manage_list(ctx, sub_command, user)




@client.command(name='mock_message3', type=interactions.ApplicationCommandType.MESSAGE, scope=140150091607441408)
async def mock_message(ctx):
    await mockModule.mock_message(ctx)



@client.event
async def on_message_create(message):
    await mockModule.on_message(message)

"""


def main():
    for filename in os.listdir(Path(__file__).parent / 'cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

    bot.run(token)


if __name__ == '__main__':
    main()

