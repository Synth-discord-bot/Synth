import logging

from disnake import Member
from disnake.ext import commands
from src.utils import economy


class EventMember(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super(EventMember, self).__init__()
        self.bot = bot
        self.economy = economy

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        await self.economy.add_member(member=member)
        logging.info(f"Member joined: {member}")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EventMember(bot=bot))
