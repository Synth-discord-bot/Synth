from typing import Union

from disnake import Embed
from disnake.ext import commands
from src.utils import economy


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.economy = economy

    async def cog_load(self) -> None:
        await self.economy.fetch_and_cache_all()

    @commands.command()
    async def balance(self, ctx: commands.Context) -> None:
        if await self.economy.find_one({"id": ctx.author.id}) is None:
            await self.economy.add_to_db({"id": ctx.author.id, "balance": 0, "bank": 0})

        money = await self.economy.get_balance(ctx.author)
        bank = await self.economy.get_bank(ctx.author)
        total = money + bank

        await ctx.reply(
            embed=Embed(
                title="Balance",
                description=f"{ctx.author.name}, your balance:\n**Cash:** {money} 🪙\n**Bank:** {bank }🪙\n**Total:** {total }🪙",
            )
        )
        # await ctx.send(f"Your balance is {await self.economy.get_balance(ctx.author)}")

    @commands.command()
    async def bank(self, ctx: commands.Context, money: Union[int, str] = "all") -> None:
        # Check if user has an existing economy record, if not, add one
        if await self.economy.find_one({"id": ctx.author.id}) is None:
            await self.economy.add_to_db({"id": ctx.author.id, "balance": 0, "bank": 0})

        # Get the current balance
        current_money = await self.economy.get_balance(ctx.author)

        # If money value is "all", set it to current balance
        if isinstance(money, str) and money == "all":
            money = current_money

        # Check if money is a valid number
        if not isinstance(money, int):
            return await ctx.reply("Please enter a valid number or \"all\" argument to send 🪙 to bank!")

        # Check if money is positive
        if money <= 0:
            return await ctx.reply("You can't send negative or zero 🪙 to your bank!")

        # Check if user has enough money
        if current_money < money:
            return await ctx.reply("You don't have enough 🪙!")

        # Update the database with new bank and balance values
        await self.economy.update_db(
            {"id": ctx.author.id},
            {
                "bank": current_money if money == current_money else money,
                "balance": 0 if money == current_money else current_money - money,
            }
        )
        
        # Calculate bank, cash, and total values
        bank = await self.economy.get_bank(ctx.author)
        cash = current_money - money
        total = cash + bank
        
        # Reply with balance information
        await ctx.reply(
            embed=Embed(
                title="Balance",
                description=f"{ctx.author.name}, your balance now:\n**Cash:** {cash} 🪙\n**Bank:** {bank}🪙\n**Total:** {total}🪙",
            )
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Economy(bot=bot))
