from typing import List, Optional, Mapping, Union
from disnake import Message, Embed
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
        print(bot_member.guild_permissions.administrator)
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
