from typing import List, Union

from disnake import (
    Message,
    Embed,
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
