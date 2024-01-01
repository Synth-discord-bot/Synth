import disnake
from disnake import Localized
from disnake.ext import commands

from src.utils import invites, main_db
from src.utils.misc import check_channel


class InviteTracker(commands.Cog):
    """Commands to set up invite tracker system."""

    EMOJI = "<:link:1169685349409226893>"

    def __init__(self, bot) -> None:
        self.bot = bot
        self.invites = invites
        self.settings_db = main_db

    async def cog_load(self) -> None:
        await self.invites.fetch_and_cache_all()

    @commands.slash_command(
        name=Localized("invite_tracker", key="INVITE_TRACKER_COMMAND_NAME"),
        description=Localized(
            "Setup invite tracker system", key="INVITE_TRACKER_COMMAND_DESC"
        ),
    )
    async def _invites(self, _: disnake.ApplicationCommandInteraction) -> None:
        pass

    @_invites.sub_command(name="set_channel")
    async def set_invite_channel(
        self,
        interaction: disnake.MessageCommandInteraction,
        channel: disnake.TextChannel = commands.Param(
            name=Localized("channel", key="INVITE_TRACKER_SET_CHANNEL_NAME"),
            description=Localized(
                "Invite tracker channel", key="INVITE_TRACKER_SET_CHANNEL_DESC"
            ),
        ),
    ) -> None:
        await check_channel(channel=channel, interaction=interaction)
        await self.invites.update_invite_info(
            guild_id=interaction.guild.id, inviter=interaction.user, invited=[]
        )
        await interaction.edit_original_response(
            content="",
            embed=disnake.Embed(
                title="Invite Tracker",
                description="Successfully setup invite tracker to channel!",
                color=self.settings_db.get_embed_color(interaction.guild.id),
            ),
        )


def setup(bot: commands.Bot):
    bot.add_cog(InviteTracker(bot))
