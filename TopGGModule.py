import os
import dbl
import discord
from discord.ext import commands



class TopGG(commands.Cog):

    def thread(self, name, app, host, port):
        serve(app, host=host, port=port)


    def __init__(self, client):
        self.client = client

        if os.path.exists('topGGToken.txt'):
            self.token = open('topGGToken.txt', 'r').readline()
            self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True)
            print('Started topGG server')

        else:
            print('Ignoring TopGG, no Token')



    @commands.Cog.listener()
    async def on_guild_post(self):
        print('Server count posted successfully')



def setup(client):
    client.add_cog(TopGG(client))