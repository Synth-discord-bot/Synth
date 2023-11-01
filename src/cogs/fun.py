import random

import disnake
from disnake import Localized
from disnake.ext import commands


class Fun(commands.Cog):
    """Fun commands."""

    EMOJI = "😂"

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name=Localized("roll", key="ROLL_COMMAND_NAME"),
        description=Localized("Roll a dice", key="ROLL_COMMAND_DESC"),
    )
    async def roll(
        self,
        interaction: disnake.MessageCommandInteraction,
        number: int = commands.Param(
            description=Localized("Default: 6", key="ROLL_COMMAND_NUMBER"),
            default=6,
            name=Localized("number", key="ROLL_COMMAND_NUMBER_NAME"),
        ),
    ):
        roll = random.randint(1, number)
        embed = disnake.Embed(
            title="Rolled", color=0x2B2D31, description=f"You rolled a `{roll}`"
        )
        await interaction.send(embed=embed)

    @commands.slash_command(
        name=Localized("coin", key="COIN_COMMAND_NAME"),
        description=Localized("Flip a coin", key="COIN_COMMAND_DESC"),
    )
    async def coin(self, interaction: disnake.MessageCommandInteraction):
        if random.randint(0, 1) == 0:
            embed = disnake.Embed(
                title="Flip coin", color=0x2B2D31, description="Heads"
            )
        else:
            embed = disnake.Embed(
                title="Flip coin", color=0x2B2D31, description="Tails"
            )
        await interaction.send(embed=embed)

    @commands.slash_command(
        name="8ball", description=Localized("Ask a question", key="8BALL_COMMAND_DESC")
    )
    async def eight_ball(
        self,
        interaction: disnake.MessageCommandInteraction,
        question: str = commands.Param(
            description=Localized("Ask a question", key="8BALL_COMMAND_QUESTION"),
            name=Localized("question", key="8BALL_COMMAND_QUESTION_NAME"),
        ),
    ):
        good_responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Yes.",
        ]
        medium_responses = [
            "Most likely.",
            "Outlook good.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
        ]
        bad_responses = [
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]

        response_category = random.choice(["good", "medium", "bad"])

        if response_category == "good":
            response = random.choice(good_responses)
            color = 0x39F007
        elif response_category == "medium":
            response = random.choice(medium_responses)
            color = 0xF0D707
        else:
            response = random.choice(bad_responses)
            color = 0xF00707

        embed = disnake.Embed(
            title="Magic 8ball",
            color=color,
            description=f"Question: `{question}`\nAnswer: `{response}`",
        )
        embed.set_image(
            url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.tapscape.com%2Fwp"
            "-content%2Fuploads%2F2018%2F06%2FMagic-8-Ball.jpg&f=1&nofb=1&ipt"
            "=a3fd2b53113d3242cd34d2cd8df87ca0071c68bebf442a1c66ccf94438a76b34&ipo=images"
        )
        embed.set_footer(text="Synth © 2023 | All Rights Reserved")

        await interaction.send(embed=embed)

    @commands.slash_command(
        name=Localized("ben", key="BEN_COMMAND_NAME"),
        description=Localized("Ask a question", key="BEN_COMMAND_DESC"),
    )
    async def ben(
        self,
        interaction: disnake.MessageCommandInteraction,
        question: str = commands.Param(
            description=Localized("Ask a question", key="BEN_COMMAND_QUESTION_DESC"),
            max_length=128,
            min_length=1,
            name=Localized("question", key="BEN_COMMAND_QUESTION_NAME"),
        ),
    ):
        chance = random.randint(1, 5)
        if chance == 1:
            embed = disnake.Embed(
                title="Yes", description=f"{question}", color=0x2B2D31
            ).set_image(url="https://c.tenor.com/R_itimARcLAAAAAC/talking-ben-yes.gif")
        if chance == 2:
            embed = disnake.Embed(
                title="No", description=f"{question}", color=0x2B2D31
            ).set_image(url="https://c.tenor.com/3ZLujiiPc4YAAAAC/talking-ben-no.gif")
        if chance == 3:
            embed = disnake.Embed(
                title="Hohoho", description=f"{question}", color=0x2B2D31
            ).set_image(
                url="https://c.tenor.com/agrQMQjQTzgAAAAd/talking-ben-laugh.gif"
            )
        if chance == 4:
            embed = disnake.Embed(
                title="Ugh...", description=f"{question}", color=0x2B2D31
            ).set_image(url="https://c.tenor.com/fr6i8VzKJuEAAAAd/talking-ben-ugh.gif")
        if chance == 5:
            embed = disnake.Embed(
                title=f"Bye...", description=f"{question}", color=0x2B2D31
            ).set_image(url="https://c.tenor.com/7j3yFGeMMgIAAAAd/talking-ben-ben.gif")
        await interaction.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot=bot))
