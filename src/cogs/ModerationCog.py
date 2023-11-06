import asyncio
import datetime
import time
from typing import Union, List, Any

import disnake
from disnake import Embed
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

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def ban(self, ctx: commands.Context, user: Union[int, str, disnake.Member], *, reason: str = None) -> None:
        embed = Embed(color=0x2F3236)

        member = user if isinstance(user, disnake.Member) else await UserConverter().convert(ctx, str(user))

        check_result, error_embed = await common_checks(ctx, member)
        if not check_result:
            return await ctx.send(embed=error_embed)

        embed.title = "<:ban:1170712517308317756> Successfully banned"
        embed.description = (
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
            f"**Member:** {member.mention} ({member})\n"
            f"**Reason:** {reason}"
        )
        embed.set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)
        await ctx.send(embed=embed)

        try:
            embed.title = "<:ban:1170712517308317756> You were banned"
            embed.description = (
                f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
                f"**Reason:** {reason}\n"
                f"**Server:** {ctx.guild.name}"
            )
            await member.send(embed=embed)
        except (disnake.HTTPException, disnake.Forbidden):
            pass

        try:
            await ctx.guild.ban(member, reason=f"{ctx.author}: {reason}")
        except (disnake.HTTPException, disnake.Forbidden):
            await ctx.send(content=f"Could not ban user {member.mention}")
        return
        
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def unban(self, ctx: commands.Context, id: Union[str, int, disnake.Member, disnake.User]) -> None:
        member = id if isinstance(id, disnake.Member) else await UserConverter().convert(ctx, str(id))

        check_result, error_embed = await common_checks(ctx, member, for_unban=True)
        if not check_result:
            return await ctx.send(embed=error_embed)

        embed = Embed(color=0x2F3236)
        embed.title = "<:invite:1169690514430382160> Successfully unbanned"
        embed.description = (
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
            f"**Member:** {member.mention} (`{id}`)"
        )
        embed.set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)

        try:
            await ctx.guild.unban(member)
        except (disnake.HTTPException, disnake.Forbidden):
            await ctx.send(content=f"Could not unban user {member.mention}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def kick(self, ctx: commands.Context, user: Union[int, str, disnake.Member], *, reason: str = None):
        embed = Embed(color=0x2F3236)

        member = user if isinstance(user, disnake.Member) else await MemberConverter().convert(ctx, str(user))

        check_result, error_embed = await common_checks(ctx, member)
        if not check_result:
            return await ctx.send(embed=error_embed)

        embed.title = "<:kick:1170712514288435271> Successfully kicked"
        embed.description = (
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
            f"**Member:** {member.mention} ({member})\n"
            f"**Reason:** {reason}"
        )
        embed.set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)
        await ctx.send(embed=embed)

        try:
            embed.title = "<:kick:1170712514288435271> You were kicked"
            embed.description = (
                f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
                f"**Reason:** {reason}\n"
                f"**Server:** {ctx.guild.name}"
            )
            embed.set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)
            await member.send(embed=embed)

        except (Exception, BaseException, disnake.Forbidden):
            pass
        
        try:
            await member.kick(reason=reason)
        except (disnake.HTTPException, disnake.Forbidden):
            await ctx.send(content=f"Could not kick user {member.mention}")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def mute(self, ctx, member: Union[int, str, disnake.Member], mute_time: str, *, reason=None):
        embed = Embed(color=0x2F3236)
        ErrorEmbed = Embed(color=disnake.Color.red())

        if isinstance(member, int):  # Check if member is an integer (ID)
            member = await ctx.guild.fetch_member(member)  # Convert the integer to a disnake.Member

        if isinstance(member, str):  # Check if member is a string
            member = await MemberConverter().convert(ctx, member)

        try:
            str_time = await str_to_seconds(mute_time)
        except ValueError:
            ErrorEmbed.description = f"{emoji('error')} | Invalid mute time format."
            ErrorEmbed.set_footer(text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)
            return await ctx.send(embed=ErrorEmbed)

        check_result, error_embed = await common_checks(ctx, member, for_mute=True, str_time=str_time)
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
        embed.set_footer(text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)

        await member.edit(timeout=disnake.utils.utcnow() + datetime.timedelta(seconds=str_time))
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
            embed.set_footer(text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)
            await member.send(embed=embed)
        except (Exception, BaseException, disnake.Forbidden):
            pass

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def unmute(self, ctx, member: Union[int, str, disnake.Member]):
        embed = Embed(color=0x2F3236)
        ErrorEmbed = Embed(color=disnake.Color.red())

        if isinstance(member, str):  # Check if member is a string
            member = await MemberConverter().convert(ctx, member)

        if isinstance(member, int):  # Check if member is an integer (ID)
            member = await ctx.guild.fetch_member(member)  # Convert the integer to a disnake.Member

        check_result, error_embed = await common_checks(ctx, member)
        if not check_result:
            return await ctx.send(embed=error_embed)

        if member == ctx.author:
            ErrorEmbed.description = f"{emoji('error')} | You can't unmute yourself!"
            ErrorEmbed.set_footer(text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)
            return await ctx.send(embed=ErrorEmbed)

        embed.title = "<:unmute:1169690521472614500> Successfully unmuted"
        embed.description = (
            f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
            f"**Member:** {member.mention} ({member})"
        )
        embed.set_footer(text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)

        await member.edit(timeout=None)
        await ctx.send(embed=embed)

        try:
            embed.title = "<:unmute:1169690521472614500> You were unmuted"
            embed.description = (
                f"**Administrator:** {ctx.author.mention} ({ctx.author})\n"
                f"**Server:** {ctx.guild.name}\n"
            )
            embed.set_footer(text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)
            await member.send(embed=embed)
        except (Exception, BaseException, disnake.Forbidden):
            pass

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def mutes(self, ctx):
        pages = []
        per_page = 5
        total = 0
        index = 0

        for member in [m for m in ctx.guild.members if not m.bot and m.current_timeout is not None]:
            total += 1
            unmuted_at = member.current_timeout
            pages.append(
                f"`[{total}]` **{member.mention}** - <t:{round(unmuted_at.timestamp())}:F> (<t:{round(unmuted_at.timestamp())}:R>)")

        if not pages:
            embed = disnake.Embed(color=0x2F3136, description="There are currently no mutes on this server.")
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)
            return await ctx.send(embed=embed)

        total_pages = (total + per_page - 1) // per_page

        async def refresh_buttons():
            buttons = [ActionRow(
                disnake.ui.Button(custom_id="back", emoji="◀️", style=disnake.ButtonStyle.blurple, disabled=index == 0),
                disnake.ui.Button(custom_id="forward", emoji="▶️", style=disnake.ButtonStyle.blurple,
                                  disabled=index == total_pages - 1),
                disnake.ui.Button(custom_id="close", emoji="<:delete:1169690519677440093>", style=disnake.ButtonStyle.danger)
            )] if total_pages > 1 else [
                ActionRow(disnake.ui.Button(custom_id="close", emoji="<:delete:1169690519677440093>", style=disnake.ButtonStyle.danger))]
            return buttons

        async def refresh_embed():
            embed: Embed = disnake.Embed(title="<:calendar:1169690539168366712> Active mutes", color=0x2F3136)
            if total_pages > 1:
                embed.set_footer(text=f"{ctx.author} | Page {index + 1} of {total_pages}", icon_url=ctx.author.avatar)
            else:
                embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar)
            for page in pages[index * per_page:(index + 1) * per_page]:
                embed.add_field(name="", value=page, inline=False)
            return embed

        embed = await refresh_embed()
        msg = await ctx.send(embed=embed, components=await refresh_buttons())

        def check(interaction: disnake.MessageInteraction) -> bool:
            return interaction.message.id == msg.id and interaction.author == ctx.author

        while True:
            try:
                inter = await self.bot.wait_for('button_click', check=check, timeout=600)
            except asyncio.TimeoutError:
                break

            if inter.component.custom_id == "back":
                index = max(index - 1, 0)
            elif inter.component.custom_id == "forward":
                index = min(index + 1, total_pages - 1)
            elif inter.component.custom_id == "close":
                break

            await msg.edit(embed=await refresh_embed(), components=await refresh_buttons())
            await inter.response.defer(ephemeral=True)

        await msg.delete()

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def bans(self, ctx):
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
            embed = disnake.Embed(color=0x2F3136, description="There are currently no bans on this server.")
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)
            return await ctx.send(embed=embed)

        total_pages = (total + per_page - 1) // per_page

        async def refresh_buttons():
            buttons = [ActionRow(
                disnake.ui.Button(custom_id="back", emoji="◀️", style=disnake.ButtonStyle.blurple, disabled=index == 0),
                disnake.ui.Button(custom_id="forward", emoji="▶️", style=disnake.ButtonStyle.blurple,
                                  disabled=index == total_pages - 1),
                disnake.ui.Button(custom_id="close", emoji="<:delete:1169690519677440093>", style=disnake.ButtonStyle.danger)
            )] if total_pages > 1 else [
                ActionRow(disnake.ui.Button(custom_id="close", emoji="<:delete:1169690519677440093>", style=disnake.ButtonStyle.danger))]
            return buttons

        async def refresh_embed():
            embed: Embed = disnake.Embed(title="<:calendar:1169690539168366712> Active bans", color=0x2F3136)
            if total_pages > 1:
                embed.set_footer(text=f"{ctx.author} | Page {index + 1} of {total_pages}", icon_url=ctx.author.avatar)
            else:
                embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar)
            for page in pages[index * per_page:(index + 1) * per_page]:
                embed.add_field(name="", value=page, inline=False)
            return embed

        embed = await refresh_embed()
        msg = await ctx.send(embed=embed, components=await refresh_buttons())

        def check(interaction: disnake.MessageInteraction) -> bool:
            return interaction.message.id == msg.id and interaction.author == ctx.author

        while True:
            try:
                inter = await self.bot.wait_for('button_click', check=check, timeout=600)
            except asyncio.TimeoutError:
                break

            if inter.component.custom_id == "back":
                index = max(index - 1, 0)
            elif inter.component.custom_id == "forward":
                index = min(index + 1, total_pages - 1)
            elif inter.component.custom_id == "close":
                break

            await msg.edit(embed=await refresh_embed(), components=await refresh_buttons())
            await inter.response.defer(ephemeral=True)

        await msg.delete()

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, user: Union[int, str, disnake.Member], *, reason=None):
        if isinstance(user, int):
            member = await ctx.guild.fetch_member(user)
        elif isinstance(user, str):
            member = await MemberConverter().convert(ctx, user)
        else:
            member = user

        common_check_result, error_embed = await common_checks(ctx, member)
        if not common_check_result:
            return await ctx.send(embed=error_embed)

        case = await warns.add_warn(ctx.guild.id, ctx.author, member, reason)

        embed = Embed(title=f"<:icons_warning:1170751866905296978> Warned {member} (Case #{case})", color=0x2F3136)
        embed.add_field(name="**Administrator:**", value=f"{ctx.author.mention} ({ctx.author})", inline=False)
        embed.add_field(name="**Member:**", value=f"{member.mention} ({member})", inline=False)
        embed.add_field(name="**Reason:**", value=reason, inline=False)

        embed.set_thumbnail(url=str(member.display_avatar.url))
        embed.set_footer(text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def warns(self, ctx, member: Union[int, disnake.Member] = None):
        common_check_result, error_embed = await common_checks(ctx, member, check_bot=False)
        if not common_check_result:
            return await ctx.send(embed=error_embed)

        if not member:
            member = ctx.author
        if isinstance(member, int):
            member = await ctx.guild.fetch_member(member)  # Convert the integer to a disnake.Member

        warnings = await warns.get_user_warnings(ctx.guild.id, member)

        index = 0
        total_pages = (len(warnings) + 4) // 5  # Calculate the total number of pages

        async def refresh_buttons(index, total_pages):
            prev_button = disnake.ui.Button(
                label="️◀️", style=disnake.ButtonStyle.blurple, custom_id=f"warns_prev:{index}",
                disabled=index == 0
            )
            next_button = disnake.ui.Button(
                label="▶️", style=disnake.ButtonStyle.blurple, custom_id=f"warns_next:{index}",
                disabled=index == total_pages - 1
            )
            delete_button = disnake.ui.Button(
                style=disnake.ButtonStyle.red,
                custom_id="delete_warns",
                emoji="<:delete:1169690519677440093>"
            )
            return [prev_button, next_button, delete_button]

        async def refresh_embed(ctx, warnings, index, total_pages):
            embed = Embed(color=0x2F3136)
            embed.title = f"Warns of {member}"
            embed.description = f"**Total warns count:** {len(warnings)}"
            embed.set_thumbnail(url=member.avatar)

            per_page = 5
            start = index * per_page
            end = (index + 1) * per_page

            for i, warning in enumerate(warnings[start:end], start=start + 1):
                timestamp = warning["timestamp"]
                administrator = ctx.guild.get_member(int(warning["moderator_id"]))
                reason = warning["reason"]
                embed.add_field(
                    name=f"Warn #{i}",
                    value=f"Administrator: {administrator.mention}\n"
                          f"Timestamp: {timestamp}\n"
                          f"Reason: {reason}",
                    inline=False
                )
            return embed

        embed = await refresh_embed(ctx, warnings, index, total_pages)
        buttons = await refresh_buttons(index, total_pages)
        msg = await ctx.send(embed=embed, components=[disnake.ui.ActionRow(*buttons)])

        def check(inter: disnake.MessageInteraction):
            return inter.message.id == msg.id and inter.user == ctx.author

        while True:
            try:
                inter = await self.bot.wait_for('button_click', check=check, timeout=600)
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
            await inter.response.edit_message(embed=embed, components=[disnake.ui.ActionRow(*buttons)])

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def unwarn(self, ctx, member: Union[int, disnake.Member] = None, amount: int = 1):
        ErrorEmbed = Embed(color=disnake.Color.red())

        common_check_result, error_embed = await common_checks(ctx, member, check_bot=False)
        if not common_check_result:
            return await ctx.send(embed=error_embed)

        member_id = member.id if isinstance(member, disnake.Member) else member

        count_deleted = await warns.delete_warnings(ctx.guild.id, member_id, amount)
        if isinstance(count_deleted, int):
            embed = Embed(
                title=f"Removed {count_deleted} warns",
                description=f"Administrator: {ctx.author.mention} ({ctx.author})\n"
                            f"Member: {ctx.guild.get_member(member_id).mention} ({ctx.guild.get_member(member_id)})",
                color=0x2F3136
            )
            embed.set_thumbnail(url=str(ctx.guild.get_member(member_id).display_avatar.url))
            embed.set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)
            await ctx.send(embed=embed)
        else:
            ErrorEmbed.description = f"{emoji('error')} | Sorry, I couldn't remove any warns"
            ErrorEmbed.set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)
            return await ctx.send(embed=ErrorEmbed)


def setup(bot):
    bot.add_cog(Moderation(bot))
