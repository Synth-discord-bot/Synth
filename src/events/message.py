from datetime import datetime

import disnake
from disnake.ext import commands

from src.utils import logger


class EventMessages(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super(EventMessages, self).__init__()
        self.logger = logger
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message) -> None:
        if message.author == message.guild.me:
            return

        message.content = (
            message.content[:1900] + "..."
            if len(message.content) > 1900
            else message.content
        )  # TODO: send message to text file if message.content > 1900
        embeds = []
        embed = disnake.Embed(color=0x2F3136, title="Deleted Message", description=None)
        embed.add_field(name="Additional information", value="No")
        field_dop_index = next(
            index
            for index, field in enumerate(embed.fields)
            if field.name == "Additional information"
        )
        files = []
        embeds.append(embed)

        if message.attachments:
            for num, attachment in enumerate(message.attachments, start=1):
                embed.set_field_at(
                    field_dop_index,
                    name="Additional information",
                    value=f"Number of media files: `{num}`",
                )
                files.append(await attachment.to_file())

        if message.embeds:
            embed.set_field_at(
                field_dop_index,
                name="Additional information",
                value=f"Number of Embeds Deleted: `{len(message.embeds)}`",
            )
            for num, emb in enumerate(message.embeds, start=1):
                if num < 9:
                    emb.set_footer(text=f"Number: {num}")
                    embeds.append(emb)

        embed.add_field(
            name="Author",
            value=f"{message.author.mention} (`{message.author}` `ID: {message.author.id}`)",
            inline=False,
        )
        embed.add_field(
            name="Deleted at",
            value=disnake.utils.format_dt(datetime.now(), style="f"),
            inline=True,
        )
        embed.add_field(
            name="Channel",
            value=f"{message.channel.mention} (`ID: {message.channel.id}`)",
        )
        embed.set_thumbnail(url=message.author.avatar)
        logger_channel = await self.logger.get_loggers(
            guild_id=message.guild.id, to_return="message"
        )
        channel = message.guild.get_channel(int(logger_channel))
        await channel.send(embeds=embeds, files=files)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author == before.guild.me:
            return

        if before.content == after.content:
            return

        before.content = (
            before.content[:1900] + "..."
            if len(before.content) > 1900
            else before.content
        )  # TODO: send message to text file if before.content > 1900
        after.content = (
            after.content[:1900] + "..." if len(after.content) > 1900 else after.content
        )  # TODO: send message to text file if after.content > 1900
        if before.content == after.content:
            return
        embed = disnake.Embed(
            title="Edited Message",
            description=f"Before: {before.content}\nAfter: {after.content}",
            color=0x2F3136,
        )
        embed.add_field(
            name="Author",
            value=f"{after.author.mention} (`{after.author}` `ID: {after.author.id}`)",
            inline=False,
        )
        embed.add_field(
            name="Edited at",
            value=disnake.utils.format_dt(datetime.now(), style="f"),
            inline=True,
        )
        embed.add_field(
            name="Channel",
            value=f"{before.channel.mention} (`ID: {before.channel.id}`)",
        )
        logger_channel = await self.logger.get_loggers(
            guild_id=before.guild.id, to_return="message"
        )
        channel = before.guild.get_channel(int(logger_channel))
        await channel.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EventMessages(bot=bot))
