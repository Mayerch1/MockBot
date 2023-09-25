import os
import json
import logging
import discord

from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum

from consts import Consts
from lib.tinyConnector import TinyConnector, MockStatus
from util.verboseErrors import VerboseErrors

from lib.sponge_module import perform_sponge

log = logging.getLogger('MockBot')

class MockModule(discord.Cog):

    ##################
    # Statics
    #################

    mock_group = discord.SlashCommandGroup('mock', 'Mock other users')

    class AutomockCool():
        def __init__(self):
            self.last_automock = None
            self.last_info_msg = None
            self.cnt = 0

    # =====================
    # internal functions
    # =====================
    def __init__(self, client: discord.AutoShardedBot):
        self.client: discord.AutoShardedBot = client
        self.auto_cool = defaultdict(lambda: defaultdict(MockModule.AutomockCool))


    def toggle_automock(self, member: discord.Member) -> MockStatus:

        g_id = str(member.guild.id)
        u_id = str(member.id)

        status = TinyConnector.get_member_status(g_id, u_id)

        # toggle the current user state
        if status == MockStatus.no_action:
            status = MockStatus.automock
        elif status == MockStatus.automock:
            status = MockStatus.no_action

        TinyConnector.set_member_status(g_id, u_id, status)
        return status


    async def automock_user(self, message: discord.Message):

        req_perms = discord.Permissions(send_messages=True, attach_files=True)
        if not VerboseErrors.has_permission(req_perms, message.channel):
            log.debug(f'missing permissions for automock')
            return

        await self.automock_info(message)
        await self.mock_message(None, message)


    async def mock_message(self, ctx: discord.ApplicationContext, message: discord.Message):
        """mocks the given message
           does not require any permissions to function

           if ctx is None, the message channel is used to send the response
           if permissions for 'manage_messages' are present, it will delete the old message

        Args:
            ctx (discord.ApplicationContext): context of interaction, can be None
            message (discord.Message): message to mock
        """

        # await ctx.defer()
        success = await perform_sponge(ctx, message, Consts.res_dir, Consts.mock_file)

        req_perms = discord.Permissions(manage_messages=True)
        if success and VerboseErrors.has_permission(req_perms, message.channel):
            await message.delete()
        elif not success and ctx:
            await ctx.respond('Failed to mock message', ephemeral=True)
        else:
            log.debug('skip message deletion, no permissions')


    # =====================
    # events functions
    # =====================


    @discord.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if 'custom_id' not in interaction.data:
            # we only care about buttons/selects here
            return

        # keep as strings, as dict is str anyway
        c_id = interaction.data['custom_id']
        if not c_id.startswith('optout'):
            return

        _, mode, g_id = c_id.split('_')
        u_id = interaction.user.id

        if mode == 'out':
            TinyConnector.set_member_status(g_id, u_id, MockStatus.blacklist)
            action_row = self._get_actionrow(g_id, opted_out=True)
        elif mode == 'in':
            TinyConnector.set_member_status(g_id, u_id, MockStatus.no_action)
            action_row = self._get_actionrow(g_id, opted_out=False)
        else:
            return

        await interaction.response.edit_message(view=action_row)


    @discord.Cog.listener()
    async def on_ready(self):
        log.info('MockModule loaded')

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.id == self.client.application_id:
            return # ignore own messages
        if not message.guild:
            return # ignore DMs and ephemeral messages

        status = TinyConnector.get_member_status(message.guild.id, message.author.id)

        if status == MockStatus.automock:
            await self.automock_user(message)


    # =====================
    # command functions
    # =====================

    @discord.commands.user_command(name='automock', description='toggle the automock status for this user')
    async def automock_context(self, ctx: discord.ApplicationContext, member: discord.Member):
        status = TinyConnector.get_member_status(member.guild.id, member.id)

        if status == MockStatus.no_action:
            action = 'add'
        else:
            action = 'remove'

        await self.mock_manage(ctx, action, member)



    @discord.commands.message_command(name='mock_message', description='mock the selected message')
    async def mock_context(self, ctx: discord.ApplicationContext, message: discord.Message):
        await self.mock_message(ctx, message)



    @mock_group.command(name='last', description='mock the last message in chat')
    async def mock_last(self, ctx: discord.ApplicationContext):

        #await ctx.defer(ephemeral=False) TODO: fix
        req_perms = discord.Permissions(view_channel=True, read_message_history=True)
        if not await VerboseErrors.show_missing_perms('mock user', req_perms, ctx.channel, text_alternative=ctx):
            return

        old_msgs = await ctx.channel.history(limit=1).flatten()
        if old_msgs:
            await self.mock_message(ctx, old_msgs[0])
        else:
            await ctx.respond('Failed to access message history', ephemeral=True)



    @mock_group.command(name='user', description='mock the last message of a user')
    async def mock_user(self, 
                        ctx: discord.ApplicationContext, 
                        user: discord.commands.Option(discord.Member)):
        
        # await ctx.defer(ephemeral=False) TODO: fix
        req_perms = discord.Permissions(view_channel=True, read_message_history=True)
        if not await VerboseErrors.show_missing_perms('mock user', req_perms, ctx.channel, text_alternative=ctx):
            return
  
        # permission is assured
        async for old_msg in ctx.channel.history(limit=250):
            # if uid of message is equals to mentioned user
            # in case of no arg: last message which is not the command
            if old_msg.author.id == int(user.id):
                await self.mock_message(ctx, old_msg)
                return

        await ctx.respond(f'cannot find any messages from {user.display_name}#{user.discriminator}')


    # =====================
    # automock functions
    # =====================


    def _get_actionrow(self, guild_id, opted_out=False):
        view = discord.ui.View(timeout=0.001)
        buttons = [
         
                discord.ui.Button(
                    style=discord.ButtonStyle.green,
                    label='Re-enable',
                    emoji='☑️',
                    custom_id='optout_in_'+str(guild_id),
                    disabled=(not opted_out)
                ),
                discord.ui.Button(
                    style=discord.ButtonStyle.danger,
                    label='Stop This',
                    emoji='⛔',
                    custom_id='optout_out_'+str(guild_id),
                    disabled=(opted_out)
                )
            ]
        for b in buttons:
            view.add_item(b)

        return view



    async def automock_info(self, message):
        """notify the user about the auto-mock feature
           to help reduce confusion when the bot is unknown
        """

        utcnow = datetime.utcnow()
        g_id = message.guild.id
        a_id = message.author.id

        info: MockModule.AutomockCool = self.auto_cool[g_id][a_id]

        # a long pause between automocks resets the counter
        # this removes info msgs on long pauses between automocks
        if info.last_automock and ((utcnow - info.last_automock) > timedelta(minutes=2)):
            info.cnt = 0

        # if the threashold for automocks has been hit without trigerring a reset
        # the info msg is send
        # if a info msg was send in recent time, the info msg can still be rejected
        no_info_msg_rate_limit = (not info.last_info_msg or (utcnow-info.last_info_msg) > timedelta(minutes=30))
        if info.cnt >= 4 and no_info_msg_rate_limit:
            info.last_info_msg = utcnow

            dm = await message.author.create_dm()
            try:
                eb = discord.Embed(title=f'Opt out for {message.guild.name}', 
                                description='An admin put you on the automock-list. This means I\'m `mocking` all your messages.\n'\
                                        'You can ask an admin to be taken off this list if you want to prevent this.\n\n'\
                                        'If you\'re an admin yourself, use `/automock` on the server to edit the list.\n\n'\
                                        'Use the buttons below, to prevent me from automatically modifying your messages. You can return at any point and re-enable this feature.\n'\
                                        'Note: this is set on a per-server base')

                # assume user is not opted-out
                # otherswise this method couldn't even be triggered in the first place
                action_row = self._get_actionrow(g_id, opted_out=False)
                await dm.send(embed = eb, view=action_row)

            except discord.errors.Forbidden as e:
                # assume interaction blocked
                # when this occurres
                TinyConnector.set_member_status(g_id, a_id, MockStatus.blacklist)

        # always increase cnt and update timestamp
        info.last_automock = utcnow
        info.cnt += 1


    async def mock_manage(self, ctx: discord.ApplicationContext, mode: str, user: discord.Member):

        if mode != 'list' and not user:
            await ctx.respond(f'You need to specify a member for this operation', ephemeral=True)
            return

        if user:
            status = TinyConnector.get_member_status(ctx.guild.id, user.id)
            if status == MockStatus.blacklist:
                await ctx.respond(f'The user has blocked this bot and cannot be managed', ephemeral=True)
                return
    
        # user guaranteed to be not None
        if mode == 'add':
            TinyConnector.set_member_status(ctx.guild.id, user.id, MockStatus.automock)
        elif mode == 'remove':
            TinyConnector.set_member_status(ctx.guild.id, user.id, MockStatus.no_action)


        # always print the list
        out_str = 'sponged users: \n\t• '
        # resolve all ids into mentions
        mocked_list = TinyConnector.get_mocked_users(ctx.guild.id)
        out_str += '\n\t• '.join(list(map(lambda x: f'<@{x}>', mocked_list)))

        await ctx.respond(out_str, ephemeral=True)


    # =====================
    # commands functions
    # =====================

    @mock_group.command(name='manage', description='manage the automocked users')
    async def mock_manage_cmd(self, 
                                ctx: discord.ApplicationContext, 
                                mode: discord.Option(str, 'Choose the mode', choices=['list', 'add', 'remove']), 
                                user: discord.Option(discord.Member, 'the member to add/remove')):
        await self.mock_manage(ctx, mode, user)



def setup(client):
    client.add_cog(MockModule(client))