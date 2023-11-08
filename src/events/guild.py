from datetime import datetime
<<<<<<< HEAD
from os import getenv

import disnake
from disnake.ext import commands

from src.utils import logger
from src.utils.misc import get_prefix
=======

import disnake
from disnake.ext import commands
from src.utils import logger
from src.utils.misc import get_prefix
from os import getenv
import io
>>>>>>> 806890f7f3011613a74d6e889d19da9ca56ca3b0


class EventGuild(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super(EventGuild, self).__init__()
        self.logger = logger
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild):
<<<<<<< HEAD
        embed = disnake.Embed(title="Joined Guild", color=0x2F3136)
=======
        embed = disnake.Embed(title="Synth | Joined Guild", color=0x2F3136)
>>>>>>> 806890f7f3011613a74d6e889d19da9ca56ca3b0
        embed.add_field(
            name="Guild", value=f"`{guild.name}` / `{guild.id}`", inline=False
        )
        embed.add_field(name="Members", value=f"`{guild.member_count}`", inline=False)
        embed.add_field(
            name="Joined at",
            value=disnake.utils.format_dt(datetime.now(), style="f"),
            inline=False,
        )
        embed.add_field(
            name="Created at",
            value=disnake.utils.format_dt(guild.created_at, style="f"),
            inline=False,
        )
        embed.add_field(
            name="Owner",
            value=f"`@{guild.owner.name}` / `{guild.owner.id}`",
            inline=False,
        )

        channel = await self.bot.fetch_channel(getenv("BOT_LOGS", "id"))
        join_embed = (
            disnake.Embed(
                title="Synth | New Era",
                description=f"""
Hey :wave_tone1:. Thanks for adding our multi-functional bot, Synth.

:rocket: Quick start:
1. Bot prefix: `{await get_prefix(message=guild)}`
2. To get more information about a command, type `{await get_prefix(message=guild)}help <command>`
3. Join our support server — [click](https://discord.gg/7vT3H3tVYp)

Finally, if you have any issues with the bot, you can take a look at the website. You can also join the [Synth Community](https://discord.gg/7vT3H3tVYp) and ask for help.
            """,
                color=0x2F3136,
            )
            .set_thumbnail(url=self.bot.user.avatar)
            .set_image(
<<<<<<< HEAD
                url=(
                    "https://cdn.discordapp.com/attachments/1167873742240755843/1168533333010022410/"
                    "synthbanner.png?ex=65521c78&is=653fa778&hm"
                    "=5481d9be9b4f7e39f60d6ac52677de9b44b2236ceaae8b94c5cfd35348f6167a&"
                )
=======
                url="https://cdn.discordapp.com/attachments/1167873742240755843/1168533333010022410/"
                "synthbanner.png?ex=65521c78&is=653fa778&hm=5481d9be9b4f7e39f60d6ac52677de9b44b2236ceaae8b94c5cfd35348f6167a&"
>>>>>>> 806890f7f3011613a74d6e889d19da9ca56ca3b0
            )
        )

        try:
            await guild.text_channels[0].send(embed=join_embed)
        except (disnake.HTTPException, disnake.Forbidden, TypeError, ValueError):
            await guild.system_channel.send(embed=join_embed)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: disnake.Guild):
<<<<<<< HEAD
        embed = disnake.Embed(title="Left Guild", color=0x2F3136)
=======
        embed = disnake.Embed(title="Synth | Removed Guild", color=0x2F3136)
>>>>>>> 806890f7f3011613a74d6e889d19da9ca56ca3b0
        embed.add_field(
            name="Guild", value=f"`{guild.name}` / `{guild.id}`", inline=False
        )
        embed.add_field(name="Members", value=f"`{guild.member_count}`", inline=False)
        embed.add_field(
            name="Removed at",
            value=disnake.utils.format_dt(datetime.now(), style="f"),
            inline=False,
        )
        embed.add_field(
            name="Owner",
            value=f"`@{guild.owner.name}` / `{guild.owner.id}`",
            inline=False,
        )

<<<<<<< HEAD
        channel = await self.bot.fetch_channel(int(getenv("BOT_LOGS", "id")))
=======
        channel = await self.bot.fetch_channel(getenv("BOT_LOGS", "id"))
>>>>>>> 806890f7f3011613a74d6e889d19da9ca56ca3b0
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: disnake.abc.GuildChannel) -> None:
        logger_channel = await self.logger.get_loggers(
            guild_id=channel.guild.id, to_return="guild"
        )

        if not logger_channel:
            return

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
<<<<<<< HEAD
            name="Created at",
            value=disnake.utils.format_dt(channel.created_at, style="f"),
        )
        embed.add_field(
=======
>>>>>>> 806890f7f3011613a74d6e889d19da9ca56ca3b0
            name="Deleted at",
            value=disnake.utils.format_dt(datetime.now(), style="f"),
            inline=True,
        )
<<<<<<< HEAD
        embed.add_field(name="Channel", value=channel.name)
        embed.add_field(name="ID", value=channel.id)
        embed.add_field(name="Position", value=channel.position)
        embed.add_field(name="Category", value=channel.category or "No Category")

        if channel := channel.guild.get_channel(int(logger_channel)):
            await channel.send(embed=embed)
=======
        embed.add_field(name="Channel", value=f"{channel.name}")

        channel = channel.guild.get_channel(int(logger_channel))
        await channel.send(embed=embed)
>>>>>>> 806890f7f3011613a74d6e889d19da9ca56ca3b0

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: disnake.abc.GuildChannel) -> None:
        logger_channel = await self.logger.get_loggers(
            guild_id=channel.guild.id, to_return="guild"
        )

        if not logger_channel:
            return

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
<<<<<<< HEAD
            value=disnake.utils.format_dt(channel.created_at, style="f"),
        )
        embed.add_field(
            name="Deleted at",
=======
>>>>>>> 806890f7f3011613a74d6e889d19da9ca56ca3b0
            value=disnake.utils.format_dt(datetime.now(), style="f"),
            inline=True,
        )
        embed.add_field(name="Channel", value=f"{channel.mention} (ID: `{channel.id}`)")
<<<<<<< HEAD
        embed.add_field(name="Position", value=channel.position)
        embed.add_field(name="Category", value=channel.category or "No Category")
=======
>>>>>>> 806890f7f3011613a74d6e889d19da9ca56ca3b0

        channel = channel.guild.get_channel(int(logger_channel))
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self,
        before: disnake.abc.GuildChannel,
        after: disnake.abc.GuildChannel,
    ) -> None:
        logger_channel = await self.logger.get_loggers(
            guild_id=before.guild.id, to_return="guild"
        )

        if not logger_channel:
            return

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
<<<<<<< HEAD
=======

        embed.add_field(
            name="Before type of channel", value=before_channel_type, inline=False
        )
>>>>>>> 806890f7f3011613a74d6e889d19da9ca56ca3b0
        embed.add_field(
            name="Edited at",
            value=disnake.utils.format_dt(datetime.now(), style="f"),
            inline=True,
        )
        embed.add_field(name="Channel", value=f"{before.mention} (`ID: {before.id}`)")
        value = []
        if before.name != after.name:
            value.append(f"New name: `{after.name}`\nOld name: `{before.name}`\n")
<<<<<<< HEAD

        if isinstance(before, disnake.TextChannel):
            if before.topic != after.topic:  # type: ignore
                value.append(f"Old topic: `{before.topic}`\nNew topic: `{after.topic}`\n")  # type: ignore

        if before.type != after.type:
            value.append(
                f"Before type of channel: **{before_channel_type}**\nAfter type of channel: **{after_channel_type}**\n"
            )
=======
        if before.topic != after.topic:  # type: ignore
            value.append(f"Old topic: `{before.topic}`\nNew topic: `{after.topic}`\n")  # type: ignore
        value.append(f"After type of channel: **{after_channel_type}**")
>>>>>>> 806890f7f3011613a74d6e889d19da9ca56ca3b0
        embed.set_field_at(
            field_index,
            name="Additional information",
            value="\n".join(value),
            inline=False,
        )
        channel = before.guild.get_channel(int(logger_channel))
        await channel.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EventGuild(bot=bot))
