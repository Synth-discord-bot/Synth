import asyncio
import datetime
import random
import re
import disnake
from disnake.ext import commands

time_units = {"d": "days", "h": "hours", "m": "minutes", "s": "seconds"}


class GiveawayCog(commands.Cog):  # Need rewrite
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command()
    async def giveaway(self, interaction):
        pass

    @giveaway.sub_command(description="Create a giveaway")
    async def create(
        self,
        interaction,
        prize: str,
        winners: int,
        duration: str = commands.Param(
            description="Example: 1d1h1m1s (1 day, 1 hour, 1 minute, 1 second)",
            name="duration",
        ),
    ):
        duration_regex = r"(\d+)([dhms])"

        matches = re.findall(duration_regex, duration)

        duration_delta = datetime.timedelta()
        for value, unit in matches:
            if unit in time_units:
                time_unit = time_units[unit]
                duration_delta += datetime.timedelta(**{time_unit: int(value)})

        end_time = datetime.datetime.now() + duration_delta
        embed = disnake.Embed(title="Giveaway", description=None, color=0x2F3136)
        embed.add_field(name=f"Prize", value=f"```\n{prize}\n```", inline=True)
        embed.add_field(name=f"Winners", value=f"```\n{winners}\n```", inline=True)
        embed.add_field(
            name=f"Note",
            value=f"```\nClick on the reaction 🎉 below to participate.\n```",
            inline=False,
        )
        embed.add_field(
            name=f"End",
            value=f"{disnake.utils.format_dt(end_time, style = 'R')} ({disnake.utils.format_dt(end_time, style = 'f')})",
            inline=False,
        )
        await interaction.send("Creating..", ephemeral=True)
        await interaction.delete_original_message()
        giveaway_msg = await interaction.channel.send(
            content="Active giveaway", embed=embed
        )
        await giveaway_msg.add_reaction("🎉")
        await asyncio.sleep(duration_delta.total_seconds())
        channel = interaction.channel
        giveaway_msg = await channel.fetch_message(giveaway_msg.id)
        reaction = disnake.utils.get(giveaway_msg.reactions, emoji="🎉")

        users = await reaction.users().flatten()
        users = [user for user in users if not user.bot]

        if len(users) == 0:
            await giveaway_msg.edit(
                content="Not enough participants to choose winners."
            )
            return

        if len(users) <= winners:
            winners_mention = " ".join([user.mention for user in users])
        else:
            winners_mention = " ".join(
                [random.choice(users).mention for _ in range(winners)]
            )

        embed.remove_field(index=3)
        embed.set_footer(
            text=f"The giveaway's over",
            icon_url="https://cdn.discordapp.com/attachments/635043187815219214/1116117523436421130/fzfZCur.png",
        )
        await giveaway_msg.edit(content=f"Winner: {winners_mention}!", embed=embed)
        await giveaway_msg.reply(
            content=f"Congratulations {winners_mention}! You won **{prize}**!"
        )

    @giveaway.sub_command(description="Reroll a giveaway")
    async def reroll(self, interaction, message_id, winners: int):
        try:
            giveaway_msg = await interaction.channel.fetch_message(message_id)
        except disnake.NotFound:
            await interaction.send("Message not found.", ephemeral=True)
            return

        if giveaway_msg.author == self.bot:
            if (
                not giveaway_msg.embeds
                or not giveaway_msg.embeds[0].title == "Giveaway"
            ):
                await interaction.send(
                    "The above message is not a giveaway message.", ephemeral=True
                )
                return

        reaction = disnake.utils.get(giveaway_msg.reactions, emoji="🎉")
        if not reaction:
            await interaction.send(
                "The above message has no 🎉 reaction.", ephemeral=True
            )
            return

        users = await reaction.users().flatten()
        users = [user for user in users if not user.bot]

        winners_mention = []

        for field in giveaway_msg.embeds[0].fields:
            if field.name == "Winners":
                winners_mention = field.value.split()

        if len(users) <= len(winners_mention):
            winners_mention = " ".join([user.mention for user in users])
        else:
            winners_mention = " ".join(
                [random.choice(users).mention for _ in range(winners)]
            )

        if len(winners_mention) > 0 and winners_mention[-1] in users:
            winners_mention.remove(winners_mention[-1])

        if winners > 1:
            await giveaway_msg.reply(content=f"🎉 New winners: {winners_mention}")
        else:
            await giveaway_msg.reply(content=f"🎉 New winner: {winners_mention}")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(GiveawayCog(bot))
