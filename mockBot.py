
import discord
from discord.ext import commands
from discord_slash import SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType

from util.verboseErrors import VerboseErrors
from lib.tinyConnector import TinyConnector



token = open('token.txt', 'r').read()
client = commands.Bot(command_prefix='/', description='Mocking any message for you')
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
    client.run(token)


if __name__ == '__main__':
    main()