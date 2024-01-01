from typing import Optional

import disnake
from disnake import InteractionMessage
from disnake.ext import commands

from src.utils import logger, main_db
from src.utils.misc import check_channel


class Logger(commands.Cog):
    """Commands to setup logging system."""

    EMOJI = "<:list:1169690529643114547>️"

    def __init__(self, bot) -> None:
        self.bot = bot
        self.logger = logger
        self.settings_db = main_db

    async def cog_load(self) -> None:
        await self.logger.fetch_and_cache_all()

    @commands.slash_command(name="logger")
    async def logger(self, _: disnake.ApplicationCommandInteraction):
        pass

    @logger.sub_command(name="set_channel")
    async def set_log_channel(
        self,
        interaction: disnake.MessageCommandInteraction,
        main_log_channel: disnake.TextChannel,
        guild_log_channel: disnake.TextChannel = None,
        invite_log_channel: disnake.TextChannel = None,
        message_log_channel: disnake.TextChannel = None,
    ) -> Optional[InteractionMessage]:
        if await check_channel(channel=main_log_channel, interaction=interaction):
            guild_log = invite_log = message_log = False
            if guild_log_channel:
                guild_log = await check_channel(
                    channel=guild_log_channel, interaction=interaction
                )
            if invite_log_channel:
                invite_log = await check_channel(
                    channel=invite_log_channel, interaction=interaction
                )
            if message_log_channel:
                message_log = await check_channel(
                    channel=message_log_channel, interaction=interaction
                )
            await self.logger.create_logger(
                guild_id=interaction.guild,
                main_log_channel=main_log_channel,
                guild_log_channel=(
                    guild_log_channel
                    if guild_log_channel is not None and guild_log
                    else main_log_channel
                ),
                invite_log_channel=(
                    invite_log_channel
                    if invite_log_channel is not None and invite_log
                    else main_log_channel
                ),
                message_log_channel=(
                    message_log_channel
                    if message_log_channel is not None and message_log
                    else main_log_channel
                ),
            )
            return await interaction.edit_original_response(
                embed=disnake.Embed(
                    title="Logger",
                    description="Successfully setup loggers to channel(s)!",
                    color=self.settings_db.get_embed_color(interaction.guild.id),
                )
            )
        return


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Logger(bot))
