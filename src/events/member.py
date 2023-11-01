import logging

from disnake import Member
from disnake.ext import commands

from src.utils import economy, invites


class EventMember(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super(EventMember, self).__init__()
        self.bot = bot
        self.economy = economy
        self.invites = invites

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        if member.bot:
            return

        await self.economy.add_member(member=member)
        # await self.invites.update_invite_info(guild_id=member.guild.id)
        logging.info(f"Member joined: {member}")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EventMember(bot=bot))
