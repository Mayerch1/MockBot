
import discord
from discord.ext import commands
from discord_slash import SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType

from util.verboseErrors import VerboseErrors
from lib.tinyConnector import TinyConnector



token = open('token.txt', 'r').read()


intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True

client = commands.Bot(command_prefix='!', intents=intents, description='Mocking any message for you', help_command=None)
slash = SlashCommand(client, sync_commands=True, override_type=True)


PREFIX_HELP = '```prefix <string>\n\n'\
             '\t• set - the command prefix for this bot\n```'


@client.event
async def on_slash_command_error(ctx, error):

    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.send('You do not have permission to execute this command')
    else:
        print(error)
        raise error


@slash.slash(name='help', description='show a help message')
async def get_help(ctx):

    embed = discord.Embed(title='Mockbot Help', description='Mock other users')

    embed.add_field(name='/help', value='show this message', inline=False)
    embed.add_field(name='/mock last', value='mock the last message in this chat', inline=False)
    embed.add_field(name='/mock user', value='mock the last message of the specified user', inline=False)
    embed.add_field(name='!mock', value='type this as a response message to a specific message', inline=False)
    embed.add_field(name='/automock', value='manage the auto-mock list', inline=False)

    embed.add_field(name='\u200b', value='If you like this bot, you can leave a vote at [top.gg](https://top.gg/bot/734829435844558999)', inline=False)

    # direct slash response is guaranteed to have permissions
    await ctx.send(embed=embed)
    




@client.event
async def on_ready():
    # debug log
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----------')
    await client.change_presence(activity=discord.Game(name='/mock last'))



@client.event
async def on_guild_remove(guild):
    TinyConnector._delete_guild(guild.id)



def main():
    client.load_extension(f'TopGGModule')
    client.load_extension(f'MockModule')
    client.load_extension(f'DiscordBotListModule')
    client.run(token)


if __name__ == '__main__':
    main()