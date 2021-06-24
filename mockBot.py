
import discord
from discord.ext import commands
from discord_slash import SlashContext, SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType

from util.verboseErrors import VerboseErrors
from lib.tinyConnector import TinyConnector



token = open('token.txt', 'r').read()
client = commands.Bot(command_prefix='/', description='Mocking any message for you', help_command=None)
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




@client.command(name='help', help='Show this message')
async def get_help(cmd, *x):


    embed = discord.Embed(title='Mockbot Help', description='Mock other users')

    embed.add_field(name='/help', value='show this message', inline=False)
    embed.add_field(name='/mock last', value='mock the last message in this chat', inline=False)
    embed.add_field(name='/mock user', value='mock the last message of the specified user', inline=False)
    embed.add_field(name='/mock', value='use this as response to a specific message', inline=False)
    embed.add_field(name='/mock manage', value='manage the auto-mock list', inline=False)

    embed.add_field(name='\u200b', value='If you like this bot, you can leave a vote at [top.gg](https://top.gg/bot/734829435844558999)', inline=False)

    try:
        await cmd.send(embed=embed)
    except discord.errors.Forbidden:
        await cmd.send('```Mockbot Help Page\n'\
                    '\n'\
                    '/help          Shows this message\n'\
                    '/mock last     mock the last message in this chat\n'\
                    '/mock user     mock the last message of the specified user\n'\
                    '/mock          use as response to a specific message\n'\
                    '/mock manage   manage the auto-mock list```')





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