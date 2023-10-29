from disnake.ext import commands


class EventMessages(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super(EventMessages, self).__init__()
        self.bot = bot


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EventMessages(bot=bot))
