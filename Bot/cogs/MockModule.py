import logging
import discord

from consts import Consts
from lib.tinyConnector import TinyConnector

from lib.sponge_module import perform_sponge

log = logging.getLogger('MockBot')

class MockModule(discord.Cog):

    ##################
    # Statics
    #################

    mock_group = discord.SlashCommandGroup('mock', 'Mock other users')

    # =====================
    # internal functions
    # =====================
    def __init__(self, client: discord.AutoShardedBot):
        self.client: discord.AutoShardedBot = client


    async def mock_message(self, ctx: discord.ApplicationContext, message: discord.Message):
        """mocks the given message and responds to the interaction

           if permissions for 'manage_messages' are present and the guild
           has message deletion enabled (see /settings), it will delete the old message

           only uses interaction data (guild id, app permissions),
           therefore no gateway intents are required

        Args:
            ctx (discord.ApplicationContext): context of interaction
            message (discord.Message): message to mock
        """

        # await ctx.defer()
        success = await perform_sponge(ctx, message, Consts.res_dir, Consts.mock_file)

        if not success:
            await ctx.respond('Failed to mock message', ephemeral=True)
            return

        if not ctx.guild_id or not TinyConnector.get_delete_on_mock(ctx.guild_id):
            log.debug('skip message deletion, disabled by guild settings')
            return

        # app_permissions are the bot permissions in this channel (incl. overwrites)
        if ctx.app_permissions.manage_messages:
            await message.delete()
        else:
            log.debug('skip message deletion, no permissions')


    @staticmethod
    def get_usage_embed() -> discord.Embed:
        """explain how to use the message context menu,
           which is the only way to mock a message without the message content intent
        """
        eb = discord.Embed(title='How to mock a message',
                           description='Mocking now works directly on the message you want to mock:\n\n'
                                       '**Desktop / Web**\n'
                                       '1. Right-click the message\n'
                                       '2. Open `Apps`\n'
                                       '3. Click `mock_message`\n\n'
                                       '**Mobile**\n'
                                       '1. Long-press the message\n'
                                       '2. Open `Apps`\n'
                                       '3. Tap `mock_message`')
        eb.set_footer(text='Server admins can choose whether the original message is deleted with /settings')
        return eb


    # =====================
    # events functions
    # =====================

    @discord.Cog.listener()
    async def on_ready(self):
        log.info('MockModule loaded')


    # =====================
    # command functions
    # =====================

    @discord.commands.message_command(name='mock_message', description='mock the selected message')
    async def mock_context(self, ctx: discord.ApplicationContext, message: discord.Message):
        await self.mock_message(ctx, message)



    # reading the message history requires the message content intent
    # these commands only explain how to use the message context menu instead

    @mock_group.command(name='last', description='learn how to mock a message')
    async def mock_last(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=self.get_usage_embed(), ephemeral=True)


    @mock_group.command(name='user', description='learn how to mock a message')
    async def mock_user(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=self.get_usage_embed(), ephemeral=True)




def setup(client):
    client.add_cog(MockModule(client))
