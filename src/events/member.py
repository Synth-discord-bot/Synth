from disnake import Member
import disnake
from disnake.ext import commands
from src.utils import invites, main_db, logger


class EventMember(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super(EventMember, self).__init__()
        self.bot = bot
        self.invites = invites
        self.settings_db = main_db
        self.logger = logger

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        if member.bot:
            return

        await self.invites.update_invite_info(
            guild_id=member.guild.id,
            # inviter=
        )

    @commands.Cog.listener()
    async def on_member_ban(self, guild: disnake.Guild, member: Member) -> None:
        logger_channel = await self.logger.get_loggers(
            guild_id=guild.id, to_return="guild"
        )
        if not logger_channel:
            return

        embed = disnake.Embed(
            color=self.settings_db.get_embed_color(guild.id),
            title="Synth | Member Banned",
        )

        embed.add_field(
            name="Member",
            value=f"`{member.name}` / `{member.id}` / {member.mention}",
            inline=False,
        )

        embed.set_thumbnail(url=member.avatar.url)

        if channel := logger_channel:
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: disnake.Guild, member: disnake.User) -> None:
        logger_channel = await self.logger.get_loggers(
            guild_id=guild.id, to_return="guild"
        )
        if not logger_channel:
            return

        embed = disnake.Embed(
            color=self.settings_db.get_embed_color(guild.id),
            title="Synth | Member Unbanned",
        )

        embed.add_field(
            name="Member",
            value=f"`{member.name}` / `{member.id}` / {member.mention}",
            inline=False,
        )

        embed.set_thumbnail(url=member.avatar.url)

        if channel := logger_channel:
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        logger_channel = await self.logger.get_loggers(
            guild_id=before.guild.id, to_return="guild"
        )
        if not logger_channel:
            return

        embed = disnake.Embed(
            color=self.settings_db.get_embed_color(before.guild.id),
            title="Synth | Member Updated",
        )
        embed.set_thumbnail(url=before.avatar.url)

        if before.nick != after.nick:
            embed.add_field(
                name="Nickname", value=f"`{before.nick} -> {after.nick}`", inline=False
            )

        if before.roles != after.roles:
            embed.add_field(
                name="Role", value=f"`{before.roles} -> {after.roles}`", inline=False
            )

        if channel := logger_channel:
            await channel.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EventMember(bot=bot))
