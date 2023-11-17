import datetime
from typing import Union, Any

import disnake
from disnake import Localized
from disnake.ext import commands
from disnake.utils import format_dt
from memory_profiler import memory_usage

from src.utils.misc import check_if_user_is_developer, emoji

startup = datetime.datetime.now()


class Utility(commands.Cog):
    """Utility commands"""

    EMOJI = "<:globe:1169690501063123065>"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.badges = {
            1: "<:staff:1168622635228344403>",
            2: "<:partner:1168622631705137233>",
            4: "<:hypesquad:1168622629901586605>",
            8: "<:bug_hunter:1168622622045634622>",
            64: "<:hypersquad_bravery:1168622644455805100>",
            128: "<:hypersquad_brilliance:1168622642690015373>",
            256: "<:hypersquad_balance:1168622640240533514>",
            512: "<:early_supporter:1168622625896009729>",
            1024: "<:team_user:1168622638592163991>",
            16384: "<:bug_hunter:1168622622045634622>",
            65536: "<:developer:1168622649967116378>",
            131072: "<:developer:1168622649967116378>",
            262144: "<:shield:1168250173089140956>",
            1048576: "⚠️",
            133172312: "<:synthdev:1169689479452311582>",
        }

    @commands.slash_command(
        name=Localized("user", key="USER_COMMAND_NAME"),
        description=Localized(
            "Display information about user.", key="USER_COMMAND_DESC"
        ),
    )
    async def user(
        self,
        interaction: disnake.MessageCommandInteraction,
        user: Union[disnake.User, disnake.Member] = commands.Param(
            description=Localized("Choice user", key="USER_COMMAND_USER_DESC"),
            name=Localized("user", key="USER_COMMAND_USER_NAME"),
            default=None,
        ),
    ) -> None:
        if user is None:
            user = interaction.user

        is_dev = (
            ""
            if not check_if_user_is_developer(bot=self.bot, user_id=user.id)
            else " <:synthdev:1169689479452311582>"
        )
        embed = disnake.Embed(
            title=f"@{user.name} / {user.id} {is_dev}",
            color=self.settings_db.get_embed_color(interaction.guild.id),
            description=f"[Link to DM](discord://discord.com/users/{user.id})",
        )
        embed.add_field(
            name="<:created_at:1169684592006017034> Created at",
            value=format_dt(user.created_at, style="f"),
            inline=False,
        )

        embed.set_thumbnail(url=user.display_avatar.url)
        if user.banner:
            embed.set_image(url=user.banner.url)

        if isinstance(user, disnake.Member):
            embed.add_field(
                name="<:info:1169685342077583480> Joined at",
                value=format_dt(user.joined_at, style="f"),
                inline=False,
            )
            embed.add_field(
                name="<:activities:1169690504393404456> Status",
                value=user.status,
                inline=False,
            )
            embed.add_field(
                name="<:globe:1169690501063123065> Is on mobile?",
                value=user.is_on_mobile(),
                inline=False,
            )
            embed.add_field(
                name="<:store:1169690541986959464> Roles:",
                value=" ".join(
                    [
                        role.mention
                        for role in user.roles
                        if not role.is_default() and role.name != "@everyone"
                    ]
                ),
                inline=False,
            )
            embed.add_field(
                name="<:design:1169688944502378536> Top role",
                value=user.top_role.mention,
                inline=False,
            )

        flags = " ".join(
            [
                user_badges
                for badge, user_badges in self.badges.items()
                if user.public_flags._has_flag(badge)
            ]
        )

        if flags != "":
            embed.add_field(
                name="<:list:1169690529643114547> Flags", value=flags, inline=False
            )

        await interaction.send(embed=embed)

    @commands.slash_command(
        name=Localized("server", key="SERVER_COMMAND_NAME"),
        description=Localized(
            "Display information about server.", key="SERVER_COMMAND_DESC"
        ),
    )
    async def server(self, interaction: disnake.MessageCommandInteraction) -> None:
        emoji_count = len(interaction.guild.emojis)
        list_of_bots = len([m for m in interaction.guild.members if m.bot])
        list_of_users = len([m for m in interaction.guild.members if not m.bot])
        guild_created_at = format_dt(interaction.guild.created_at, style="f")
        text_channels = len(interaction.guild.text_channels)
        voice_channels = len(interaction.guild.voice_channels)
        categories = len(interaction.guild.categories)
        threads = len(interaction.guild.threads)
        owner = interaction.guild.owner

        embed = disnake.Embed(
            title=f"{interaction.guild.name}'s information",
            color=self.settings_db.get_embed_color(interaction.guild.id),
        )
        embed.add_field(
            name="Main Information",
            value=(
                f"<:owner:1169684595697004616> **Owner:** {owner.mention} ({owner.id})\n"
                f"<:created_at:1169684592006017034> **Created at:** {guild_created_at}\n"
                f"<:boost:1169685353515462697> **Boosts:** {interaction.guild.premium_subscription_count}\n"
                f"<:star:1169685347576336385> **Emojis:** {emoji_count}\n"
                f"<:link:1169685349409226893> **Icon:** [click]({interaction.guild.icon})\n"
                f"<:channels:1169684589640429599> **Channels:** {len(interaction.guild.channels)}\n"
                f"<:design:1169686174374301746> <:channels:1169684589640429599> **Text Channels:** {text_channels}\n"
                f"<:design:1169686174374301746> <:voice:1169684588315029534> **Voice Channels:** {voice_channels}\n"
                f"<:design:1169686174374301746> <:category:1169684586666663999> **Categories:** {categories}\n"
                f"<:design:1169688944502378536> <:thread:1169685355423866963> **Threads:** {threads}\n\n"
            ),
            inline=False,
        )
        embed.add_field(
            name="Members",
            value=f"<:members:1169684583369949285> **All members:** {len(interaction.guild.members)}\n"
            f"<:design:1169686174374301746> <:members:1169684583369949285> **Human:** {list_of_users}\n"
            f"<:design:1169688944502378536> <:bot:1169685346506776697> **Bots:** {list_of_bots}",
            inline=False,
        )
        embed.set_thumbnail(url=interaction.guild.icon)
        embed.set_image(url=interaction.guild.banner)
        await interaction.send(embed=embed)

    @commands.slash_command(name="clear", description="Clear messages from chat")
    async def clear(
        self,
        interaction: disnake.MessageCommandInteraction,
        amount: int,
        channel: disnake.TextChannel = commands.Param(
            name="channel",
            description="The channel to clear messages from",
            default=None,
        ),
    ) -> None:
        if channel is None:
            channel = interaction.channel

        if amount > 100:
            await interaction.send(
                embed=disnake.Embed(
                    title="Sorry, the maximum amount of messages to delete is 100",
                    color=disnake.Color.red(),
                ).set_footer(
                    text=f"Synth © 2023 | All Rights Reserved",
                    icon_url=self.bot.user.avatar,
                ),
                delete_after=10,
            )
            return
        try:
            deleted = await channel.purge(limit=amount)
        except disnake.Forbidden:
            await interaction.send(
                embed=disnake.Embed(
                    title="Sorry, the bot doesn't have enough permissions to delete messages",
                    color=disnake.Color.red(),
                ).set_footer(
                    text=f"Synth © 2023 | All Rights Reserved",
                    icon_url=self.bot.user.avatar,
                ),
                delete_after=10,
            )
            return
        except disnake.HTTPException:
            await interaction.send(
                embed=disnake.Embed(
                    title="Sorry, the bot doesn't have enough permissions to delete messages",
                    color=disnake.Color.red(),
                ).set_footer(
                    text=f"Synth © 2023 | All Rights Reserved",
                    icon_url=self.bot.user.avatar,
                ),
                delete_after=10,
            )
            return

        embed = disnake.Embed(
            color=self.settings_db.get_embed_color(interaction.guild.id)
        )
        embed.title = "<a:loading:1168599537682755584> Cleaning messages..."
        embed.description = f"Deleted **{len(deleted)}** messages"
        embed.set_footer(
            text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await interaction.channel.send(embed=embed, delete_after=10)

    @commands.slash_command(
        name="botinfo", description="Display information about the bot."
    )
    async def _bot_info(self, interaction: disnake.MessageCommandInteraction):
        channels = set(self.bot.get_all_channels())
        big_builds = len([g for g in self.bot.guilds if g.member_count >= 1000])

        embed = disnake.Embed(
            title="Information about Synth",
            description="**Synth** - is a multi-functional Discord bot.",
            color=self.settings_db.get_embed_color(interaction.guild.id),
        ).set_thumbnail(url=self.bot.user.avatar)
        embed.add_field(
            name="Main",
            value=f"<:clock:1169690592465395722> Ping: **{round(self.bot.latency * 1000)} ms\n**"
            f"<:activities:1169690504393404456> RAM: **{round(memory_usage()[0], 2)} mb**\n"
            f"<:icons_goodping:1169690518645649478> Uptime: {format_dt(startup, style='F')}\n",
            inline=False,
        )
        embed.add_field(
            name="Popularity",
            value=f"<:info:1169685342077583480> Servers: **{len(self.bot.guilds)}**\n"
            f"<:globe:1169690501063123065> Big servers (1000+): **{big_builds}**\n"
            f"<:members:1169684583369949285> Users: **{len(set(self.bot.get_all_members()))}**\n"
            f"<:channels:1169684589640429599> Channels: **{len(channels)}**\n",
            inline=False,
        )
        embed.add_field(
            name="Other Information",
            value=f"<:calendar:1169690539168366712> Created at: **31/10/2023**\n"
            f"<:created_at:1169684592006017034> Bot version: **v1.0.0.**\n"
            f"<:wrench:1169690509929889802> Python version: **3.11.6**\n"
            f"<:owner:1169684595697004616> Owners: [Snaky](https://discord.com/users/999682446675161148), "
            f"[Weever](https://discord.com/users/419159175009009675), "
            f"[LazyDev](https://discord.com/users/1167458549132181668)",
            inline=False,
        )
        embed.set_footer(
            text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )

        support = disnake.ui.Button(
            label="Support server", url="https://discord.gg/7vT3H3tVYp"
        )
        website = disnake.ui.Button(
            label="Documentation", url="https://synth.gitbook.io/"
        )

        await interaction.send(embed=embed, components=[support, website])

    @commands.slash_command(name="avatar", description="View user avatar")
    async def avatar(
        self,
        interaction: disnake.MessageCommandInteraction,
        user: disnake.User = commands.Param(
            name="user",
            description="The user you want to view the avatar",
            default=None,
        ),
    ) -> None:
        user = user or interaction.author
        embed = disnake.Embed(
            color=self.settings_db.get_embed_color(interaction.guild.id)
        )
        embed.set_author(name=user, icon_url=str(user.display_avatar))
        if user.avatar is not None:
            embed.description = (
                f"{emoji('users')} [JPG]({user.display_avatar.with_format('jpeg')}) | "
                f"[PNG]({user.display_avatar.with_format('png')}) |  "
                f"[WEBP]({user.display_avatar})"
            )
            if user.display_avatar.is_animated():
                embed.description += (
                    f" | [GIF]({user.display_avatar.with_format('gif')})"
                )
        else:
            embed.description = f"<:q_members:1031115958191931452> [PNG]({user.display_avatar.with_format('png')})"
        embed.set_image(url=str(user.display_avatar))
        await interaction.send(embed=embed)

    async def send_processing_message(
        self, interaction: disnake.MessageCommandInteraction, action: str, role
    ) -> None:
        message = await interaction.send(
            embed=disnake.Embed(
                title=f"<a:loading:1168599537682755584> Please wait...",
                description=f"{action} {role.mention} to all members in this server.\n"
                f"Please do not delete this message until the process is completed.",
                color=self.settings_db.get_embed_color(interaction.guild.id),
            ).set_footer(
                text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
            )
        )
        return message

    async def process_role_action(
        self,
        interaction: disnake.MessageCommandInteraction,
        role: disnake.Role,
        action_func: Any,
        action_str: str,
    ):
        total_members = len(interaction.guild.members)
        failed_members = []

        if not role.permissions.administrator:
            processing_message = await self.send_processing_message(
                interaction, action_str, role
            )

            for member in interaction.guild.members:
                try:
                    await action_func(member, role)
                except disnake.Forbidden:
                    failed_members.append(member)

            if failed_members:
                failed_count = len(failed_members)
                await processing_message.edit(
                    embed=disnake.Embed(
                        description=f"Successfully {action_str} role for "
                        f"**{total_members - failed_count}/{total_members}** members. "
                        f"Failed to {action_str} role for **{failed_count}** members.",
                        color=self.settings_db.get_embed_color(interaction.guild.id),
                    ).set_footer(
                        text="Synth © 2023 | All Rights Reserved",
                        icon_url=self.bot.user.avatar,
                    )
                )
            else:
                await processing_message.edit(
                    embed=disnake.Embed(
                        description=f"Successfully {action_str} role for all **{total_members}** members.",
                        color=self.settings_db.get_embed_color(interaction.guild.id),
                    ).set_footer(
                        text="Synth © 2023 | All Rights Reserved",
                        icon_url=self.bot.user.avatar,
                    )
                )
        else:
            await interaction.send(
                embed=disnake.Embed(
                    description=f"<a:error:1168599839899144253> | Sorry, this role has administrator permissions, "
                    f"so I can't {action_str} it to all members.",
                    color=0xFF0000,
                )
            )

    @commands.slash_command(
        name="add-roles", description="Add a specific role to all users"
    )
    async def add_roles(
        self,
        interaction: disnake.MessageCommandInteraction,
        role: disnake.Role = commands.Param(
            name="role", description="The role to add to all users"
        ),
    ) -> None:
        await self.process_role_action(
            interaction, role, disnake.Member.add_roles, "Adding"
        )

    @commands.slash_command(
        name="remove-roles", description="Remove a specific role from all users"
    )
    async def remove_roles(
        self,
        interaction: disnake.MessageCommandInteraction,
        role: disnake.Role = commands.Param(
            name="role", description="The role to remove from all users"
        ),
    ) -> None:
        await self.process_role_action(
            interaction, role, disnake.Member.remove_roles, "Removing"
        )

    @commands.slash_command(
        name="lock", description="Lock the current channel for everyone"
    )
    async def lock(
        self,
        interaction: disnake.MessageCommandInteraction,
        channel: disnake.TextChannel = commands.Param(
            name="channel",
            description="The channel to lock",
            default=None,
        ),
    ) -> None:
        channel = channel or interaction.channel

        await channel.set_permissions(
            interaction.guild.default_role, send_messages=False
        )
        await interaction.send(
            f"{emoji('success')} | Channel is locked", ephemeral=True
        )

    @commands.slash_command(
        name="unlock", description="Unlock the current channel for everyone"
    )
    async def lock(
        self,
        interaction: disnake.MessageCommandInteraction,
        channel: disnake.TextChannel = commands.Param(
            name="channel",
            description="The channel to unlock",
            default=None,
        ),
    ) -> None:
        channel = channel or interaction.channel

        await channel.set_permissions(
            interaction.guild.default_role, send_messages=True
        )
        await interaction.send(
            f"{emoji('success')} | Channel is unlocked", ephemeral=True
        )


def setup(bot: commands.Bot):
    bot.add_cog(Utility(bot=bot))
