from typing import List, Optional, Mapping
from disnake import Message, Embed
from disnake.ext import commands
from . import main_db


async def get_guild_prefix(bot: commands.Bot, message: Message) -> List[str]:
    if not message.guild or await main_db.get_prefix(message.guild.id) is None:
        return commands.when_mentioned_or(">>", ">")(bot, message)

    prefix = await main_db.get_prefix(message.guild.id)
    return commands.when_mentioned_or(prefix)(bot, message)


def command_is_disabled():
    async def predicate(ctx: commands.Context) -> bool:
        guild_id = ctx.guild.id

        result = await main_db.check_command(
            guild_id,
            ctx.command.qualified_name.split()[0]
            if ctx.command.parent
            else ctx.command.name,
        )

        if result:
            await ctx.send(
                embed=Embed(
                    title="Error",
                    description="This command is disabled in this guild.",
                    colour=0xFF0000,
                )
            )
            return False
        return True

    return commands.check(predicate)
