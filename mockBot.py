import os

import discord
from discord.ext import commands
from discord_slash.context import MenuContext
from discord_slash import cog_ext, SlashContext, SlashCommand, ComponentContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils import manage_components
from discord_slash.model import SlashCommandOptionType, ButtonStyle

from util.verboseErrors import VerboseErrors
from lib.tinyConnector import TinyConnector


token = os.getenv('BOT_TOKEN')
privacy_notice = open('privacy.txt').read()


intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True

client = commands.Bot(command_prefix='!', intents=intents, description='Mocking any message for you', help_command=None)
slash = SlashCommand(client, sync_commands=True)


PREFIX_HELP = '```prefix <string>\n\n'\
             '\t• set - the command prefix for this bot\n```'


@client.event
async def on_slash_command_error(ctx, error):

    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.send('You do not have permission to execute this command')
    elif isinstance(error, discord.ext.commands.errors.NoPrivateMessage):
        await ctx.send('This command is only to be used on servers')
    else:
        print(error)
        raise error


@slash.slash(name='help', description='show a help message')
async def get_help(ctx):

    def get_help_components():
            buttons = [
                manage_components.create_button(
                    style=ButtonStyle.URL,
                    label='Invite Me',
                    url='https://discord.com/api/oauth2/authorize?client_id=734829435844558999&permissions=274878015488&scope=bot%20applications.commands'
                ),
                manage_components.create_button(
                    style=ButtonStyle.URL,
                    label='Support Server',
                    url='https://discord.gg/Xpyb9DX3D6'
                ),
                manage_components.create_button(
                    style=ButtonStyle.gray,
                    label='Privacy',
                    custom_id='help_privacy'
                )
            ]
            row_1 = manage_components.create_actionrow(*buttons)
            return [row_1]

    embed = discord.Embed(title='Mockbot Help', description='Mock other users')

    embed.add_field(name='/help', value='show this message', inline=False)
    embed.add_field(name='*Context Menu*', value='right-click a chat-message to mock it')
    embed.add_field(name='/mock last', value='mock the last message in this chat', inline=False)
    embed.add_field(name='/mock user', value='mock the last message of the specified user', inline=False)
    embed.add_field(name='/automock', value='manage the auto-mock list', inline=False)

    embed.add_field(name='\u200b', value='If you like this bot, you can leave a vote at [top.gg](https://top.gg/bot/734829435844558999)', inline=False)

    # direct slash response is guaranteed to have permissions
    await ctx.send(embed=embed, components=get_help_components())


async def send_privacy_notice(ctx):
    await ctx.send(privacy_notice, hidden=True)


@client.event
async def on_ready():
    # debug log
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----------')
    await client.change_presence(activity=discord.Game(name='/mock last'))


@client.event
async def on_component(ctx: ComponentContext):

    if ctx.custom_id == 'help_privacy':
        await send_privacy_notice(ctx)



@client.event
async def on_guild_remove(guild):
    TinyConnector._delete_guild(guild.id)


def main():
    client.load_extension(f'MockModule')
    client.load_extension(f'ServerCountPost')
    client.run(token)


if __name__ == '__main__':
    main()