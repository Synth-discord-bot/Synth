import io
import re
from enum import StrEnum
from io import BytesIO
from typing import List, Union, Literal

import disnake
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
)
from disnake.ext import commands

from . import main_db


async def bot_get_guild_prefix(bot: commands.Bot, message: Message) -> List[str]:
    if not message.guild or await main_db.get_prefix(message.guild.id) is None:
        return commands.when_mentioned_or(">>", ">")(bot, message)

    prefix = await main_db.get_prefix(message.guild.id)
    return commands.when_mentioned_or(prefix)(bot, message)


# get prefix for commands, events etc..
async def get_prefix(message: Union[Message, Guild]) -> Union[List[str], str]:
    guild = message.guild if isinstance(message, Message) else message

    if not guild or await main_db.get_prefix(guild.id) is None:
        return "s."

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
        return False


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

    return commands.check(predicate)


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

    return commands.check(predicate)


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

    total_seconds = 0
    matches = re.findall(r"(\d+)\s*([a-zA-Zа-яА-Я]+)", input_string)

    for number, unit in matches:
        multiplier = units.get(unit, 1)
        total_seconds += int(number) * multiplier

    total_seconds = max(total_seconds, 0)

    return total_seconds


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
    if ld[0] == "1" and len(ld) > 1:
        case = p3
    else:
        if len(ld) == 1:
            case = cases.get(ld[0], p1)
        else:
            case = cases.get(ld[1], p2)
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
    ctx, member, check_bot=False, for_unban=False, for_mute=False, str_time=None
):
    ErrorEmbed = Embed(color=disnake.Colour.red())

    if isinstance(member, disnake.User):
        # Try to convert user to member
        member = ctx.guild.get_member(member.id)

    elif not member and not for_unban:
        ErrorEmbed.description = f"{emoji('error')} | Member not found in the guild"
        return False, ErrorEmbed

    elif member == ctx.author:
        ErrorEmbed.description = (
            f"{emoji('error')} | You can't perform this action on yourself."
        )
        return False, ErrorEmbed

    elif (
        not for_unban
        and isinstance(member, disnake.Member)
        and check_bot
        and member.bot
    ):
        ErrorEmbed.description = (
            f"{emoji('error')} | You can't perform this action on a bot."
        )
        return False, ErrorEmbed

    elif (
        not for_unban
        and isinstance(member, disnake.Member)
        and member.top_role >= ctx.author.top_role
    ):
        ErrorEmbed.description = (
            f"{emoji('error')} | Your role is not higher than {member.mention}'s role."
        )
        return False, ErrorEmbed

    elif (
        not for_unban
        and isinstance(member, disnake.Member)
        and member.id == ctx.bot.user.id
    ):
        ErrorEmbed.description = (
            f"{emoji('error')} | You can't perform this action on the bot."
        )
        return False, ErrorEmbed

    elif (
        check_bot
        and isinstance(member, disnake.Member)
        and member.top_role >= ctx.guild.get_member(ctx.bot.user.id).top_role
        and not ctx.author.guild.owner
        and not for_unban
    ):
        ErrorEmbed.description = f"{emoji('error')} | {member.mention}'s role is higher than mine, I can't perform this action."
        return False, ErrorEmbed

    elif for_mute and str_time > 2419200:  # 28 days in seconds
        ErrorEmbed.description = (
            f"{emoji('error')} | Mute time cannot be more than 28 days."
        )
        return False, ErrorEmbed

    elif for_mute and str_time < 60:
        ErrorEmbed.description = (
            f"{emoji('error')} | Mute time cannot be less then 1 minute."
        )
        return False, ErrorEmbed

    return True, None
