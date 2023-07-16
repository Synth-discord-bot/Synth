import disnake
from disnake.ext import commands
from src import testdb


class FirstTestCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.testdb = testdb

    @commands.command()
    async def search_all(self, ctx: commands.Context) -> None:
        # await self.testdb.add_to_db({"id": 1, "test": False})
        msg = await ctx.send("Successfully added to database. Now lets try to find it.")
        result = self.testdb.get_items_in_cache({"test": True})
        await msg.edit(content="The result is {}".format(result))
        await ctx.message.add_reaction("✅")

    @commands.command()
    async def search_one(self, ctx: commands.Context) -> None:
        # await self.testdb.add_to_db({"id": 1, "test": False})
        msg = await ctx.send("Successfully added to database. Now lets try to find it.")
        result = await self.testdb.find_one_cache({"test": True})
        await msg.edit(content="The result is {}".format(result))
        await ctx.message.add_reaction("✅")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(FirstTestCog(bot=bot))
