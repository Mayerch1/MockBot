import os
import dbl
import discord
from discord.ext import commands, tasks




class TopGG(commands.Cog):

    def __init__(self, bot):

        if os.path.exists('topGGToken.txt'):
            self.bot = bot
            self.token = open('topGGToken.txt', 'r').readline()

            #self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True)
            self.dblpy = dbl.DBLClient(self.bot, self.token)
            print('Started topGG server')
            self.update_stats.start()

        else:
            print('Ignoring TopGG, no Token')
        
    def cog_unload(self):
        self.update_stats.cancel()

    @tasks.loop(minutes=30)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count."""
        await self.bot.wait_until_ready()
        try:
            server_count = len(self.bot.guilds)
            await self.dblpy.post_guild_count(server_count)
            print('Posted server count ({})'.format(server_count))
        except Exception as e:
            print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))



def setup(client):
    client.add_cog(TopGG(client))


