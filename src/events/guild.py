from datetime import datetime

import disnake
from disnake.ext import commands
from src.utils import logger


class EventGuild(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super(EventGuild, self).__init__()
        self.logger = logger
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: disnake.abc.GuildChannel) -> None:
        embed = disnake.Embed(title="Deleted Channel", color=0x2F3136)

        match channel.type:
            case disnake.ChannelType.text:
                channel_type = "Text Channel"
            case disnake.ChannelType.voice:
                channel_type = "Voice Channel"
            case disnake.ChannelType.category:
                channel_type = "Category"
            case disnake.ChannelType.forum:
                channel_type = "Forum"
            case _:
                channel_type = "Unknown Type"

        embed.add_field(name="Type of channel", value=channel_type, inline=False)
        embed.add_field(
            name="Deleted at",
            value=disnake.utils.format_dt(datetime.now(), style="f"),
            inline=True,
        )
        embed.add_field(name="Channel", value=f"{channel.name}")
        logger_channel = await self.logger.get_loggers(
            guild_id=channel.guild.id, to_return="guild"
        )
        channel = channel.guild.get_channel(int(logger_channel))
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: disnake.abc.GuildChannel) -> None:
        embed = disnake.Embed(title="Created Channel", color=0x2F3136)

        match channel.type:
            case disnake.ChannelType.text:
                channel_type = "Text Channel"
            case disnake.ChannelType.voice:
                channel_type = "Voice Channel"
            case disnake.ChannelType.category:
                channel_type = "Category"
            case disnake.ChannelType.forum:
                channel_type = "Forum"
            case _:
                channel_type = "Unknown Type"

        embed.add_field(name="Type of channel", value=channel_type, inline=False)
        embed.add_field(
            name="Created at",
            value=disnake.utils.format_dt(datetime.now(), style="f"),
            inline=True,
        )
        embed.add_field(name="Channel", value=f"{channel.mention} (ID: `{channel.id}`)")
        logger_channel = await self.logger.get_loggers(
            guild_id=channel.guild.id, to_return="guild"
        )
        channel = channel.guild.get_channel(int(logger_channel))
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self,
        before: disnake.abc.GuildChannel,
        after: disnake.abc.GuildChannel,
    ) -> None:
        embed = disnake.Embed(title="Updated Channel", description=None, color=0x2F3136)
        embed.add_field(
            name="Additional information", value="Unknown error ❓", inline=False
        )
        field_index = next(
            index
            for index, field in enumerate(embed.fields)
            if field.name == "Additional information"
        )

        if before.type != after.type:
            match before.type:
                case disnake.ChannelType.text:
                    before_channel_type = "Text Channel"
                case disnake.ChannelType.voice:
                    before_channel_type = "Voice Channel"
                case disnake.ChannelType.category:
                    before_channel_type = "Category"
                case disnake.ChannelType.forum:
                    before_channel_type = "Forum"
                case _:
                    before_channel_type = "Unknown Type"

            match after.type:
                case disnake.ChannelType.text:
                    after_channel_type = "Text Channel"
                case disnake.ChannelType.voice:
                    after_channel_type = "Voice Channel"
                case disnake.ChannelType.category:
                    after_channel_type = "Category"
                case disnake.ChannelType.forum:
                    after_channel_type = "Forum"
                case _:
                    after_channel_type = "Unknown Type"
        else:
            before_channel_type = after_channel_type = before.type

        embed.add_field(
            name="Before type of channel", value=before_channel_type, inline=False
        )
        embed.add_field(
            name="Edited at",
            value=disnake.utils.format_dt(datetime.now(), style="f"),
            inline=True,
        )
        embed.add_field(name="Channel", value=f"{before.mention} (`ID: {before.id}`)")
        value = []
        if before.name != after.name:
            value.append(f"New name: `{after.name}`\nOld name: `{before.name}`\n")
        if before.topic != after.topic:  # type: ignore
            value.append(f"Old topic: `{before.topic}`\nNew topic: `{after.topic}`\n")  # type: ignore
        value.append(f"After type of channel: **{after_channel_type}**")
        embed.set_field_at(
            field_index,
            name="Additional information",
            value="\n".join(value),
            inline=False,
        )
        logger_channel = await self.logger.get_loggers(
            guild_id=before.guild.id, to_return="guild"
        )
        channel = before.guild.get_channel(int(logger_channel))
        await channel.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EventGuild(bot=bot))
