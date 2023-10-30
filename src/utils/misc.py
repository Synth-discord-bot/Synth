from typing import List, Union
from json import loads

from disnake import (
    Message,
    Guild,
    Embed,
    MessageCommandInteraction,
    TextChannel,
    HTTPException,
    Forbidden,
)
from disnake.ext import commands

from . import main_db

# with open("src\\assets\\langs\\ru.json", "r", encoding="utf-8") as ru_lang:
#     r = ru_lang.read()
#     ru = loads(r)
# with open("src\\assets\\langs\\ua.json", "r", encoding="utf-8") as ua_lang:
#     r = ua_lang.read()
#     ua = loads(r)
# with open("src\\assets\\langs\\en.json", "r", encoding="utf-8") as en_lang:
#     r = en_lang.read()
#     en = loads(r)
# langs_detect = {"ru": ru, "en": en, "ua": ua}

# def get_language(
#     guild_id: int,
#     category: Literal["errors", "lang", "logs"],
#     sub_category: str,
#     name: str = None,
# ):
#     global langs_detect
#     if (
#         mongo.config_data.get(guild_id) is not None
#         and mongo.config_data.get(guild_id)["lang"]
#     ):
#         lang = mongo.config_data.get(guild_id)["lang"]
#         if name:
#             return langs_detect[lang][category][sub_category][name]
#         else:
#             return langs_detect[lang][category][sub_category]
#     else:
#         return False


async def bot_get_guild_prefix(bot: commands.Bot, message: Message) -> List[str]:
    if not message.guild or await main_db.get_prefix(message.guild.id) is None:
        return commands.when_mentioned_or(">>", ">")(bot, message)

    prefix = await main_db.get_prefix(message.guild.id)
    return commands.when_mentioned_or(prefix)(bot, message)


# get prefix for commands, events etc..
async def get_prefix(message: Union[Message, Guild]) -> Union[List[str], str]:
    guild_id = message.guild.id if isinstance(message, Message) else message.id

    if not guild_id or await main_db.get_prefix(guild_id=guild_id) is None:
        return "s."

    prefix = await main_db.get_prefix(guild_id=guild_id)
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
