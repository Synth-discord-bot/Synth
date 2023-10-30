from datetime import datetime

import disnake
from disnake.ext import commands

from src.utils import logger


class EventInvites(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super(EventInvites, self).__init__()
        self.logger = logger
        self.bot = bot

    @commands.Cog.listener()
    async def on_invite_create(self, invite: disnake.Invite) -> None:
        embed = disnake.Embed(title="Created Invite", description=None, color=0x2F3136)
        embed.add_field(
            name="Channel",
            value=f"{invite.channel.mention} (`ID: {invite.channel.id}`)",
            inline=False,
        )
        embed.add_field(name="Link", value=f"{invite.url}", inline=False)
        embed.add_field(
            name="Created at",
            value=disnake.utils.format_dt(datetime.now(), style="f"),
            inline=True,
        )
        embed.add_field(
            name="Inviter",
            value=f"{invite.inviter.name} (`ID: {invite.inviter.id}`)",
        )
        logger_channel = await self.logger.get_loggers(
            guild_id=invite.guild.id, to_return="invite"
        )
        channel = invite.guild.get_channel(int(logger_channel))
        await channel.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EventInvites(bot=bot))
