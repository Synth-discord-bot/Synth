import asyncio
import datetime
import time
from typing import Union, List, Any

import disnake
from disnake import Embed, Message
from disnake.ext import commands
from disnake.ext.commands import UserConverter, MemberConverter
from disnake.ui import ActionRow

from src.utils import warns, main_db
from src.utils.misc import emoji, str_to_seconds, hms, common_checks


class Moderation(commands.Cog):
    """Commands to moderate your server."""

    EMOJI = "<:hammer:1169685339720384512>"

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.warns = warns
        self.settings_db = main_db

    async def cog_load(self) -> None:
        await self.warns.fetch_and_cache_all()

    @commands.slash_command(name="ban", description="Ban a user")
    async def ban(
        self,
        interaction: disnake.MessageCommandInteraction,
        user: disnake.Member,
        *,
        reason: str = None,
    ) -> None:
        embed = Embed(color=self.settings_db.get_embed_color(interaction.guild.id))

        check_result, error_embed = await common_checks(interaction, user.id)
        if not check_result:
            return await interaction.send(embed=error_embed)

        embed.title = "<:ban:1170712517308317756> Successfully banned"
        embed.description = (
            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
            f"**Member:** {user.mention} ({user})\n"
            f"**Reason:** {reason}"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await interaction.send(embed=embed)

        try:
            embed.title = "<:ban:1170712517308317756> You were banned"
            embed.description = (
                f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
                f"**Reason:** {reason}\n"
                f"**Server:** {interaction.guild.name}"
            )
            await user.send(embed=embed)
        except (Exception, BaseException, disnake.Forbidden):
            pass

        await interaction.guild.ban(user, reason=f"{interaction.user}: {reason}")

    @commands.slash_command(name="unban", description="Unban a user")
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def unban(
        self,
        interaction: disnake.MessageCommandInteraction,
        member: disnake.Member,
    ) -> Message:
        check_result, error_embed = await common_checks(
            interaction, member.id, for_unban=True
        )
        if not check_result:
            return await interaction.send(embed=error_embed)

        embed = Embed(color=self.settings_db.get_embed_color(interaction.guild.id))
        embed.title = "<:invite:1169690514430382160> Successfully unbanned"
        embed.description = (
            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
            f"**Member:** {member.mention} (`{id}`)"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )

        await interaction.guild.unban(member)
        await interaction.send(embed=embed)

    @commands.slash_command(name="kick", description="Kick a user")
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def kick(
        self,
        interaction: disnake.MessageCommandInteraction,
        member: disnake.Member,
        *,
        reason: str = None,
    ) -> Message:
        embed = Embed(color=self.settings_db.get_embed_color(interaction.guild.id))

        check_result, error_embed = await common_checks(interaction, member.id)
        if not check_result:
            return await interaction.send(embed=error_embed)

        embed.title = "<:kick:1170712514288435271> Successfully kicked"
        embed.description = (
            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
            f"**Member:** {member.mention} ({member})\n"
            f"**Reason:** {reason}"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await interaction.send(embed=embed)

        try:
            embed.title = "<:kick:1170712514288435271> You were kicked"
            embed.description = (
                f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
                f"**Reason:** {reason}\n"
                f"**Server:** {interaction.guild.name}"
            )
            embed.set_footer(
                text=f"Synth © 2023 | All Rights Reserved",
                icon_url=self.bot.user.avatar,
            )
            await member.send(embed=embed)

        except (Exception, BaseException, disnake.Forbidden):
            pass

        await member.kick(reason=reason)

    @commands.slash_command(name="mute", description="Mute a user")
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def mute(
        self,
        interaction: disnake.MessageCommandInteraction,
        member: disnake.Member,
        mute_time: str,
        *,
        reason: str = None,
    ) -> Message:
        embed = Embed(color=self.settings_db.get_embed_color(interaction.guild.id))
        error_embed = Embed(color=disnake.Color.red())

        try:
            str_time = await str_to_seconds(mute_time)
        except ValueError:
            error_embed.description = f"{emoji('error')} | Invalid mute time format."
            error_embed.set_footer(
                text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
            )
            return await interaction.send(embed=error_embed)

        check_result, error_embed = await common_checks(
            interaction, member, for_mute=True, str_time=str_time
        )
        if not check_result:
            return await interaction.send(embed=error_embed)

        embed.title = "<:mute:1170712518725992529> Successfully muted"
        embed.description = (
            f"**Member:** {member.mention} ({member})\n"
            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
            f"**Time:** {str(await hms(float(str_time)))}\n"
            f"**Reason:** {reason}\n"
            f"**Unmute date:** <t:{int(time.time()) + str_time}>"
        )
        embed.set_footer(
            text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )

        await member.edit(
            timeout=disnake.utils.utcnow() + datetime.timedelta(seconds=str_time)
        )
        await interaction.send(embed=embed)

        try:
            embed.title = "<:mute:1170712518725992529> You were muted"
            embed.description = (
                f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
                f"**Server:** {interaction.guild.name}\n"
                f"**Time:** {str(await hms(float(str_time)))}\n"
                f"**Reason:** {reason}\n"
                f"**Unmute date:** <t:{int(time.time() + float(str_time))}>"
            )
            embed.set_footer(
                text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
            )
            await member.send(embed=embed)
        except (Exception, BaseException, disnake.Forbidden):
            pass

    @commands.slash_command(name="unmute", description="Unmute a user")
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def unmute(
        self,
        interaction: disnake.MessageCommandInteraction,
        member: disnake.Member,
    ):
        embed = Embed(color=self.settings_db.get_embed_color(interaction.guild.id))

        check_result, error_embed = await common_checks(interaction, member)
        if not check_result:
            return await interaction.send(embed=error_embed)

        if member == interaction.user:
            error_embed.description = f"{emoji('error')} | You can't unmute yourself!"
            error_embed.set_footer(
                text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
            )
            return await interaction.send(embed=error_embed)

        embed.title = "<:unmute:1169690521472614500> Successfully unmuted"
        embed.description = (
            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
            f"**Member:** {member.mention} ({member})"
        )
        embed.set_footer(
            text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )

        await member.edit(timeout=None)
        await interaction.send(embed=embed)

        try:
            embed.title = "<:unmute:1169690521472614500> You were unmuted"
            embed.description = (
                f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
                f"**Server:** {interaction.guild.name}\n"
            )
            embed.set_footer(
                text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
            )
            await member.send(embed=embed)
        except (Exception, BaseException, disnake.Forbidden):
            pass

    @commands.slash_command(name="mutes", description="View all mutes")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def mutes(self, interaction: disnake.MessageCommandInteraction) -> Message:
        pages = []
        per_page = 5
        total = 0
        index = 0

        for member in [
            m
            for m in interaction.guild.members
            if not m.bot and m.current_timeout is not None
        ]:
            total += 1
            timeout = member.current_timeout
            pages.append(
                f"`[{total}]` **{member.mention}** - "
                f"<t:{round(timeout.timestamp())}:F> "
                f"(<t:{round(timeout.timestamp())}:R>)"
            )

        if not pages:
            embed = disnake.Embed(
                color=self.settings_db.get_embed_color(interaction.guild.id),
                description="There are currently no mutes on this server.",
            )
            embed.set_footer(text=interaction.user, icon_url=interaction.user.avatar)
            return await interaction.send(embed=embed)

        total_pages = (total + per_page - 1) // per_page

        async def refresh_buttons():
            buttons = (
                [
                    ActionRow(
                        disnake.ui.Button(
                            custom_id="back",
                            emoji="◀️",
                            style=disnake.ButtonStyle.blurple,
                            disabled=index == 0,
                        ),
                        disnake.ui.Button(
                            custom_id="forward",
                            emoji="▶️",
                            style=disnake.ButtonStyle.blurple,
                            disabled=index == total_pages - 1,
                        ),
                        disnake.ui.Button(
                            custom_id="close",
                            emoji="<:delete:1169690519677440093>",
                            style=disnake.ButtonStyle.danger,
                        ),
                    )
                ]
                if total_pages > 1
                else [
                    ActionRow(
                        disnake.ui.Button(
                            custom_id="close",
                            emoji="<:delete:1169690519677440093>",
                            style=disnake.ButtonStyle.danger,
                        )
                    )
                ]
            )
            return buttons

        async def refresh_embed():
            mutes_embed: Embed = disnake.Embed(
                title="<:calendar:1169690539168366712> Active mutes",
                color=self.settings_db.get_embed_color(interaction.guild.id),
            )

            if total_pages <= 1:
                mutes_embed.set_footer(
                    text=f"{interaction.user}", icon_url=interaction.user.avatar
                )
            else:
                mutes_embed.set_footer(
                    text=f"{interaction.user} | Page {index + 1} of {total_pages}",
                    icon_url=interaction.user.avatar,
                )

            start = index * per_page
            for page in pages[start : (index + 1) * per_page]:
                mutes_embed.add_field(name="", value=page, inline=False)
            return mutes_embed

        embed: Embed = await refresh_embed()
        msg: Message = await interaction.send(
            embed=embed, components=await refresh_buttons()
        )

        while True:
            try:
                inter = await self.bot.wait_for(
                    "button_click",
                    check=lambda i: i.message.id == msg.id
                    and i.author == interaction.user,
                    timeout=600,
                )
            except asyncio.TimeoutError:
                break

            match inter.component.custom_id:
                case "back":
                    index = max(index - 1, 0)
                case "forward":
                    index = min(index + 1, total_pages - 1)
                case "close":
                    break

            await msg.edit(
                embed=await refresh_embed(), components=await refresh_buttons()
            )
            await inter.response.defer(ephemeral=True)

        await msg.delete()

    @commands.slash_command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def bans(self, interaction: disnake.MessageCommandInteraction) -> Message:
        pages = []
        per_page = 5
        total = 0
        index = 0

        async for ban in interaction.guild.bans(limit=200):
            if not ban.user.bot:
                member = ban.user
                reason = ban.reason if ban.reason else "No Reason"
                total += 1
                pages.append(f"`[{total}]` **{member}** - {reason}")

        if not pages:
            embed = disnake.Embed(
                color=self.settings_db.get_embed_color(interaction.guild.id),
                description="There are currently no bans on this server.",
            )
            embed.set_footer(text=interaction.user, icon_url=interaction.user.avatar)
            return await interaction.send(embed=embed)

        total_pages = (total + per_page - 1) // per_page

        async def refresh_buttons():
            buttons = (
                [
                    ActionRow(
                        disnake.ui.Button(
                            custom_id="back",
                            emoji="◀️",
                            style=disnake.ButtonStyle.blurple,
                            disabled=index == 0,
                        ),
                        disnake.ui.Button(
                            custom_id="forward",
                            emoji="▶️",
                            style=disnake.ButtonStyle.blurple,
                            disabled=index == total_pages - 1 and index != 0,
                        ),
                        disnake.ui.Button(
                            custom_id="close",
                            emoji="<:delete:1169690519677440093>",
                            style=disnake.ButtonStyle.danger,
                        ),
                    )
                ]
                if total_pages > 1
                else [
                    ActionRow(
                        disnake.ui.Button(
                            custom_id="close",
                            emoji="<:delete:1169690519677440093>",
                            style=disnake.ButtonStyle.danger,
                        )
                    )
                ]
            )
            return buttons

        async def refresh_embed():
            bans_embed: Embed = disnake.Embed(
                title="<:calendar:1169690539168366712> Active bans",
                color=self.settings_db.get_embed_color(interaction.guild.id),
            )
            if total_pages > 1:
                bans_embed.set_footer(
                    text=f"{interaction.user} | Page {index + 1} of {total_pages}",
                    icon_url=interaction.user.avatar,
                )
            else:
                bans_embed.set_footer(
                    text=f"{interaction.user}", icon_url=interaction.user.avatar
                )

            start = index * per_page
            for page in pages[start : (index + 1) * per_page]:
                bans_embed.add_field(name="", value=page, inline=False)
            return bans_embed

        embed = await refresh_embed()
        msg = await interaction.send(embed=embed, components=await refresh_buttons())

        def check(interaction: disnake.MessageInteraction) -> bool:
            return (
                interaction.message.id == msg.id
                and interaction.user == interaction.user
            )

        while True:
            try:
                inter = await self.bot.wait_for(
                    "button_click", check=check, timeout=600
                )
            except asyncio.TimeoutError:
                break

            if inter.component.custom_id == "back":
                index = max(index - 1, 0)
            elif inter.component.custom_id == "forward":
                index = min(index + 1, total_pages - 1)
            elif inter.component.custom_id == "close":
                break

            await msg.edit(
                embed=await refresh_embed(), components=await refresh_buttons()
            )
            await inter.response.defer(ephemeral=True)

        await msg.delete()

    @commands.slash_command(name="warn", description="Warn a user")
    @commands.has_permissions(administrator=True)
    async def warn(
        self,
        interaction: disnake.MessageCommandInteraction,
        member: disnake.Member,
        *,
        reason=None,
    ):
        check_result, error_embed = await common_checks(
            interaction, member, check_bot=True
        )
        if not check_result:
            return await interaction.send(embed=error_embed)

        case = await self.warns.add_warn(
            interaction.guild.id, interaction.user, member, reason
        )

        embed = Embed(
            title=f"<:icons_warning:1170751866905296978> Warned {member} (Case #{case})",
            color=self.settings_db.get_embed_color(interaction.guild.id),
        )
        embed.add_field(
            name="**Administrator:**",
            value=f"{interaction.user.mention} ({interaction.user})",
            inline=False,
        )
        embed.add_field(
            name="**Member:**", value=f"{member.mention} ({member})", inline=False
        )
        embed.add_field(name="**Reason:**", value=reason, inline=False)

        embed.set_thumbnail(url=str(member.display_avatar.url))
        embed.set_footer(
            text="Synth © 2023 | All Rights Reserved",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
        )
        await interaction.send(embed=embed)

    @commands.slash_command(name="warns", description="View a user's warns")
    @commands.has_permissions(administrator=True)
    async def warns(
        self,
        interaction: disnake.MessageCommandInteraction,
        user: disnake.Member = None,
    ):
        check_result, error_embed = await common_checks(
            interaction, user, check_bot=True
        )
        if not check_result:
            return await interaction.send(embed=error_embed)

        warnings = await self.warns.get_user_warnings(interaction.guild.id, user)

        index = 0
        total_pages = (len(warnings) + 4) // 5

        async def refresh_buttons(ind: int, total_p: int):
            prev_button = disnake.ui.Button(
                label="️◀️",
                style=disnake.ButtonStyle.blurple,
                custom_id=f"warns_prev:{ind}",
                disabled=ind == 0,
            )
            next_button = disnake.ui.Button(
                label="▶️",
                style=disnake.ButtonStyle.blurple,
                custom_id=f"warns_next:{ind}",
                disabled=ind == (total_p - 1 if total_p > 0 else 0),
            )
            delete_button = disnake.ui.Button(
                style=disnake.ButtonStyle.red,
                custom_id="delete_warns",
                emoji="<:delete:1169690519677440093>",
            )
            return [prev_button, next_button, delete_button]

        async def refresh_embed(
            context: disnake.MessageCommandInteraction, warns_list: List[Any], i, _
        ):
            warns_embed = Embed(
                title=f"Warns of {user}",
                description=f"**Total warns count:** {len(warns_list)}",
                color=self.settings_db.get_embed_color(interaction.guild.id),
            )
            warns_embed.set_thumbnail(url=user.avatar)

            per_page = 5
            start = i * per_page
            end = (i + 1) * per_page

            for ind, warning in enumerate(warns_list[start:end], start=start + 1):
                timestamp = warning["timestamp"]
                administrator = context.guild.get_member(int(warning["moderator_id"]))
                reason = warning["reason"]
                warns_embed.add_field(
                    name=f"Warn #{ind}",
                    value=f"Administrator: {administrator.mention}\n"
                    f"Timestamp: {timestamp}\n"
                    f"Reason: {reason}",
                    inline=False,
                )
            return warns_embed

        embed = await refresh_embed(interaction, warnings, index, total_pages)
        buttons = await refresh_buttons(index, total_pages)
        msg = await interaction.send(
            embed=embed, components=[disnake.ui.ActionRow(*buttons)]
        )

        while True:
            try:
                inter = await self.bot.wait_for(
                    "button_click",
                    check=lambda i: i.message.id == msg.id
                    and i.user == interaction.user,
                    timeout=600,
                )
            except asyncio.TimeoutError:
                break

            if inter.data.custom_id.startswith("warns_prev:"):
                index = max(0, index - 1)
            elif inter.data.custom_id.startswith("warns_next:"):
                index = min(total_pages - 1, index + 1)
            elif inter.data.custom_id == "delete_warns":
                await msg.delete()

            embed = await refresh_embed(interaction, warnings, index, total_pages)
            buttons = await refresh_buttons(index, total_pages)
            await inter.response.edit_message(
                embed=embed, components=[disnake.ui.ActionRow(*buttons)]
            )

    @commands.slash_command(name="remove_warn", description="Remove a user's warns")
    @commands.has_permissions(administrator=True)
    async def remove_warn(
        self,
        interaction: disnake.MessageCommandInteraction,
        user: disnake.Member,
        amount: int = 1,
    ):
        check_result, error_embed = await common_checks(
            interaction, user, check_bot=True
        )
        if not check_result:
            return await interaction.send(embed=error_embed)

        count_deleted = await self.warns.delete_warnings(
            interaction.guild.id, user.id, amount
        )
        if isinstance(count_deleted, int):
            embed = Embed(
                title=f"Removed {count_deleted} warns",
                description=f"Administrator: {interaction.user.mention} ({interaction.user})\n"
                f"Member: {interaction.guild.get_member(user.id).mention} ({interaction.guild.get_member(user.id)})",
                color=self.settings_db.get_embed_color(interaction.guild.id),
            )
            embed.set_thumbnail(
                url=str(interaction.guild.get_member(user.id).display_avatar.url)
            )
            embed.set_footer(
                text=f"Synth © 2023 | All Rights Reserved",
                icon_url=self.bot.user.avatar,
            )
            await interaction.send(embed=embed)
        else:
            error_embed.description = (
                f"{emoji('error')} | Sorry, I couldn't remove any warns"
            )
            error_embed.set_footer(
                text=f"Synth © 2023 | All Rights Reserved",
                icon_url=self.bot.user.avatar,
            )
            return await interaction.send(embed=error_embed)

    @commands.slash_command(name="cross_ban", description="Ban a user from all servers")
    @commands.has_permissions(administrator=True)
    async def cross_ban(
        self,
        interaction: disnake.MessageCommandInteraction,
        member: disnake.Member,
        reason: str = None,
    ):
        embed = Embed(color=self.settings_db.get_embed_color(interaction.guild.id))
        success_servers = []

        check_result, error_embed = await common_checks(interaction, member)
        if not check_result:
            return await interaction.send(embed=error_embed)

        if not member:
            member = interaction.user

        for guild in self.bot.guilds:
            author_permissions = (
                await guild.fetch_member(interaction.user.id)
            ).guild_permissions
            if not author_permissions.administrator:
                continue

            if member := await guild.fetch_member(member.id):
                try:
                    await guild.ban(member)

                    if not guild == interaction.guild:
                        embed.title = "<:ban:1170712517308317756> Crossban"
                        embed.description = (
                            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
                            f"**Member:** {member} (`{member.id}`)\n"
                            f"**Reason:** {reason}"
                        )
                        embed.set_footer(
                            text=f"Synth © 2023 | All Rights Reserved",
                            icon_url=self.bot.user.avatar,
                        )
                        await guild.text_channels[0].send(embed=embed)

                    success_servers.append(guild.name)
                except (disnake.HTTPException, disnake.Forbidden):
                    error_embed.title = "<:ban:1170712517308317756> Crossban Fail"
                    error_embed.description = (
                        f"Failed to ban {member.mention} on **{guild.name}** guild."
                    )
                    error_embed.set_footer(
                        text=f"Synth © 2023 | All Rights Reserved",
                        icon_url=self.bot.user.avatar,
                    )
                    await interaction.send(embed=embed)
                    continue

        embed.title = "<:ban:1170712517308317756> Crossban Success"
        embed.description = (
            f"**Banned from {len(success_servers)} servers.**\n"
            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
            f"**Member:** {member} (`{member.id}`)\n"
            f"**Reason:** {reason}"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await interaction.send(embed=embed)

    @commands.slash_command(
        name="crosskick", description="Kick a user from all servers"
    )
    @commands.has_permissions(administrator=True)
    async def cross_kick(
        self,
        interaction: disnake.MessageCommandInteraction,
        member: disnake.Member,
        reason: str = None,
    ):
        error_embed = Embed(color=disnake.Color.red())
        embed = Embed(color=self.settings_db.get_embed_color(interaction.guild.id))
        success_servers = []

        if not member:
            member = interaction.user

        member = (
            await interaction.guild.fetch_member(member)
            if isinstance(member, int)
            else await MemberConverter().convert(interaction, member)
            if isinstance(member, str)
            else member
        )

        common_check_result, error_embed = await common_checks(
            interaction, member, check_bot=False
        )
        if not common_check_result:
            return await interaction.send(embed=error_embed)

        for guild in self.bot.guilds:
            author_permissions = (
                await guild.fetch_member(interaction.user.id)
            ).guild_permissions
            if not author_permissions.administrator:
                continue

            if member := await guild.fetch_member(member.id):
                try:
                    await guild.kick(member)

                    if not guild == interaction.guild:
                        embed.title = "<:kick:1170712514288435271> Crosskick"
                        embed.description = (
                            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
                            f"**Member:** {member} (`{member.id}`)\n"
                            f"**Reason:** {reason}"
                        )
                        embed.set_footer(
                            text=f"Synth © 2023 | All Rights Reserved",
                            icon_url=self.bot.user.avatar,
                        )
                        await guild.text_channels[0].send(embed=embed)

                    success_servers.append(guild.name)
                except (disnake.HTTPException, disnake.Forbidden):
                    error_embed.title = "<:kick:1170712514288435271> Crosskick Fail"
                    error_embed.description = (
                        f"Failed to kick {member.mention} on **{guild.name}** guild."
                    )
                    error_embed.set_footer(
                        text=f"Synth © 2023 | All Rights Reserved",
                        icon_url=self.bot.user.avatar,
                    )
                    await interaction.send(embed=embed)
                    continue

        embed.title = "<:kick:1170712514288435271> Crosskick Success"
        embed.description = (
            f"**Kicked from {len(success_servers)} servers.**\n"
            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
            f"**Member:** {member} (`{member.id}`)\n"
            f"**Reason:** {reason}"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await interaction.send(embed=embed)

    @commands.slash_command(name="crossmute")
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def cross_mute(
        self,
        interaction: disnake.MessageCommandInteraction,
        member: disnake.Member,
        mute_time: str,
        *,
        reason: str = None,
    ):
        embed = Embed(color=self.settings_db.get_embed_color(interaction.guild.id))
        success_servers = []

        if not member:
            member = interaction.user

        common_check_result, error_embed = await common_checks(
            interaction, member, check_bot=False, for_mute=True
        )
        if not common_check_result:
            return await interaction.send(embed=error_embed)

        try:
            str_time = await str_to_seconds(mute_time)
        except ValueError:
            error_embed.description = f"{emoji('error')} | Invalid mute time format."
            error_embed.set_footer(
                text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
            )
            return await interaction.send(embed=error_embed)

        for guild in self.bot.guilds:
            author_permissions = (
                await guild.fetch_member(interaction.user.id)
            ).guild_permissions
            if not author_permissions.administrator:
                continue

            if member := await guild.fetch_member(member.id):
                try:
                    timeout = disnake.utils.utcnow() + datetime.timedelta(
                        seconds=str_time
                    )
                    await member.edit(timeout=timeout)
                    if not guild == interaction.guild:
                        embed.title = "<:mute:1170712518725992529> Crossmute"
                        embed.description = (
                            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
                            f"**Member:** {member} (`{member.id}`)\n"
                            f"**Time:** {str(await hms(float(str_time)))}\n"
                            f"**Unmute date:** <t:{int(time.time()) + str_time}>"
                            f"**Reason:** {reason}"
                        )
                        embed.set_footer(
                            text=f"Synth © 2023 | All Rights Reserved",
                            icon_url=self.bot.user.avatar,
                        )
                        await guild.text_channels[0].send(embed=embed)

                    success_servers.append(guild.name)
                except (disnake.HTTPException, disnake.Forbidden):
                    error_embed.title = "<:mute:1170712518725992529> Crossmute Fail"
                    error_embed.description = (
                        f"Failed to mute {member.mention} on **{guild.name}** guild."
                    )
                    error_embed.set_footer(
                        text=f"Synth © 2023 | All Rights Reserved",
                        icon_url=self.bot.user.avatar,
                    )
                    await interaction.send(embed=embed)
                    continue

        embed.title = "<:mute:1170712518725992529> Crossmute Success"
        embed.description = (
            f"**Muted on {len(success_servers)} servers.**\n"
            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
            f"**Member:** {member} (`{member.id}`)\n"
            f"**Time:** {str(await hms(float(str_time)))}\n"
            f"**Unmute date:** <t:{int(time.time()) + str_time}>"
            f"**Reason:** {reason}"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await interaction.send(embed=embed)

    @commands.slash_command(name="crosswarn")
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def crosswarn(
        self,
        interaction: disnake.MessageCommandInteraction,
        member: disnake.Member,
        *,
        reason: str = None,
    ):
        embed = Embed(color=self.settings_db.get_embed_color(interaction.guild.id))
        success_servers = []

        if not member:
            member = interaction.user

        common_check_result, error_embed = await common_checks(
            interaction, member, check_bot=False
        )
        if not common_check_result:
            return await interaction.send(embed=error_embed)

        for guild in self.bot.guilds:
            author_permissions = (
                await guild.fetch_member(interaction.user.id)
            ).guild_permissions
            if not author_permissions.administrator:
                continue

            if member := await guild.fetch_member(member.id):
                try:
                    case = await self.warns.add_warn(
                        interaction.guild.id, interaction.user, member, reason
                    )
                    if not guild == interaction.guild:
                        embed.title = "<:hammer:1169685339720384512> Crosswarn"
                        embed.description = (
                            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
                            f"**Member:** {member} (`{member.id}`)\n"
                            f"**Warn Number:** #{case}\n"
                            f"**Reason:** {reason}"
                        )
                        embed.set_footer(
                            text=f"Synth © 2023 | All Rights Reserved",
                            icon_url=self.bot.user.avatar,
                        )
                        await guild.text_channels[0].send(embed=embed)

                    success_servers.append(guild.name)
                except (Exception, BaseException, disnake.Forbidden):
                    error_embed.title = "<:hammer:1169685339720384512> Crosswarn Fail"
                    error_embed.description = (
                        f"Failed to warn {member.mention} on **{guild.name}** guild."
                    )
                    error_embed.set_footer(
                        text=f"Synth © 2023 | All Rights Reserved",
                        icon_url=self.bot.user.avatar,
                    )
                    await interaction.send(embed=embed)
                    continue

        embed.title = "<:hammer:1169685339720384512> Crosswarn Success"
        embed.description = (
            f"**Warned on {len(success_servers)} servers.**\n"
            f"**Administrator:** {interaction.user.mention} ({interaction.user})\n"
            f"**Member:** {member} (`{member.id}`)\n"
            f"**Reason:** {reason}"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
