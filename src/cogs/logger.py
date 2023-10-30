import datetime

import disnake
from disnake.ext import commands

from src.utils import logger


class LogsCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.logger = logger

    async def cog_load(self):
        await self.logger.fetch_and_cache_all()

    @commands.slash_command(name="logger")
    async def logger(self, _: disnake.ApplicationCommandInteraction):
        pass

    @logger.sub_command(name="set_channel")
    async def set_log_channel(
        self,
        interaction: disnake.MessageCommandInteraction,
        channel: disnake.TextChannel,
    ):
        await interaction.send("Checking channel...", ephemeral=True)
        try:
            await channel.send(".", delete_after=0.05)
            await self.logger.update_logger_info(
                guild_id=interaction.guild.id, logger_channel_id=channel.id
            )
            await interaction.edit_original_message(
                f"New log channel: {channel.mention} "
            )
        except (disnake.HTTPException, disnake.Forbidden):
            await interaction.edit_original_message(
                content="This channel does not have permissions to send messages."
            )

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        if not message.author == message.guild.me:
            message.content = (
                message.content[:1900] + "..."
                if len(message.content) > 1900
                else message.content
            )
            embeds = []
            embed = disnake.Embed(
                color=0x2F3136, title="Deleted Message", description=None
            )
            embed.add_field(name="Additional information", value="No")
            field_dop_index = next(
                index
                for index, field in enumerate(embed.fields)
                if field.name == "Additional information"
            )
            files = []
            embeds.append(embed)

            if message.attachments:
                for num, attachment in enumerate(message.attachments):
                    embed.set_field_at(
                        field_dop_index,
                        name="Additional information",
                        value=f"Number of media files: `{num+1}`",
                    )
                    files.append(await attachment.to_file())

            if message.embeds:
                embed.set_field_at(
                    field_dop_index,
                    name="Additional information",
                    value=f"Number of Embeds Deleted: `{len(message.embeds)}`",
                )
                for num, emb in enumerate(message.embeds):
                    if num + 1 < 9:
                        emb.set_footer(text=f"Number: {num + 1}")
                        embeds.append(emb)

            embed.add_field(
                name="Author",
                value=f"{message.author.mention} (`{message.author}` `ID: {message.author.id}`)",
                inline=False,
            )
            embed.add_field(
                name="Deleted",
                value=disnake.utils.format_dt(datetime.datetime.now(), style="f"),
                inline=True,
            )
            embed.add_field(
                name="Channel",
                value=f"{message.channel.mention} (`ID: {message.channel.id}`)",
            )
            embed.set_thumbnail(url=message.author.avatar)
            logger_channel = await self.logger.get_loggers(guild_id=1109511263509291098)
            channel = message.guild.get_channel(logger_channel[0]["logger_channel_id"])
            await channel.send(embeds=embeds, files=files)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.author == before.guild.me:
            if before.content or after.content:
                before.content = (
                    before.content[:1900] + "..."
                    if len(before.content) > 1900
                    else before.content
                )
                after.content = (
                    after.content[:1900] + "..."
                    if len(after.content) > 1900
                    else after.content
                )
                if before.content == after.content:
                    return
                embed = disnake.Embed(
                    title=f"Edited Message",
                    description=f"Before: {before.content}\nAfter: {after.content}",
                    color=0x2F3136,
                )
                embed.add_field(
                    name=f"Author",
                    value=f"{after.author.mention} (`{after.author}` `ID: {after.author.id}`)",
                    inline=False,
                )
                embed.add_field(
                    name=f"Edited",
                    value=disnake.utils.format_dt(datetime.datetime.now(), style="f"),
                    inline=True,
                )
                embed.add_field(
                    name=f"Channel",
                    value=f"{before.channel.mention} (`ID: {before.channel.id}`)",
                )
                logger_channel = await self.logger.get_loggers(
                    guild_id=1109511263509291098
                )
                channel = before.guild.get_channel(
                    logger_channel[0]["logger_channel_id"]
                )
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: disnake.abc.GuildChannel):
        embed = disnake.Embed(
            title=f"Deleted Channel", description=None, color=0x2F3136
        )
        channel_type = None

        if channel.type == disnake.ChannelType.text:
            channel_type = "Text Channel"
        elif channel.type == disnake.ChannelType.voice:
            channel_type = "Voice Channel"
        elif channel.type == disnake.ChannelType.category:
            channel_type = "Category"
        elif channel.type == disnake.ChannelType.forum:
            channel_type = "Forum"
        else:
            channel_type = "Unknown Type"
        embed.add_field(name=f"Type of channel", value=channel_type, inline=False)
        embed.add_field(
            name=f"Deleted",
            value=disnake.utils.format_dt(datetime.datetime.now(), style="f"),
            inline=True,
        )
        embed.add_field(name=f"Channel", value=f"{channel.name}")
        logger_channel = await self.logger.get_loggers(guild_id=1109511263509291098)
        channel = channel.guild.get_channel(logger_channel[0]["logger_channel_id"])
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: disnake.abc.GuildChannel):
        embed = disnake.Embed(
            title=f"Created Channel", description=None, color=0x2F3136
        )
        channel_type = None
        if channel.type == disnake.ChannelType.text:
            channel_type = "Text Channel"
        elif channel.type == disnake.ChannelType.voice:
            channel_type = "Voice Channel"
        elif channel.type == disnake.ChannelType.category:
            channel_type = "Category"
        elif channel.type == disnake.ChannelType.forum:
            channel_type = "Forum"
        else:
            channel_type = "Unknown Type"
        embed.add_field(name=f"Type of channel", value=channel_type, inline=False)
        embed.add_field(
            name=f"Created",
            value=disnake.utils.format_dt(datetime.datetime.now(), style="f"),
            inline=True,
        )
        embed.add_field(
            name=f"Channel", value=f"{channel.mention} (ID: `{channel.id}`)"
        )
        logger_channel = await self.logger.get_loggers(guild_id=1109511263509291098)
        channel = channel.guild.get_channel(logger_channel[0]["logger_channel_id"])
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self,
        before: disnake.abc.GuildChannel,
        after: disnake.abc.GuildChannel,
    ):
        embed = disnake.Embed(
            title=f"Updated Channel", description=None, color=0x2F3136
        )
        embed.add_field(
            name="Additional information", value="Unknown error❓", inline=False
        )
        field_index = next(
            index
            for index, field in enumerate(embed.fields)
            if field.name == "Additional information"
        )
        channel_type = None
        if before.type == disnake.ChannelType.text:
            channel_type = "Text Channel"
        elif before.type == disnake.ChannelType.voice:
            channel_type = "Voice Channel"
        elif before.type == disnake.ChannelType.category:
            channel_type = "Category"
        elif before.type == disnake.ChannelType.forum:
            channel_type = "Forum"
        else:
            channel_type = "Unknown Type"
        embed.add_field(name=f"Type of channel", value=channel_type, inline=False)
        embed.add_field(
            name=f"Edited",
            value=disnake.utils.format_dt(datetime.datetime.now(), style="f"),
            inline=True,
        )
        embed.add_field(name=f"Channel", value=f"{before.mention} (`ID: {before.id}`)")
        value = []
        if before.name != after.name:
            value.append(f"New name: `{after.name}`\nOld name: `{before.name}`\n")
        if before.topic != after.topic:
            value.append(f"New topic: `{after.topic}`\nOld topic: `{before.topic}`\n")
        embed.set_field_at(
            field_index,
            name="Additional information",
            value="\n".join(value),
            inline=False,
        )
        logger_channel = await self.logger.get_loggers(guild_id=1109511263509291098)
        channel = before.guild.get_channel(logger_channel[0]["logger_channel_id"])
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: disnake.Invite):
        embed = disnake.Embed(title=f"Created Invite", description=None, color=0x2F3136)
        embed.add_field(
            name=f"Channel",
            value=f"{invite.channel.mention} (`ID: {invite.channel.id}`)",
            inline=False,
        )
        embed.add_field(name=f"Link", value=f"{invite.url}", inline=False)
        embed.add_field(
            name=f"Created",
            value=disnake.utils.format_dt(datetime.datetime.now(), style="f"),
            inline=True,
        )
        embed.add_field(
            name=f"Inviter",
            value=f"{invite.inviter.name} (`ID: {invite.inviter.id}`)",
        )
        logger_channel = await self.logger.get_loggers(guild_id=1109511263509291098)
        channel = invite.guild.get_channel(logger_channel[0]["logger_channel_id"])
        await channel.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(LogsCog(bot))
