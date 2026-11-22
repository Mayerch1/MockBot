import logging
import discord

from lib.tinyConnector import TinyConnector

log = logging.getLogger('MockBot')

MANAGE_PERMS = discord.Permissions(manage_guild=True)

DELETE_SETTING_NAME = 'After mocking a message'
DELETE_OPTION_LABELS = {
    True: 'Delete original message',
    False: 'Keep original message',
}


class SettingsModal(discord.ui.DesignerModal):
    """modal for editing the guild settings
       - whether the original message is deleted after mocking it
    """

    def __init__(self, guild_id: int, delete_on_mock: bool):
        self.guild_id = guild_id

        self.delete_select = discord.ui.Select(
            discord.ComponentType.string_select,
            custom_id='settings_delete_on_mock',
            min_values=1,
            max_values=1,
            required=True,
            options=[
                discord.SelectOption(label=DELETE_OPTION_LABELS[True], value='on',
                                     description='The bot needs the Manage Messages permission',
                                     default=delete_on_mock),
                discord.SelectOption(label=DELETE_OPTION_LABELS[False], value='off',
                                     default=not delete_on_mock),
            ],
        )

        super().__init__(
            discord.ui.Label(DELETE_SETTING_NAME, self.delete_select,
                             description='What happens to the message that was mocked'),
            title='MockBot Settings',
        )


    async def callback(self, interaction: discord.Interaction):
        delete_on_mock = (self.delete_select.values[0] == 'on')
        TinyConnector.set_delete_on_mock(self.guild_id, delete_on_mock)

        eb = discord.Embed(title='Settings saved')
        eb.add_field(name=DELETE_SETTING_NAME, value=DELETE_OPTION_LABELS[delete_on_mock], inline=False)

        await interaction.response.send_message(embed=eb, ephemeral=True)


class SettingsCog(discord.Cog):

    def __init__(self, client: discord.AutoShardedBot):
        self.client: discord.AutoShardedBot = client


    @discord.Cog.listener()
    async def on_ready(self):
        log.info('MockSettings loaded')


    @discord.slash_command(name='settings',
                           description='edit the bot settings for this server',
                           default_member_permissions=MANAGE_PERMS,
                           contexts={discord.InteractionContextType.guild})
    async def settings_cmd(self, ctx: discord.ApplicationContext):

        modal = SettingsModal(
            guild_id=ctx.guild_id,
            delete_on_mock=TinyConnector.get_delete_on_mock(ctx.guild_id),
        )
        await ctx.send_modal(modal)


def setup(client):
    client.add_cog(SettingsCog(client))
