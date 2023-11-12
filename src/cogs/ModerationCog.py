import asyncio
import datetime
import time
from typing import Union, List, Any

import disnake
from disnake import Embed, Message
from disnake.ext import commands
from disnake.ext.commands import UserConverter, MemberConverter
from disnake.ui import ActionRow

from src.utils import warns
from src.utils.misc import emoji, str_to_seconds, hms, common_checks


class Moderation(commands.Cog):
    """Helper commands for server moderation"""

    EMOJI = "<:hammer:1169685339720384512>"

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.warns = warns

    async def cog_load(self) -> None:
        await self.warns.fetch_and_cache_all()

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def ban(
        self, ctx, user: Union[int, str, disnake.Member], *, reason: str = None
    ) -> None:
        embed = Embed(color=0x2F3236)

        member = (
            user.id
            if isinstance(user, disnake.Member)
            else await UserConverter().convert(ctx, str(user))
        )

        check_result, error_embed = await common_checks(ctx, member)
        if not check_result:
            return await ctx.send(embed=error_embed)

        embed.title = "<:ban:1170712517308317756> Successfully banned"
        embed.description = (
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
            f"**Member:** {member.mention} ({member})\n"
            f"**Reason:** {reason}"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await ctx.send(embed=embed)

        try:
            embed.title = "<:ban:1170712517308317756> You were banned"
            embed.description = (
                f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
                f"**Reason:** {reason}\n"
                f"**Server:** {ctx.guild.name}"
            )
            await member.send(embed=embed)
        except (Exception, BaseException, disnake.Forbidden):
            pass

        await ctx.guild.ban(member, reason=f"{ctx.author}: {reason}")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def unban(
        self, ctx: commands.Context, user: Union[int, str, disnake.Member]
    ) -> Message:
        member = (
            user.id
            if isinstance(user, disnake.Member)
            else await UserConverter().convert(ctx, str(user))
        )

        check_result, error_embed = await common_checks(ctx, member, for_unban=True)
        if not check_result:
            return await ctx.send(embed=error_embed)

        embed = Embed(color=0x2F3236)
        embed.title = "<:invite:1169690514430382160> Successfully unbanned"
        embed.description = (
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
            f"**Member:** {member.mention} (`{id}`)"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )

        await ctx.guild.unban(member)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def kick(
        self,
        ctx: commands.Context,
        user: Union[int, str, disnake.Member],
        *,
        reason: str = None,
    ) -> Message:
        embed = Embed(color=0x2F3236)

        if isinstance(user, disnake.Member):
            member = user.id
        else:
            member = await MemberConverter().convert(ctx, str(user))

        check_result, error_embed = await common_checks(ctx, member)
        if not check_result:
            return await ctx.send(embed=error_embed)

        embed.title = "<:kick:1170712514288435271> Successfully kicked"
        embed.description = (
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
            f"**Member:** {member.mention} ({member})\n"
            f"**Reason:** {reason}"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await ctx.send(embed=embed)

        try:
            embed.title = "<:kick:1170712514288435271> You were kicked"
            embed.description = (
                f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
                f"**Reason:** {reason}\n"
                f"**Server:** {ctx.guild.name}"
            )
            embed.set_footer(
                text=f"Synth © 2023 | All Rights Reserved",
                icon_url=self.bot.user.avatar,
            )
            await member.send(embed=embed)

        except (Exception, BaseException, disnake.Forbidden):
            pass

        await member.kick(reason=reason)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def mute(
        self,
        ctx: commands.Context,
        member: Union[int, str, disnake.Member],
        mute_time: str,
        *,
        reason: str = None,
    ) -> Message:
        embed = Embed(color=0x2F3236)
        error_embed = Embed(color=disnake.Color.red())

        member = (
            await ctx.guild.fetch_member(member)
            if isinstance(member, int)
            else await MemberConverter().convert(ctx, str(member))
            if isinstance(member, str)
            else member
        )

        try:
            str_time = await str_to_seconds(mute_time)
        except ValueError:
            error_embed.description = f"{emoji('error')} | Invalid mute time format."
            error_embed.set_footer(
                text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
            )
            return await ctx.send(embed=error_embed)

        check_result, error_embed = await common_checks(
            ctx, member, for_mute=True, str_time=str_time
        )
        if not check_result:
            return await ctx.send(embed=error_embed)

        embed.title = "<:mute:1170712518725992529> Successfully muted"
        embed.description = (
            f"**Member:** {member.mention} ({member})\n"
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
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
        await ctx.send(embed=embed)

        try:
            embed.title = "<:mute:1170712518725992529> You were muted"
            embed.description = (
                f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
                f"**Server:** {ctx.guild.name}\n"
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

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def unmute(self, ctx, member: Union[int, str, disnake.Member]):
        embed = Embed(color=0x2F3236)

        member = (
            member
            if isinstance(member, disnake.Member)
            else await MemberConverter().convert(ctx, str(member))
        )

        check_result, error_embed = await common_checks(ctx, member)
        if not check_result:
            return await ctx.send(embed=error_embed)

        if member == ctx.author:
            error_embed.description = f"{emoji('error')} | You can't unmute yourself!"
            error_embed.set_footer(
                text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
            )
            return await ctx.send(embed=error_embed)

        embed.title = "<:unmute:1169690521472614500> Successfully unmuted"
        embed.description = (
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
            f"**Member:** {member.mention} ({member})"
        )
        embed.set_footer(
            text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )

        await member.edit(timeout=None)
        await ctx.send(embed=embed)

        try:
            embed.title = "<:unmute:1169690521472614500> You were unmuted"
            embed.description = (
                f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
                f"**Server:** {ctx.guild.name}\n"
            )
            embed.set_footer(
                text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
            )
            await member.send(embed=embed)
        except (Exception, BaseException, disnake.Forbidden):
            pass

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def mutes(self, ctx: commands.Context) -> Message:
        pages = []
        per_page = 5
        total = 0
        index = 0

        for member in [
            m for m in ctx.guild.members if not m.bot and m.current_timeout is not None
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
                color=0x2F3136,
                description="There are currently no mutes on this server.",
            )
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)
            return await ctx.send(embed=embed)

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
                title="<:calendar:1169690539168366712> Active mutes", color=0x2F3136
            )

            if total_pages <= 1:
                mutes_embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar)
            else:
                mutes_embed.set_footer(
                    text=f"{ctx.author} | Page {index + 1} of {total_pages}",
                    icon_url=ctx.author.avatar,
                )

            for page in pages[index * per_page : (index + 1) * per_page]:
                mutes_embed.add_field(name="", value=page, inline=False)
            return mutes_embed

        embed: Embed = await refresh_embed()
        msg: Message = await ctx.send(embed=embed, components=await refresh_buttons())

        while True:
            try:
                inter = await self.bot.wait_for(
                    "button_click",
                    check=lambda i: i.message.id == msg.id and i.author == ctx.author,
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

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def bans(self, ctx: commands.Context) -> Message:
        pages = []
        per_page = 5
        total = 0
        index = 0

        async for ban in ctx.guild.bans(limit=200):
            if not ban.user.bot:
                member = ban.user
                reason = ban.reason if ban.reason else "No Reason"
                total += 1
                pages.append(f"`[{total}]` **{member}** - {reason}")

        if not pages:
            embed = disnake.Embed(
                color=0x2F3136,
                description="There are currently no bans on this server.",
            )
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)
            return await ctx.send(embed=embed)

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
                title="<:calendar:1169690539168366712> Active bans", color=0x2F3136
            )
            if total_pages > 1:
                bans_embed.set_footer(
                    text=f"{ctx.author} | Page {index + 1} of {total_pages}",
                    icon_url=ctx.author.avatar,
                )
            else:
                bans_embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar)
            for page in pages[index * per_page : (index + 1) * per_page]:
                bans_embed.add_field(name="", value=page, inline=False)
            return bans_embed

        embed = await refresh_embed()
        msg = await ctx.send(embed=embed, components=await refresh_buttons())

        def check(interaction: disnake.MessageInteraction) -> bool:
            return interaction.message.id == msg.id and interaction.author == ctx.author

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

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: Union[int, str, disnake.Member], *, reason=None):
        member = (
            await ctx.guild.fetch_member(member)
            if isinstance(member, int)
            else await MemberConverter().convert(ctx, member)
            if isinstance(member, str)
            else member
        )

        check_result, error_embed = await common_checks(ctx, member, check_bot=True)
        if not check_result:
            return await ctx.send(embed=error_embed)

        case = await self.warns.add_warn(ctx.guild.id, ctx.author, member, reason)

        embed = Embed(
            title=f"<:icons_warning:1170751866905296978> Warned {member} (Case #{case})",
            color=0x2F3136,
        )
        embed.add_field(
            name="**Administrator:**",
            value=f"{ctx.author.mention} ({ctx.author})",
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
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def warns(self, ctx, user: Union[int, str, disnake.Member] = None):
        user = (
            await ctx.guild.fetch_member(user)
            if isinstance(user, int)
            else await MemberConverter().convert(ctx, user)
            if isinstance(user, str)
            else user
        )

        check_result, error_embed = await common_checks(ctx, user, check_bot=True)
        if not check_result:
            return await ctx.send(embed=error_embed)

        warnings = await self.warns.get_user_warnings(ctx.guild.id, user)

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
            context: commands.Context, warns_list: List[Any], i, total_pages
        ):
            warns_embed = Embed(
                title=f"Warns of {user}",
                description=f"**Total warns count:** {len(warns_list)}",
                color=0x2F3136,
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

        embed = await refresh_embed(ctx, warnings, index, total_pages)
        buttons = await refresh_buttons(index, total_pages)
        msg = await ctx.send(embed=embed, components=[disnake.ui.ActionRow(*buttons)])

        while True:
            try:
                inter = await self.bot.wait_for(
                    "button_click",
                    check=lambda i: i.message.id == msg.id and i.user == ctx.author,
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

            embed = await refresh_embed(ctx, warnings, index, total_pages)
            buttons = await refresh_buttons(index, total_pages)
            await inter.response.edit_message(
                embed=embed, components=[disnake.ui.ActionRow(*buttons)]
            )

    @commands.command(aliases=["unwarn"])
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def remove_warn(
        self, ctx, user: Union[int, disnake.Member] = None, amount: int = 1
    ):
        user = (
            await ctx.guild.fetch_member(user)
            if isinstance(user, int)
            else await MemberConverter().convert(ctx, user)
            if isinstance(user, str)
            else user
        )

        check_result, error_embed = await common_checks(ctx, user, check_bot=True)
        if not check_result:
            return await ctx.send(embed=error_embed)

        count_deleted = await self.warns.delete_warnings(ctx.guild.id, user.id, amount)
        if isinstance(count_deleted, int):
            embed = Embed(
                title=f"Removed {count_deleted} warns",
                description=f"Administrator: {ctx.author.mention} ({ctx.author})\n"
                f"Member: {ctx.guild.get_member(user.id).mention} ({ctx.guild.get_member(user.id)})",
                color=0x2F3136,
            )
            embed.set_thumbnail(
                url=str(ctx.guild.get_member(user.id).display_avatar.url)
            )
            embed.set_footer(
                text=f"Synth © 2023 | All Rights Reserved",
                icon_url=self.bot.user.avatar,
            )
            await ctx.send(embed=embed)
        else:
            error_embed.description = (
                f"{emoji('error')} | Sorry, I couldn't remove any warns"
            )
            error_embed.set_footer(
                text=f"Synth © 2023 | All Rights Reserved",
                icon_url=self.bot.user.avatar,
            )
            return await ctx.send(embed=error_embed)

    @commands.command(aliases=["crossban"])
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def cross_ban(
        self, ctx, member: Union[int, str, disnake.Member], reason: str = None
    ):
        embed = Embed(color=0x2F3236)
        success_servers = []

        member = (
            await ctx.guild.fetch_member(member)
            if isinstance(member, int)
            else await MemberConverter().convert(ctx, member)
            if isinstance(member, str)
            else member
        )

        check_result, error_embed = await common_checks(ctx, member)
        if not check_result:
            return await ctx.send(embed=error_embed)

        if not member:
            member = ctx.author

        for guild in self.bot.guilds:
            author_permissions = (
                await guild.fetch_member(ctx.author.id)
            ).guild_permissions
            if not author_permissions.administrator:
                continue

            if member := await guild.fetch_member(member.id):
                try:
                    await guild.ban(member)

                    if not guild == ctx.guild:
                        embed.title = "<:ban:1170712517308317756> Crossban"
                        embed.description = (
                            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
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
                    await ctx.send(embed=embed)
                    continue

        embed.title = "<:ban:1170712517308317756> Crossban Success"
        embed.description = (
            f"**Banned from {len(success_servers)} servers.**\n"
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
            f"**Member:** {member} (`{member.id}`)\n"
            f"**Reason:** {reason}"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["crosskick"])
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def cross_kick(
        self, ctx, member: Union[int, disnake.Member], reason: str = None
    ):
        ErrorEmbed = Embed(color=disnake.Color.red())
        embed = Embed(color=0x2F3236)
        success_servers = []

        if not member:
            member = ctx.author

        member = (
            await ctx.guild.fetch_member(member)
            if isinstance(member, int)
            else await MemberConverter().convert(ctx, member)
            if isinstance(member, str)
            else member
        )

        common_check_result, error_embed = await common_checks(
            ctx, member, check_bot=False
        )
        if not common_check_result:
            return await ctx.send(embed=error_embed)

        for guild in self.bot.guilds:
            author_permissions = (
                await guild.fetch_member(ctx.author.id)
            ).guild_permissions
            if not author_permissions.administrator:
                continue

            if member := await guild.fetch_member(member.id):
                try:
                    await guild.kick(member)

                    if not guild == ctx.guild:
                        embed.title = "<:kick:1170712514288435271> Crosskick"
                        embed.description = (
                            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
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
                    ErrorEmbed.title = "<:kick:1170712514288435271> Crosskick Fail"
                    ErrorEmbed.description = (
                        f"Failed to kick {member.mention} on **{guild.name}** guild."
                    )
                    ErrorEmbed.set_footer(
                        text=f"Synth © 2023 | All Rights Reserved",
                        icon_url=self.bot.user.avatar,
                    )
                    await ctx.send(embed=embed)
                    continue

        embed.title = "<:kick:1170712514288435271> Crosskick Success"
        embed.description = (
            f"**Kicked from {len(success_servers)} servers.**\n"
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
            f"**Member:** {member} (`{member.id}`)\n"
            f"**Reason:** {reason}"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["crossmute"])
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def cross_mute(
        self,
        ctx,
        member: Union[int, disnake.Member],
        mute_time: str,
        *,
        reason: str = None,
    ):
        embed = Embed(color=0x2F3236)
        success_servers = []

        if not member:
            member = ctx.author

        member = (
            await ctx.guild.fetch_member(member)
            if isinstance(member, int)
            else await MemberConverter().convert(ctx, member)
            if isinstance(member, str)
            else member
        )

        common_check_result, error_embed = await common_checks(
            ctx, member, check_bot=False, for_mute=True
        )
        if not common_check_result:
            return await ctx.send(embed=error_embed)

        try:
            str_time = await str_to_seconds(mute_time)
        except ValueError:
            error_embed.description = f"{emoji('error')} | Invalid mute time format."
            error_embed.set_footer(
                text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
            )
            return await ctx.send(embed=error_embed)

        for guild in self.bot.guilds:
            author_permissions = (
                await guild.fetch_member(ctx.author.id)
            ).guild_permissions
            if not author_permissions.administrator:
                continue

            if member := await guild.fetch_member(member.id):
                try:
                    timeout = disnake.utils.utcnow() + datetime.timedelta(
                        seconds=str_time
                    )
                    await member.edit(timeout=timeout)
                    if not guild == ctx.guild:
                        embed.title = "<:mute:1170712518725992529> Crossmute"
                        embed.description = (
                            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
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
                    await ctx.send(embed=embed)
                    continue

        embed.title = "<:mute:1170712518725992529> Crossmute Success"
        embed.description = (
            f"**Muted on {len(success_servers)} servers.**\n"
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
            f"**Member:** {member} (`{member.id}`)\n"
            f"**Time:** {str(await hms(float(str_time)))}\n"
            f"**Unmute date:** <t:{int(time.time()) + str_time}>"
            f"**Reason:** {reason}"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def crosswarn(
        self, ctx, member: Union[int, disnake.Member], *, reason: str = None
    ):
        embed = Embed(color=0x2F3236)
        success_servers = []

        if not member:
            member = ctx.author

        member = (
            await ctx.guild.fetch_member(member)
            if isinstance(member, int)
            else await MemberConverter().convert(ctx, member)
            if isinstance(member, str)
            else member
        )

        common_check_result, error_embed = await common_checks(
            ctx, member, check_bot=False
        )
        if not common_check_result:
            return await ctx.send(embed=error_embed)

        for guild in self.bot.guilds:
            author_permissions = (
                await guild.fetch_member(ctx.author.id)
            ).guild_permissions
            if not author_permissions.administrator:
                continue

            if member := await guild.fetch_member(member.id):
                try:
                    case = await self.warns.add_warn(
                        ctx.guild.id, ctx.author, member, reason
                    )
                    if not guild == ctx.guild:
                        embed.title = "<:hammer:1169685339720384512> Crosswarn"
                        embed.description = (
                            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
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
                    await ctx.send(embed=embed)
                    continue

        embed.title = "<:hammer:1169685339720384512> Crosswarn Success"
        embed.description = (
            f"**Warned on {len(success_servers)} servers.**\n"
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
            f"**Member:** {member} (`{member.id}`)\n"
            f"**Reason:** {reason}"
        )
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
