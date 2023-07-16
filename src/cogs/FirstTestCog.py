import disnake
from disnake.ext import commands

class FirstTestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx: commands.Context):
        await ctx.send("хай, ета synth перепісь")

def setup(bot: commands.Bot):
    bot.add_cog(FirstTestCog(bot=bot))