from disnake.ext import commands
import disnake
import random
from disnake import Localized


class Fun(commands.Cog):
    """Fun commands."""

    EMOJI = "😂"

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name=Localized("roll", key="ROLL_COMMAND_NAME"), description=Localized("Roll a dice", key="ROLL_COMMAND_DESC"))
    async def roll(
        self,
        interaction: disnake.MessageCommandInteraction,
        number: int = commands.Param(description=Localized("Default: 6", key="ROLL_COMMAND_NUMBER"), default=6, name = Localized("number", key="ROLL_COMMAND_NUMBER_NAME")),
    ):
        roll = random.randint(1, number)
        embed = disnake.Embed(
            title="Rolled", color=0x2b2d31, description=f"You rolled a `{roll}`"
        )
        await interaction.send(embed=embed)

    @commands.slash_command(name=Localized("coin", key="COIN_COMMAND_NAME"), description=Localized("Flip a coin", key="COIN_COMMAND_DESC"))
    async def coin(self, interaction: disnake.MessageCommandInteraction):
        if random.randint(0, 1) == 0:
            embed = disnake.Embed(
                title="Flip coin", color=0x2b2d31, description="Heads"
            )
        else:
            embed = disnake.Embed(
                title="Flip coin", color=0x2b2d31, description="Tails"
            )
        await interaction.send(embed=embed)

    @commands.slash_command(name="8ball", description=Localized("Ask a question", key="8BALL_COMMAND_DESC"))
    async def eight_ball(
        self, interaction: disnake.MessageCommandInteraction, question: str = commands.Param(description=Localized("Ask a question", key="8BALL_COMMAND_QUESTION"), name=Localized("question", key="8BALL_COMMAND_QUESTION_NAME"))
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
            color=0x2b2d31,
            description=f"Question: `{question}`\nAnswer: `{random.choice(responses)}`",
        )
        await interaction.send(embed=embed)

    @commands.slash_command(name=Localized("ben", key="BEN_COMMAND_NAME"), description=Localized("Ask a question", key="BEN_COMMAND_DESC"))
    async def ben(
        self,
        interaction: disnake.MessageCommandInteraction,
        question: str = commands.Param(
            description=Localized("Ask a question", key="BEN_COMMAND_QUESTION_DESC"), max_length=128, min_length=1,
            name = Localized("question", key="BEN_COMMAND_QUESTION_NAME")
        ),
    ):
        chance = random.randint(1, 5)
        if chance == 1:
            embed = disnake.Embed(
                title="Yes", description=f"{question}", color=0x2b2d31
            ).set_image(url="https://c.tenor.com/R_itimARcLAAAAAC/talking-ben-yes.gif")
        if chance == 2:
            embed = disnake.Embed(
                title="No", description=f"{question}", color=0x2b2d31
            ).set_image(url="https://c.tenor.com/3ZLujiiPc4YAAAAC/talking-ben-no.gif")
        if chance == 3:
            embed = disnake.Embed(
                title="Hohoho", description=f"{question}", color=0x2b2d31
            ).set_image(
                url="https://c.tenor.com/agrQMQjQTzgAAAAd/talking-ben-laugh.gif"
            )
        if chance == 4:
            embed = disnake.Embed(
                title="Ugh...", description=f"{question}", color=0x2b2d31
            ).set_image(url="https://c.tenor.com/fr6i8VzKJuEAAAAd/talking-ben-ugh.gif")
        if chance == 5:
            embed = disnake.Embed(
                title=f"Bye...", description=f"{question}", color=0x2b2d31
            ).set_image(url="https://c.tenor.com/7j3yFGeMMgIAAAAd/talking-ben-ben.gif")
        await interaction.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot=bot))
