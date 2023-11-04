import disnake
from disnake.ext import commands
from disnake.ext.commands import UserConverter, MemberConverter
from typing import Union

from src.utils.misc import emoji


class Moderation(commands.Cog):
    """Helper commands for server moderation"""

    EMOJI = "<:hammer:1169685339720384512>"

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def ban(self, ctx, user: Union[int, str, disnake.Member], *, reason=None):
        if isinstance(user, disnake.Member):
            member = user.id
        else:
            member = await UserConverter().convert(ctx, str(user))

        if member == ctx.author:
            return await ctx.send(mbed=disnake.Embed(
                description=f"{emoji('error')} | You can't ban yourself!",
                color=disnake.Color.red()
            ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))
        else:
            await ctx.send(embed=disnake.Embed(
                title="<:hammer:1169685339720384512> Successfully banned",
                description=f"Administrator: {ctx.author.mention} ({ctx.author})\n"
                            f"Member: {member.mention} ({member})\n"
                            f"Reason: {reason}",
                color=0x2F3236
            ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))
            try:
                await member.send(embed=disnake.Embed(
                    title="<:hammer:1169685339720384512> You were banned",
                    description=f"Administrator: {ctx.author.mention} ({ctx.author})\n"
                                f"Reason: {reason}"
                                f"Server: {ctx.guild.name}",
                    color=0x2F3236).set_footer(text=f"Synth © 2023 | All Rights Reserved",
                                               icon_url=self.bot.user.avatar))
            except (Exception, BaseException, disnake.Forbidden):
                pass
            await ctx.guild.ban(member, reason=f"Administrator: {ctx.author}, Reason: {reason}")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def unban(self, ctx, id: int):
        if isinstance(id, disnake.Member):
            member = id
        else:
            member = await UserConverter().convert(ctx, str(id))
        await ctx.guild.unban(member)
        await ctx.send(embed=disnake.Embed(
            title="<:hammer:1169685339720384512> Successfully unbanned",
            description=f"Administrator: {ctx.author.mention} ({ctx.author})\n"
                        f"Member: {member.mention} (`{id}`)",
            color=0x2F3236
        ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def kick(self, ctx, user: Union[int, str, disnake.Member], *, reason=None):
        if isinstance(user, disnake.Member):
            member = user.id
        else:
            member = await MemberConverter().convert(ctx, str(user))

        if member.top_role >= ctx.author.top_role:
            return await ctx.send(embed=disnake.Embed(
                description=f"{emoji('error')} | Your role is not higher than {member.mention}'s role!",
                color=disnake.Color.red()
            ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))

        elif member.top_role >= ctx.guild.get_member(self.bot.user.id).top_role:
            return await ctx.send(embed=disnake.Embed(
                description=f"{emoji('error')} | {member.mention}'s role is higher than mine, I can't kick him.",
                color=disnake.Color.red()
            ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))
        elif member == ctx.author:
            return await ctx.send(mbed=disnake.Embed(
                description=f"{emoji('error')} | You can't kick yourself!",
                color=disnake.Color.red()
            ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))
        elif member.id == self.bot.user.id:
            return await ctx.send(embed=disnake.Embed(
                description=f"{emoji('error')} | You can't kick me!",
                color=disnake.Color.red()
            ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))
        else:
            await member.kick(reason=reason)
            await ctx.send(embed=disnake.Embed(
                title="<:hammer:1169685339720384512> Successfully kicked",
                description=f"Administrator: {ctx.author.mention} ({ctx.author})\n"
                            f"Member: {member.mention} ({member})\n"
                            f"Reason: {reason}",
                color=0x2F3236
            ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))
            try:
                await member.send(embed=disnake.Embed(
                    title="<:hammer:1169685339720384512> You were kicked",
                    description=f"Administrator: {ctx.author.mention} ({ctx.author})\n"
                                f"Reason: {reason}\n"
                                f"Server: {ctx.guild.name}",
                    color=0x2F3236
                ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))
            except (Exception, BaseException, disnake.Forbidden):
                pass


def setup(bot):
    bot.add_cog(Moderation(bot))
