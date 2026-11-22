import logging
import discord

log = logging.getLogger('MockBot')


FEEDBACK_CHANNEL = 897465075219193916
FEEDBACK_MENTION = 872107119988588566

SUPPORT_URL = 'https://discord.gg/Xpyb9DX3D6'
GITHUB_URL = 'https://github.com/Mayerch1/MockBot'
VOTE_URL = 'https://top.gg/bot/734829435844558999'

TOS_FILE = 'legal/tos.md'
PRIVACY_FILE = 'legal/privacy.md'

# deleting the mocked message is the only action requiring a permission
# interaction responses do not need any channel permissions
INVITE_PERMISSIONS = discord.Permissions(manage_messages=True)


def _read_file(path: str) -> str:
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except OSError:
        log.exception(f'failed to read {path}')
        return '*Missing Content*'


def get_help_embed() -> discord.Embed:
    """the help page, deprecated commands (e.g. /mock last) are intentionally not listed"""

    eb = discord.Embed(title='MockBot Help',
                       description='Turn any message into a mocking SpongeBob meme.')

    eb.add_field(name='Mock a message',
                 value='Right-click (desktop) or long-press (mobile) a message, '
                       'then choose `Apps` > `mock_message`.\n'
                       'Works with text and images.',
                 inline=False)
    eb.add_field(name='/settings',
                 value='Choose whether the original message is deleted after mocking it.\n'
                       'Requires the *Manage Server* permission.',
                 inline=False)
    eb.add_field(name='/help',
                 value='Show this page.',
                 inline=False)
    eb.add_field(name='​',
                 value=f'If you like this bot, you can leave a vote at [top.gg]({VOTE_URL}).\n'
                       f'If you find a bug contact us on [GitHub]({GITHUB_URL}) or join the support server.',
                 inline=False)
    return eb


class FeedbackModal(discord.ui.DesignerModal):

    def __init__(self, client: discord.Client):
        self.client = client
        self.feedback = discord.ui.InputText(
            style=discord.InputTextStyle.paragraph,
            custom_id='help_feedback_text',
            min_length=3,
            max_length=1500,
        )
        super().__init__(
            discord.ui.Label('Please enter your feedback for this bot', self.feedback),
            title='Direct Feedback',
        )


    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        content = self.feedback.value.replace('\n', '\n> ') # keep multiline quote style

        text = f'<@&{FEEDBACK_MENTION}> New Feedback:\n'\
               f'Author: {user.mention} ({user.name})\n\n'\
               f'> {content}\n'

        try:
            ch = await self.client.fetch_channel(FEEDBACK_CHANNEL)
            # only ping the feedback role, never anything mentioned in the user text
            await ch.send(text, allowed_mentions=discord.AllowedMentions(
                everyone=False, users=False, roles=[discord.Object(FEEDBACK_MENTION)]))
        except discord.HTTPException:
            log.exception('failed to deliver feedback')
            await interaction.response.send_message(
                'There was an issue while saving your feedback.\n'
                'Please report this bug on the *support server* or on *GitHub*',
                view=HelpView.get_error_view(), ephemeral=True)
            return

        await interaction.response.send_message('Thanks for giving feedback to improve the bot', ephemeral=True)


class HelpView(discord.ui.View):
    """persistent view (no timeout, fixed custom_ids),
       buttons keep working on old help messages after a restart
    """

    def __init__(self, client: discord.Client):
        super().__init__(timeout=None)
        self.client = client

        # link buttons do not need a callback
        self.add_item(discord.ui.Button(
            style=discord.ButtonStyle.link, label='Invite Me', row=0,
            url=discord.utils.oauth_url(client.application_id, permissions=INVITE_PERMISSIONS,
                                        scopes=('bot', 'applications.commands'))))
        self.add_item(discord.ui.Button(
            style=discord.ButtonStyle.link, label='Support Server', url=SUPPORT_URL, row=0))

        # decorated buttons are added first, move feedback behind the link buttons
        self.remove_item(self.feedback_button)
        self.add_item(self.feedback_button)


    @staticmethod
    def get_error_view() -> discord.ui.View:
        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label='Support Server', url=SUPPORT_URL))
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label='GitHub Issue', url=f'{GITHUB_URL}/issues'))
        return view


    @discord.ui.button(label='Direct Feedback', style=discord.ButtonStyle.secondary,
                       custom_id='help_direct_feedback', row=0)
    async def feedback_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(FeedbackModal(self.client))


    @discord.ui.button(label='ToS', style=discord.ButtonStyle.secondary, custom_id='help_tos', row=1)
    async def tos_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(_read_file(TOS_FILE), ephemeral=True)


    @discord.ui.button(label='Privacy', style=discord.ButtonStyle.secondary, custom_id='help_privacy', row=1)
    async def privacy_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(_read_file(PRIVACY_FILE), ephemeral=True)


class HelpModule(discord.Cog):

    def __init__(self, client: discord.AutoShardedBot):
        self.client: discord.AutoShardedBot = client
        self.view_registered = False


    @discord.Cog.listener()
    async def on_ready(self):
        # on_ready can fire multiple times, only register the persistent view once
        if not self.view_registered:
            self.client.add_view(HelpView(self.client))
            self.view_registered = True
        log.info('HelpModule loaded')


    @discord.slash_command(name='help', description='Show the help page for this bot')
    async def help_cmd(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=get_help_embed(), view=HelpView(self.client), ephemeral=True)


def setup(client):
    client.add_cog(HelpModule(client))
