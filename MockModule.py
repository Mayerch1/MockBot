import os

import json

import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType


from lib.tinyConnector import TinyConnector
from consts import Consts
from util.verboseErrors import VerboseErrors

from lib.sponge_module import perform_sponge


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


    @cog_ext.cog_slash(name='automock', description='manage the auto-mocked users',
                            options=[
                                create_option(
                                    name='mode',
                                    description='select the manage mode',
                                    required=True,
                                    option_type=SlashCommandOptionType.STRING,
                                    choices=[
                                        create_choice(
                                            name='list',
                                            value='ls'
                                        ),
                                        create_choice(
                                            name='add',
                                            value='add'
                                        ),
                                        create_choice(
                                            name='remove',
                                            value='rm'
                                        )
                                    ]
                                ),
                                create_option(
                                    name='user',
                                    description='the user to add/remove from the list',
                                    required=False,
                                    option_type=SlashCommandOptionType.USER
                                )
                            ])
    @commands.cooldown(rate=15, per=60, type=commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def mock_manage_list(self, ctx, mode, user=None):

        error = False
        server = TinyConnector.get_guild(ctx.guild.id)

        if mode == 'ls':
            await ctx.defer(hidden=True)

            out_str = 'sponged users: \n\t\t• '
            # resolve all ids into mentions
            # mentions are hidden due to using a hidden slash command
            out_str += '\n\t• '.join(list(map(lambda x: f'<@{x}>', server.sponge_list)))

            await ctx.send(out_str, hidden=True)

        elif user:
            if mode == 'add':
                if user.id not in server.sponge_list:
                    server.sponge_list.append(user.id)
            elif mode == 'rm':
                if user.id in server.sponge_list:
                    server.sponge_list.remove(user.id)

            TinyConnector.update_guild(server)
            await ctx.send('list was updated', hidden=True)
        else:
            await ctx.send('the selected mode requires a user to be defined', hidden=True)


    @cog_ext.cog_subcommand(base='mock', name='user', description='mock the last message of a given user',
                            options=[
                                create_option(
                                    name='user',
                                    description='the target user to mock',
                                    required=True,
                                    option_type=SlashCommandOptionType.USER
                                )
                            ])
    @commands.cooldown(rate=15, per=60, type=commands.BucketType.user)
    @commands.max_concurrency(5, commands.BucketType.guild)
    @commands.guild_only()
    async def mock_user(self, ctx, user):

        server = TinyConnector.get_guild(ctx.guild.id)

        if ctx.author.id in server.sponge_list:
            await ctx.send('You\'re on the automock list and cannot use this feature', hidden=True)
            return  # user is blacklisted


        req_perms = discord.Permissions(manage_messages=True, attach_files=True, read_message_history=True)
        if not await VerboseErrors.show_missing_perms('mock', req_perms, ctx.channel):
            await ctx.send('missing permissions', hidden=True)
            return

        await ctx.defer(hidden=True)
        
        # permission is assured
        async for old_msg in ctx.channel.history(limit=250):
            # if uid of message is equals to mentioned user
            # in case of no arg: last message which is not the command
            if user == old_msg.author:

                success = await perform_sponge(old_msg, Consts.res_dir, Consts.mock_file)
                if success:
                    await ctx.send('ok', hidden=True) # close the interaction as success
                    await old_msg.delete() # delete permission is assured at function beginning

                return  # return on succes and failure

        await ctx.send('Could not find a message of the requested user', hidden=True)


    @cog_ext.cog_subcommand(base='mock', name='last', description='mock the last message')
    @commands.cooldown(rate=15, per=60, type=commands.BucketType.user)
    @commands.max_concurrency(5, commands.BucketType.guild)
    @commands.guild_only()
    async def mock_last(self, ctx):

        server = TinyConnector.get_guild(ctx.guild.id)

        if ctx.author.id in server.sponge_list:
            await ctx.send('You\'re on the automock list and cannot use this feature', hidden=True)
            return # user is blacklisted


        req_perms = discord.Permissions(manage_messages=True, attach_files=True, read_message_history=True)
        if not await VerboseErrors.show_missing_perms('mock', req_perms, ctx.channel):
            await ctx.send('missing permissions', hidden=True)
            return

        # needs deletion before iteration over history
        # otherwise the command request will be sponged
        await ctx.send('ok', hidden=True) # close the interaction

        # permission is assured
        async for old_msg in ctx.channel.history(limit=1):
            # if uid of message is equals to mentioned user
            # in case of no arg: last message which is not the command
            
            success = await perform_sponge(old_msg, Consts.res_dir, Consts.mock_file)
            if success:
                await old_msg.delete() # delete permission is assured at function beginning
            return

        await ctx.send('failed to access message history', hidden=True)
           

    @commands.command(name='mock', help='use this as response to a specific message')
    @commands.guild_only()
    @commands.cooldown(rate=15, per=60, type=commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def mock_response(self, cmd):
        
        server = TinyConnector.get_guild(cmd.guild.id)

        if cmd.author.id in server.sponge_list:
            return  # user is blacklisted


        req_perms = discord.Permissions(manage_messages=True, attach_files=True, read_message_history=True)
        if not await VerboseErrors.show_missing_perms('mock', req_perms, cmd.channel):
            await cmd.send('missing permissions', hidden=True)
            return

        # needs deletion before iteration over history
        # otherwise the command request will be sponged
        await cmd.message.delete()


        if cmd.message.reference:
           msg = cmd.message.reference
           if not msg.cached_message:
               channel = self.client.get_channel(msg.channel_id)
               msg = await channel.fetch_message(msg.message_id)
           else:
               msg = msg.cached_message
        else:
           return
    
        success = await perform_sponge(msg, Consts.res_dir, Consts.mock_file)
        if success:
            await msg.delete()


def setup(client):
    client.add_cog(MockModule(client))