import io
import math
import re
from enum import StrEnum
from io import BytesIO
from typing import List, Union, Literal, Any, Optional, Dict

import disnake
import mafic
import ujson
from disnake import (
    Attachment,
    Message,
    Embed,
    Guild,
    MessageCommandInteraction,
    TextChannel,
    HTTPException,
    Forbidden,
    MessageInteraction,
)
from disnake.ext import commands

from . import main_db, commands_db


async def bot_get_guild_prefix(bot: commands.Bot, message: Message) -> List[str]:
    if not message.guild or await main_db.get_prefix(message.guild.id) is None:
        return commands.when_mentioned_or(">>", ">")(bot, message)

    prefix = await main_db.get_prefix(message.guild.id)
    return commands.when_mentioned_or(prefix)(bot, message)


# get prefix for commands, events etc..
async def get_prefix(message: Union[Message, Guild]) -> Union[List[str], str]:
    guild = message.guild if isinstance(message, Message) else message

    if not guild or await main_db.get_prefix(guild.id) is None:
        return ">>"

    prefix = await main_db.get_prefix(guild.id)
    return prefix


async def is_command_disabled(message: Message, command: str) -> bool:
    guild_id = message.guild.id

    result = await main_db.check_command(guild_id, command, False)
    if result is not False:
        await message.reply(
            embed=Embed(
                title="Error",
                description="This command is disabled in this guild.",
                colour=0xFF0000,
            )
        )
        return True


async def check_channel(
        channel: TextChannel,
        interaction: Union[MessageCommandInteraction, commands.Context],
) -> bool:
    await interaction.send(
        f"Checking access to channel {channel.mention}...", ephemeral=True
    )
    try:
        await channel.send(".", delete_after=0.05)
        return True
    except (HTTPException, Forbidden):
        await interaction.edit_original_message(
            content=(
                f"I can't check access to {channel.mention} channel, "
                f"because i don't have permissions to send messages."
            )
        )
        return False


def check_if_user_is_developer(bot: commands.Bot, user_id: int) -> bool:
    return user_id in bot.owner_ids


def is_owner():
    async def predicate(ctx: commands.Context) -> bool:
        result = ctx.author == ctx.guild.owner

        if not result:
            await ctx.send(
                embed=Embed(
                    title="<a:error:1168599839899144253> Error",
                    description="This command can be only used by the server owner",
                    colour=0xFF0000,
                )
            )
            return False

        return True

    return commands.check(predicate)  # type: ignore


def has_bot_permissions():
    async def predicate(ctx: commands.Context) -> bool:
        bot_member = ctx.guild.get_member(ctx.bot.user.id)
        if not bot_member.guild_permissions.administrator:
            await ctx.send(
                embed=Embed(
                    title="<<a:error:1168599839899144253> Error",
                    description="Bot hasn't got enough permissions to do this.",
                    colour=0xFF0000,
                )
            )
            return False

        return True

    return commands.check(predicate)  # type: ignore


def emoji(name: Literal["loading", "success", "error", "users"]):
    layers = {
        "loading": "<a:loading:1168599537682755584>",
        "success": "<a:success:1168599845192339577>",
        "error": "<a:error:1168599839899144253>",
        "users": "<:users:1168968100637589607>",
    }

    return layers[name]


async def save_file_to_memory(file: Attachment, to_dict: bool = False) -> BytesIO:
    with io.BytesIO() as temp_file:
        await file.save(fp=temp_file)
        temp_file.seek(0)
        if to_dict:
            temp_file = ujson.load(temp_file)
        return temp_file


class ConfirmEnum(StrEnum):
    OK = "confirm_yes"
    FAIL = "confirm_no"


async def str_to_seconds(input_string):
    units = {
        "s": 1,
        "с": 1,
        "m": 60,
        "х": 60,
        "h": 3600,
        "г": 3600,
        "d": 86400,
        "д": 86400,
        "w": 604800,
        "т": 604800,
        "o": 2592000,
        "м": 2592000,
        "y": 31536000,
        "р": 31536000,
    }
    input_string = (
        str(input_string).lower().strip("-").replace("мес", "е").replace("mo", "o")
    )
    return sum(
        int(number) * units.get(unit, 1)
        for number, unit in re.findall(r"(\d+)\s*([a-zA-Zа-яА-Я]+)", input_string)
    )


def word_correct(number, p1, p2, p3):
    ld = str(number)[-2:]
    cases = {
        "0": p3,
        "1": p1,
        "2": p2,
        "3": p2,
        "4": p2,
        "5": p3,
        "6": p3,
        "7": p3,
        "8": p3,
        "9": p3,
    }
    case = (
        p3
        if ld[0] == "1" and len(ld) > 1
        else cases.get(ld[0], p1)
        if len(ld) == 1
        else cases.get(ld[1], p2)
    )
    return case


async def hms(sec):
    time_units = [
        (604800, "week", "weeks"),
        (86400, "day", "days"),
        (3600, "hour", "hours"),
        (60, "minute", "minutes"),
        (1, "second", "seconds"),
    ]

    for unit, singular, plural in time_units:
        if sec >= unit:
            value = int(sec // unit)
            word = word_correct(value, singular, plural, plural)
            display = f"{value} {word}"
            sec %= unit
            if sec > 0:
                display += " " + await hms(sec)
            return display

    ms = int(sec * 1000)
    return f'{ms} {word_correct(ms, "millisecond", "milliseconds", "milliseconds")}'


async def common_checks(
        ctx: commands.Context,
        member: Union[int, str, disnake.Member, disnake.User],
        check_bot=False,
        for_unban=False,
        for_mute=False,
        str_time=None,
):
    error_embed = Embed(color=disnake.Colour.red())

    if isinstance(member, disnake.User):
        # Try to convert user to member
        member = ctx.guild.get_member(member.id or member)

    elif not member and not for_unban:
        error_embed.description = f"{emoji('error')} | Member not found in the guild"
        return False, error_embed

    elif member == ctx.author:
        error_embed.description = (
            f"{emoji('error')} | You can't perform this action on yourself."
        )
        return False, error_embed

    elif (
            not for_unban
            and isinstance(member, disnake.Member)
            and check_bot
            and member.bot
    ):
        error_embed.description = (
            f"{emoji('error')} | You can't perform this action on a bot."
        )
        return False, error_embed

    elif (
            not for_unban
            and isinstance(member, disnake.Member)
            and member.top_role >= ctx.author.top_role
    ):
        error_embed.description = (
            f"{emoji('error')} | Your role is not higher than {member.mention}'s role."
        )
        return False, error_embed

    elif (
            not for_unban
            and isinstance(member, disnake.Member)
            and member.id == ctx.bot.user.id
    ):
        error_embed.description = (
            f"{emoji('error')} | You can't perform this action on the bot."
        )
        return False, error_embed

    elif (
            check_bot
            and isinstance(member, disnake.Member)
            and member.top_role >= ctx.guild.get_member(ctx.bot.user.id).top_role
            and not ctx.author.guild.owner
            and not for_unban
    ):
        error_embed.description = (
            f"{emoji('error')} | "
            f"{member.mention}'s role is higher than mine, I can't perform this action."
        )
        return False, error_embed

    elif for_mute and str_time > 2419200:  # 28 days in seconds
        error_embed.description = (
            f"{emoji('error')} | Mute time cannot be more than 28 days."
        )
        return False, error_embed

    elif for_mute and str_time < 60:
        error_embed.description = (
            f"{emoji('error')} | Mute time cannot be less then 1 minute."
        )
        return False, error_embed

    return True, None


class EmbedPaginator(disnake.ui.View):
    def __init__(
            self,
            interaction: Union[
                disnake.MessageCommandInteraction, disnake.MessageInteraction
            ],
            author: disnake.Member,
            embed: disnake.Embed,
            data: Optional[Union[Dict, List]],
            timeout: Optional[int] = None,
            separate: int = 10,
    ) -> None:
        super().__init__(timeout=timeout)
        self.current_page = 1
        self.interaction = interaction
        self.author: disnake.Member = author
        self.embed: disnake.Embed = embed
        self.separate = separate
        self.data = data

    async def send_message(
            self,
            ctx: Union[
                commands.Context,
                disnake.MessageCommandInteraction,
                disnake.MessageInteraction,
            ],
    ) -> Union[Message, Any]:
        if isinstance(
                ctx, (disnake.MessageCommandInteraction, disnake.MessageInteraction)
        ):
            return await ctx.response.send_message(embed=self.embed, view=self)
        return await ctx.send(embed=self.embed, view=self)

    async def _create_embed(
            self, embed: disnake.Embed, data: Union[Dict, List]
    ) -> disnake.Embed:
        embed: disnake.Embed = disnake.Embed(
            title=embed.title,
            colour=embed.colour,
            timestamp=embed.timestamp,
            description="",
        )

        for index, music in enumerate(data, start=1):
            if index > self.separate:
                break

            music: mafic.Track
            embed.description += f"`{index}.` **{music.author} - {music.title}**\n"

        all_pages = math.ceil(len(self.data) / self.separate)
        embed.set_footer(text=f"Page {self.current_page} of {all_pages}")

        return embed

    async def update(
            self,
            message: Union[disnake.MessageCommandInteraction, disnake.MessageInteraction],
            embed: disnake.Embed,
    ) -> None:
        await message.edit_original_response(embed=embed, view=self)

    @disnake.ui.button(label="️◀️", style=disnake.ButtonStyle.blurple)
    async def prev_page(
            self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        await interaction.response.defer()
        self.current_page -= 1

        start = self.current_page * self.separate
        data = self.data[start:]
        await self.update(self.interaction, await self._create_embed(self.embed, data))

    @disnake.ui.button(label="▶️", style=disnake.ButtonStyle.blurple)
    async def next_page(
            self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        await interaction.response.defer()
        self.current_page += 1

        start = self.current_page * self.separate
        data = self.data[start:]
        await self.update(self.interaction, await self._create_embed(self.embed, data))

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.send(
                content="You are not allowed to use this buttons!", ephemeral=True
            )
            return False
        return True


def custom_cooldown(message: disnake.Message):
    prefix = main_db.get_prefix_from_cache(message.guild.id)
    len_prefix = len(prefix)

    if message.content.startswith(prefix):
        command = message.content.split()[0][len_prefix:]

        if cooldown := commands_db.get_command_cooldown(message.guild.id, command):
            return commands.Cooldown(1, cooldown)
