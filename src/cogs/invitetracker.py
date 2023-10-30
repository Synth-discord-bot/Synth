import datetime

import disnake
from disnake.ext import commands
from disnake.ext.commands import TextChannelConverter

from src.utils import invites
from src.utils.misc import check_channel


class InviteTracker(commands.Cog):
    """Helper commands to setup invite tracker system."""

    EMOJI = "🔗"

    def __init__(self, bot) -> None:
        self.bot = bot
        self.invites = invites

    async def cog_load(self):
        await self.invites.fetch_and_cache_all()

    @commands.slash_command(name="invite_tracker")
    async def _invites(self, _: disnake.ApplicationCommandInteraction):
        pass

    @_invites.sub_command(name="set_channel")
    async def set_invite_channel(
        self,
        interaction: disnake.MessageCommandInteraction,
        channel: disnake.TextChannel,
    ):
        invite_channel = await check_channel(channel=channel, interaction=interaction)
        await self.invites.update_invite_info(
            guild_id=interaction.guild.id, inviter=interaction.user, invited=[]
        )
        await interaction.edit_original_response(
            content="",
            embed=disnake.Embed(
                title="Invite Tracker",
                description="Successfully setup invite tracker to channel!",
            ),
        )


def setup(bot: commands.Bot):
    bot.add_cog(InviteTracker(bot))
