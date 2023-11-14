import datetime
import random
import re

import disnake
from disnake import Localized
from disnake.ext import commands, tasks

from src.utils import giveaway, main_db

time_units = {"d": "days", "h": "hours", "m": "minutes", "s": "seconds"}


class Giveaway(commands.Cog):  # Need rewrite
    """Helper commands to set up giveaway."""

    EMOJI = "<:tada:1169690533719986297>"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.giveaway_db = giveaway
        self.settings_db = main_db

    async def cog_load(self) -> None:
        await self.check_gw.start()
        await self.giveaway_db.fetch_and_cache_all()

    async def end_gw(self, i):
        channel = self.bot.get_channel(i["channel_id"])
        message: disnake.Message = await channel.fetch_message(i["message_id"])
        winner_amount = i["winner_amount"]

        embed = disnake.Embed.from_dict(i["embed_data"])
        embed.title = "Giveaway over"
        embed.set_footer(text="Ended")
        embed.timestamp = datetime.datetime.now()

        users = await message.reactions[0].users().flatten()
        users.remove(self.bot.user)

        if len(users) < winner_amount:
            winners = random.sample(users, len(users))
        else:
            winners = random.sample(users, winner_amount)

        await self.giveaway_db.delete_giveaway(value=i)
        winners = ", ".join(w.mention for w in winners)
        await message.edit(content=f"Giveaway over, winners: {winners}", embed=embed)

        if len(users) > 0:
            prize = i.get("prize")
            await message.reply(
                (f"{winners} congratulations, you have won **{prize}**!")
            )

    @commands.slash_command(
        name=Localized("giveaway", key="GIVEAWAY_COMMAND_NAME"),
        description=Localized("Create a giveaway", key="GIVEAWAY_COMMAND_DESC"),
    )
    async def giveaway(self, interaction):
        pass

    @giveaway.sub_command(
        description=Localized("Create a giveaway", key="GIVEAWAY_CREATE_COMMAND_DESC"),
        name=Localized("create", key="GIVEAWAY_CREATE_COMMAND_NAME"),
    )
    async def create(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        prize: str = commands.Param(
            description=Localized(
                "Choice prize", key="GIVEAWAY_CREATE_COMMAND_PRIZE_DESC"
            ),
            name=Localized("prize", key="GIVEAWAY_CREATE_COMMAND_PRIZE_NAME"),
        ),
        winners: int = commands.Param(
            description=Localized(
                "Winners", key="GIVEAWAY_CREATE_COMMAND_WINNERS_DESC"
            ),
            name=Localized("winners", key="GIVEAWAY_CREATE_COMMAND_WINNERS_NAME"),
        ),
        duration: str = commands.Param(
            description=Localized(
                "Example: 1d1h1m1s (1 day, 1 hour, 1 minute, 1 second)",
                key="GIVEAWAY_CREATE_COMMAND_DURATION_DESC",
            ),
            name=Localized("duration", key="GIVEAWAY_CREATE_COMMAND_DURATION_NAME"),
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
        embed = disnake.Embed(title="Giveaway", description=None, color=self.settings_db.get_embed_color(interaction.guild.id))
        embed.add_field(name="Prize", value=f"```\n{prize}\n```", inline=True)
        embed.add_field(name="Winners", value=f"```\n{winners}\n```", inline=True)
        embed.add_field(
            name="Note",
            value="```\nClick on the reaction 🎉 below to participate.\n```",
            inline=False,
        )
        embed.add_field(
            name="End",
            value=f"{disnake.utils.format_dt(end_time, style='R')} ({disnake.utils.format_dt(end_time, style='f')})",
            inline=False,
        )

        await interaction.send("Creating..", ephemeral=True)
        await interaction.delete_original_message()
        giveaway_msg: disnake.Message = await interaction.channel.send(
            content="Active giveaway", embed=embed
        )
        await giveaway_msg.add_reaction("🎉")

        await self.giveaway_db.insert_giveaway(
            channel_id=interaction.channel.id,
            message_id=giveaway_msg.id,
            end_time=end_time.timestamp(),
            winners=winners,
            embed=embed.to_dict(),
            prize=prize,
        )

    @giveaway.sub_command(
        description=Localized("Reroll giveaway", key="GIVEAWAY_REROLL_COMMAND_DESC"),
        name=Localized("reroll", key="GIVEAWAY_REROLL_COMMAND_NAME"),
    )
    async def reroll(
        self,
        interaction,
        message_id=commands.Param(
            description=Localized(
                "Message ID", key="GIVEAWAY_REROLL_COMMAND_MESSAGEID_DESC"
            ),
            name=Localized("message_id", key="GIVEAWAY_REROLL_COMMAND_MESSAGEID_NAME"),
        ),
        winners: int = commands.Param(
            description=Localized(
                "Choice winners (default: 1)",
                key="GIVEAWAY_REROLL_COMMAND_WINNERS_DESC",
            ),
            name=Localized("winners", key="GIVEAWAY_REROLL_COMMAND_WINNERS_NAME"),
            default=1,
        ),
    ):
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
            winners_mention = " ".join([user.mention for user in users]).split(" ")
        else:
            winners_mention = " ".join(
                [random.choice(users).mention for _ in range(winners)]
            ).split(" ")

        if len(winners_mention) > 0 and winners_mention[-1] in users:
            winners_mention.remove(winners_mention[-1])

        if winners > 1:
            await giveaway_msg.reply(content=f"🎉 New winners: {winners_mention}")
        else:
            await giveaway_msg.reply(content=f"🎉 New winner: {winners_mention}")

    @tasks.loop(seconds=1)
    async def check_gw(self):
        await self.bot.wait_until_ready()

        async for giveaway_data in self.giveaway_db.collection.find({}):
            channel: disnake.TextChannel = self.bot.get_channel(
                giveaway_data["channel_id"]
            )
            try:
                await channel.fetch_message(giveaway_data["message_id"])
            except (disnake.NotFound, disnake.Forbidden, disnake.HTTPException):
                await self.giveaway_db.delete_giveaway(value=giveaway_data)
                continue

            end_time = giveaway_data["end_time"]

            now = datetime.datetime.now().timestamp()

            if now > end_time:
                await self.end_gw(giveaway_data)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Giveaway(bot))
