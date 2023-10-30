from disnake.ext import commands
import disnake
import random


class Fun(commands.Cog):
    """Fun commands."""

    EMOJI = "😂"

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="roll", description="Rolls a dice.")
    async def roll(
        self,
        interaction: disnake.MessageCommandInteraction,
        number: int = commands.Param(description="Default: 6", default=6),
    ):
        roll = random.randint(1, number)
        embed = disnake.Embed(
            title="Rolled", color=0x2F3136, description=f"You rolled a `{roll}`"
        )
        await interaction.send(embed=embed)

    @commands.slash_command(name="flip", description="Flips a coin.")
    async def flip(self, interaction: disnake.MessageCommandInteraction):
        if random.randint(0, 1) == 0:
            embed = disnake.Embed(
                title="Flip coin", color=0x2F3136, description="Heads"
            )
        else:
            embed = disnake.Embed(
                title="Flip coin", color=0x2F3136, description="Tails"
            )
        await interaction.send(embed=embed)

    @commands.slash_command(name="8ball", description="Ask the magic 8ball a question.")
    async def eight_ball(
        self, interaction: disnake.MessageCommandInteraction, question: str
    ):
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]
        embed = disnake.Embed(
            title="Magic 8ball",
            color=0x2F3136,
            description=f"Question: `{question}`\nAnswer: `{random.choice(responses)}`",
        )
        await interaction.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot=bot))
