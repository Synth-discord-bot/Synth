import io
from io import BytesIO
from typing import List, Union, Literal

import ujson
from disnake import (
    Attachment,
    Message,
    Embed,
    MessageCommandInteraction,
    TextChannel,
    HTTPException,
    Forbidden,
)
from disnake.ext import commands

from . import main_db

from enum import StrEnum


async def bot_get_guild_prefix(bot: commands.Bot, message: Message) -> List[str]:
    if not message.guild or await main_db.get_prefix(message.guild.id) is None:
        return commands.when_mentioned_or(">>", ">")(bot, message)

    prefix = await main_db.get_prefix(message.guild.id)
    return commands.when_mentioned_or(prefix)(bot, message)


# get prefix for commands, events etc..
async def get_prefix(message: Message) -> Union[List[str], str]:
    if not message.guild or await main_db.get_prefix(message.guild.id) is None:
        return "s."

    prefix = await main_db.get_prefix(message.guild.id)
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
