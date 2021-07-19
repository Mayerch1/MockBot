import os
import json
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils import manage_components
from discord_slash.model import SlashCommandOptionType, ButtonStyle

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

    class AutomockCool():
        def __init__(self):
            self.last_automock = None
            self.last_info_msg = None
            self.cnt = 0

    # =====================
    # internal functions
    # =====================
    def __init__(self, client):
        self.client = client
        self.automock = {}


    def set_bot_block(self, g_id, u_id, block=True):
        
        server = TinyConnector.get_guild(g_id)

        g_id = str(g_id)
        u_id = str(u_id)

        if block:
            if g_id not in server.black_list:
                server.black_list[g_id] = {}
            server.black_list[g_id][u_id] = 1

        else:
            if u_id in server.black_list[g_id]:
                del server.black_list[g_id][u_id]
        
        TinyConnector.update_guild(server)


    async def automock_info(self, member):
        """notify the user about the auto-mock feature
           to help reduce confusion when the bot is unknown
        """

        utcnow = datetime.utcnow()
        g_id = member.guild.id
        m_id = member.id

        if g_id not in self.automock:
            self.automock[g_id] = {}
        servermock = self.automock[g_id]

        if m_id not in servermock:
            servermock[m_id] = MockModule.AutomockCool()

        info = servermock[m_id]

        # a long pause between automocks resets the counter
        # this removes info msgs on long pauses between automocks
        if info.last_automock and ((utcnow - info.last_automock) > timedelta(minutes=2)):
            info.cnt = 0

        # if the threashold for automocks has been hit without trigerring a reset
        # the info msg is send
        # if a info msg was send in recent time, the info msg can still be rejected
        if info.cnt >= 5 and (not info.last_info_msg or (utcnow - info.last_info_msg) > timedelta(minutes=15)):
            info.last_info_msg = utcnow

            buttons = [
                manage_components.create_button(
                    style=ButtonStyle.green,
                    label='Re-enable',
                    emoji='☑️',
                    custom_id=str(g_id)+'_enable'
                ),
                manage_components.create_button(
                    style=ButtonStyle.danger,
                    label='Stop This',
                    emoji='⛔',
                    custom_id=str(g_id)+'_disable'
                )
            ]
            action_row = manage_components.create_actionrow(*buttons)

            dm = await member.create_dm()
            try:
                await dm.send('An admin put you on the automock-list. This means I\'m `mocking` all your messages.\n'\
                               'You can ask an admin to be taken off this list if you want to prevent this.\n\n'\
                               'If you\'re an admin yourself, use `/automock` on the server to edit the list.\n\n'\
                               'Alternatively you can disable the blocking feature for you on this server or block me'\
                               ' using the discord functionality. You can return at any point and re-enable this feature\n'\
                               'Note: this is set on a per-server base',
                               components=[action_row])

            except discord.errors.Forbidden as e:
                # assume interaction blocked
                # when this occurres
                self.set_bot_block(g_id, m_id, True)

        # always increase cnt and update timestamp
        info.last_automock = utcnow
        info.cnt += 1

    # =====================
    # events functions
    # =====================

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):

        # keep as strings, as dict is str anyway
        g_id, mode = ctx.component_id.split('_')
        m_id = str(ctx.author_id)

        if mode == 'disable':
            self.set_bot_block(g_id, m_id, True)
        elif mode == 'enable':
            self.set_bot_block(g_id, m_id, False)
        else:
            return

        await ctx.defer(edit_origin=True)

    @commands.Cog.listener()
    async def on_ready(self):
        print('MockModule loaded')


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        g_id = message.guild.id
 
        server = TinyConnector.get_guild(g_id)

        # do not trigger if user has the bot blacklisted
        if message.author.id in server.sponge_list and\
           str(message.author.id) not in server.black_list.get(str(g_id), {}):

            success = await perform_sponge(message, Consts.res_dir, Consts.mock_file)

            if not success:
                print('failed to apply automock')
                return

            try:
                await message.delete()
            except discord.NotFound:
                print('msg of sp user already deleted by other command, no further action')
            except discord.Forbidden:
                print('No permissions to delete event-triggered sponge')

            await self.automock_info(message.author)


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
    @commands.guild_only()
    async def mock_user(self, ctx, user):

        server = TinyConnector.get_guild(ctx.guild.id)

        if ctx.author.id in server.sponge_list:
            await ctx.send('You\'re on the automock list and cannot use this feature', hidden=True)
            return  # user is blacklisted


        req_perms = discord.Permissions(manage_messages=True, attach_files=True, read_message_history=True)
        if not await VerboseErrors.show_missing_perms('mock user', req_perms, ctx.channel, text_alternative=ctx):
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
    @commands.guild_only()
    async def mock_last(self, ctx):

        server = TinyConnector.get_guild(ctx.guild.id)

        if ctx.author.id in server.sponge_list:
            await ctx.send('You\'re on the automock list and cannot use this feature', hidden=True)
            return # user is blacklisted


        req_perms = discord.Permissions(manage_messages=True, attach_files=True, read_message_history=True)
        if not await VerboseErrors.show_missing_perms('mock last', req_perms, ctx.channel, text_alternative=ctx):
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
    async def mock_response(self, cmd):

        if not cmd.message.reference:
            return
        
        server = TinyConnector.get_guild(cmd.guild.id)

        if cmd.author.id in server.sponge_list:
            return  # user is blacklisted

        req_perms = discord.Permissions(manage_messages=True, attach_files=True, read_message_history=True)
        if not await VerboseErrors.show_missing_perms('mock [as response]', req_perms, cmd.channel):
            await cmd.send('missing permissions', hidden=True)
            return

        # needs deletion before iteration over history
        # otherwise the command request will be sponged
        await cmd.message.delete()

        msg = cmd.message.reference  # guaranteed to be set
        if not msg.cached_message:
            channel = self.client.get_channel(msg.channel_id)
            msg = await channel.fetch_message(msg.message_id)
        else:
            msg = msg.cached_message

        success = await perform_sponge(msg, Consts.res_dir, Consts.mock_file)
        if success:
            await msg.delete()


def setup(client):
    client.add_cog(MockModule(client))
