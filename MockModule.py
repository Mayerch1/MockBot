import os

import json

import discord
from discord.ext import commands


from lib.tinyConnector import TinyConnector
from consts import Consts
from util.verboseErrors import VerboseErrors
from lib.sponge_module import perform_sponge
from util.interaction import ack_message


class MockModule(commands.Cog):


    SPM_HELP =  '```*mockmanage <mode>\n\n'\
                'available modes\n'\
                '\t• ls - list all users on the mock-list\n'\
                '\t• add <user..> -add the given user to the list \n'\
                '\t• rm <user..> - remove the given user from the list \n'\
                '\n'\
                '\t• remove - alias for rm\n'\
                '\t• list - alias for ls```'


    # =====================
    # internal functions
    # =====================
    def __init__(self, client):
        self.client = client

    # =====================
    # events functions
    # =====================
    @commands.Cog.listener()
    async def on_ready(self):
        print('MockModule loaded')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
 
        server = TinyConnector.get_guild(message.guild.id)

        if message.author.id in server.sponge_list:
            await perform_sponge(message, Consts.res_dir, Consts.mock_file)
            try:
                await message.delete()
            except discord.NotFound:
                print('msg of sp user already deleted by other command, no further action')
            except discord.Forbidden:
                print('No permissions to delete event-triggered sponge')


    # =====================
    # commands functions
    # =====================

    @commands.command(name='mockmanage', help='Set users onto perm-sponge list')
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def mock_manage(self, cmd, mode, *user_mentions: discord.Member):
        #print(mode)
        error = False
        server = TinyConnector.get_guild(cmd.guild.id)

        if mode == 'ls' or mode == 'list':
            out_str = 'sponged users: \n\t\t• '
            # resolve all client ids to Users
            # do not use mentions, to not alert the victims

            out_str += '\n\t\t• '.join(
                list(map(lambda x: self.client.get_user(x).name, server.sponge_list)))
            await cmd.send(out_str)

        elif mode == 'add' and user_mentions:
            for user in user_mentions:
                if user.id not in server.sponge_list:
                    server.sponge_list.append(user.id)
            TinyConnector.update_guild(server)

        elif mode == 'rm' or mode == 'remove' and user_mentions:
            for user in user_mentions:
                if user.id in server.sponge_list:
                    server.sponge_list.remove(user.id)
            TinyConnector.update_guild(server)

        else:
            await cmd.send(MockModule.SPM_HELP)
            error = True

        if not error:
            # this are the same permission as for the 'sp' command
            # managing the command does not make sense, if the cmd itself cannot be performed
            req_perms = discord.Permissions(attach_files=True, read_message_history=True, manage_messages=True)

            await VerboseErrors.show_missing_perms('mock', req_perms, cmd.channel, additional_info='This might be depending on the used channel')
            await ack_message(cmd.message)





    @commands.command(name='mock', help='Perform \'mock\' on a message')
    @commands.cooldown(rate=15, per=60, type=commands.BucketType.user)
    @commands.max_concurrency(10, commands.BucketType.guild)
    @commands.guild_only()
    async def mock(self, cmd, *user_mentions: discord.Member):


        server = TinyConnector.get_guild(cmd.guild.id)

        if cmd.author.id in server.sponge_list:
            return # user is blacklisted


        req_perms = discord.Permissions(manage_messages=True, attach_files=True, read_message_history=True)
        if not await VerboseErrors.show_missing_perms('mock', req_perms, cmd.channel):
            return

        # needs deletion before iteration over history
        # otherwise the command request will be sponged
        await cmd.message.delete() # permission assured



        # permission is assured
        async for old_msg in cmd.channel.history(limit=250):
            # if uid of message is equals to mentioned user
            # in case of no arg: last message which is not the command
            if not user_mentions or user_mentions[0] == old_msg.author:
                success = await perform_sponge(old_msg, Consts.res_dir, Consts.mock_file)
                if success:
                    await old_msg.delete() # delete permission is assured at function beginning

                return # return on succes and failure


        await cmd.send('Could not match the filter within the last 250 messages')


def setup(client):
    client.add_cog(MockModule(client))