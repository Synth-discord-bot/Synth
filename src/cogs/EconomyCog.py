from typing import Any

import disnake
from disnake import (
    Embed,
    Localized,
    CommandInteraction,
    ui,
    ButtonStyle,
    MessageInteraction,
    Color,
    Member,
    MessageCommandInteraction,
)
from disnake.ext import commands

from src.utils import economy, EconomyDatabase as EcoDB


class Buttons(ui.View):
    def __init__(
        self,
        ctx: MessageCommandInteraction,
        bot: commands.Bot,
        receiver: Member,
        money: int,
        economy_data: EcoDB,
    ) -> None:
        super().__init__(timeout=20)
        self.ctx = ctx
        self.bot = bot
        self.receiver = receiver
        self.money = money
        self.economy = economy_data

    @ui.button(emoji="✅", style=ButtonStyle.secondary, custom_id="test")
    async def yes_callback(self, _: ui.Button, interaction: MessageInteraction) -> None:
        await interaction.send(content="Please, wait...")

        received_balance = await self.economy.get_balance(user_id=self.receiver.id)
        new_received_balance = received_balance + self.money

        old_bal_sender = await self.economy.get_balance(user_id=self.ctx.author.id)
        new_sender_balance = old_bal_sender - self.money

        try:
            await self.economy.update_db(
                {"id": self.receiver.id}, {"balance": new_received_balance}
            )
            await self.economy.update_db(
                {"id": self.ctx.author.id}, {"balance": new_sender_balance}
            )
            await interaction.edit_original_response(
                content="",
                embed=Embed(
                    title="Successful",
                    description=f"You successfully transferred {self.receiver} {self.money} 🪙!",
                    color=Color.green(),
                ),
            )
        except (Exception, BaseException):
            await interaction.edit_original_response(
                content="",
                embed=Embed(
                    title="Error",
                    description=f"Failed to transfer to {self.receiver} {self.money} 🪙",
                    color=Color.red(),
                ),
            )

    @disnake.ui.button(
        emoji="❌",
        style=ButtonStyle.secondary,
        custom_id="danger",
    )
    async def no_callback(self, _, interaction):
        await interaction.response.send_message("OK!")

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(
                "You cannot press these buttons!", ephemeral=True
            )
        else:
            return True

    async def on_timeout(self) -> None:
        return


class Economy(commands.Cog):
    """Economy commands"""

    EMOJI = "<:gift:1169690502635991241>"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.economy = economy

    async def cog_load(self) -> None:
        await self.economy.fetch_and_cache_all()

    @commands.slash_command(description=Localized("test", key="test"))
    async def balance(self, interaction: CommandInteraction):
        if await self.economy.find_one({"id": interaction.author.id}) is None:
            await self.economy.add_to_db(
                {"id": interaction.author.id, "balance": 0, "bank": 0}
            )

        money = await self.economy.get_balance(interaction.author)
        bank = await self.economy.get_bank(interaction.author)
        total = money + bank

        await interaction.send(
            embed=Embed(
                title="Balance",
                description=(
                    f"{interaction.author.name}, your balance:"
                    f"\n**Cash:** {money} 🪙\n**Bank:** {bank}🪙\n**Total:** {total}🪙"
                ),
            ),
            ephemeral=True,
        )

    @commands.slash_command(
        name=Localized("bank", key="BANK_COMMAND_NAME"),
        description=Localized("bank", key="BANK_COMMAND_DESC"),
    )
    async def bank(
        self,
        interaction: disnake.MessageCommandInteraction,
        money: Any = "all",
    ) -> None:
        """Send money to the bank

        Arguments: number or "all"
        """

        # Check if user has an existing economy record, if not, add one
        if await self.economy.find_one({"id": interaction.author.id}) is None:
            await self.economy.add_to_db(
                {"id": interaction.author.id, "balance": 0, "bank": 0}
            )

        # Get the current balance
        current_money = await self.economy.get_balance(interaction.author)

        # If money value is "all", set it to current balance
        if isinstance(money, str) and money == "all":
            money = current_money

        # Check if money is a valid number
        if not isinstance(money, int):
            return await interaction.send(
                'Please enter a valid number or "all" argument to send 🪙 to bank!'
            )

        # Check if money is positive
        if money <= 0:
            return await interaction.send(
                "You can't send negative or zero 🪙 to your bank!"
            )

        # Check if user has enough money
        if current_money < money:
            return await interaction.send("You don't have enough 🪙!")

        # Update the database with new bank and balance values
        await self.economy.update_db(
            {"id": interaction.author.id},
            {
                "bank": current_money if money == current_money else money,
                "balance": 0 if money == current_money else current_money - money,
            },
        )

        # Calculate bank, cash, and total values
        bank = await self.economy.get_bank(interaction.author)
        cash = current_money - money
        total = cash + bank

        # Reply with balance information
        await interaction.send(
            embed=Embed(
                title="Balance",
                description=(
                    f"{interaction.author.name}, your balance now:"
                    f"\n**Cash:** {cash} 🪙\n**Bank:** {bank}🪙\n**Total:** {total}🪙"
                ),
            )
        )

    @commands.slash_command(
        name=Localized("pay", key="PAY_COMMAND_NAME"),
        description=Localized("", key="PAY_COMMAND_DESC"),
    )
    async def pay(
        self,
        interaction: disnake.MessageCommandInteraction,
        user: disnake.Member,
        money: int = 0,
    ):
        if user is None:
            return await interaction.send("Please specify the user (mention or id)")

        if money == 0:
            return await interaction.send("Please specify money to transfer")

        elif await self.economy.get_balance(user_id=interaction.author.id) < money:
            return await interaction.send(
                "Not enough to transfer the money to the user"
            )
        elif money > 9223372036854775807:
            await interaction.send(
                embed=Embed(
                    title="🚫 | Transfer error",
                    description="You want to transfer too much money!",
                    color=Color.red(),
                ),
            )
        elif money < 1:
            return await interaction.send(
                embed=Embed(
                    title="🚫 | Transfer error",
                    description="You can't transfer less than 1 🪙",
                    color=Color.red(),
                ).set_footer(text=f"Command executed by {interaction.author}"),
            )
        else:
            await interaction.send(
                f"Are you sure you want transfer {money} 🪙 to {user.mention}?",
                view=Buttons(
                    ctx=interaction,
                    bot=self.bot,
                    receiver=user,
                    money=money,
                    economy_data=self.economy,
                ),
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Economy(bot=bot))
