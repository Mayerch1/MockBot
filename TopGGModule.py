import os
import dbl
import web
import discord
from discord.ext import commands

import _thread

from flask import Flask, request
from waitress import serve

from consts import Consts
from lib.tinyConnector import TinyConnector

class TopGG(commands.Cog):

    app = Flask(__name__)
    user_votes = {}
    secret = None


    def thread(self, name, app, host, port):
        serve(app, host=host, port=port)


    def __init__(self, client):
        self.client = client

        """
        if os.path.exists('topGGSecret.txt'):
            TopGG.secret = open('topGGSecret.txt', 'r').readline()

            # port 2302 is routed to dev pc, while docker routes 9124->2302
            _thread.start_new_thread(self.thread, ('flask server', TopGG.app, '0.0.0.0', 2302))
            print('Started webhook')
        else:
            print('Ignoring Webhook, no Token')
        """
        
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