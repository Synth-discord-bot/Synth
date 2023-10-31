from disnake.ext import commands
import disnake
from disnake.utils import format_dt
from typing import Union
from src.utils.misc import check_if_user_is_developer
from disnake import Localized
import datetime
from memory_profiler import memory_usage

startup = datetime.datetime.now()

class BasicUtility(commands.Cog):
    """Basic utility commands."""

    EMOJI = "✨"

    def __init__(self, bot):
        self.bot = bot
        self.badges = {
            # 0: "No Badge",
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
            1048576: "<:error:1168968103984636014>",
            133172312: "<:synth_dev:1168623393717899314>",
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
    ):
        if user is None:
            user = interaction.user

        embed = disnake.Embed(
            title=f"@{user.name} / {user.id} {'' if not check_if_user_is_developer(bot=self.bot, user_id=user.id) else ' <:synth_dev:1168623393717899314>'}",
            color=0x2B2D31,
            description=f"[Link to DM](discord://discord.com/users/{user.id})",
        )
        embed.add_field(
            name="Created at", value=format_dt(user.created_at, style="f"), inline=False
        )

        embed.set_thumbnail(url=user.display_avatar.url)
        if user.banner:
            embed.set_image(url=user.banner.url)

        if isinstance(user, disnake.Member):
            embed.add_field(
                name="Joined at",
                value=format_dt(user.joined_at, style="f"),
                inline=False,
            )
            embed.add_field(name="Status", value=user.status, inline=False)
            embed.add_field(
                name="Is on mobile?", value=user.is_on_mobile(), inline=False
            )
            embed.add_field(
                name="Roles:",
                value=" ".join(
                    [
                        role.mention
                        for role in user.roles
                        if not role.is_default() and role.name != "@everyone"
                    ]
                ),
                inline=False,
            )
            embed.add_field(name="Top role", value=user.top_role.mention, inline=False)

        flags = " ".join(
            [
                user_badges
                for badge, user_badges in self.badges.items()
                if user.public_flags._has_flag(badge)
            ]
        )

        if flags != "":
            embed.add_field(name="Flags", value=flags, inline=False)

        await interaction.send(embed=embed)

    @commands.slash_command(
        name=Localized("server", key="SERVER_COMMAND_NAME"),
        description=Localized(
            "Display information about server.", key="SERVER_COMMAND_DESC"
        ),
    )
    async def server(self, interaction: disnake.MessageCommandInteraction):
        emoji_count = len(interaction.guild.emojis)
        list_of_bots = len([m for m in interaction.guild.members if m.bot])
        list_of_users = len([m for m in interaction.guild.members if not m.bot])

        embed = disnake.Embed(
            title=f"{interaction.guild.name}'s information", color=0x2B2D31
        )
        embed.add_field(
            name="<:gear:1168228790183415868> Main Information",
            value=f"**Emojis:** `{emoji_count}`\n"
            f"**Members:** `{len(interaction.guild.members)}`\n"
            f"**Owner:** `{interaction.guild.owner}`\n"
            f"**Roles:** `{len(interaction.guild.roles)}`\n"
            f"**Created at:** {format_dt(interaction.guild.created_at, style='f')}\n"
            f"**Icon:** [click]({interaction.guild.icon})\n"
            f"**Boost:** `{interaction.guild.premium_subscription_count}`\n",
            inline=True,
        )

        embed.add_field(
            name="<:link:1168250171524649060> Server Channels",
            value=f"**Channels:** `{len(interaction.guild.channels)}`\n"
            f"**Text Channels:** `{len(interaction.guild.text_channels)}`\n"
            f"**Voice Channels:** `{len(interaction.guild.voice_channels)}`\n"
            f"**Categories:** `{len(interaction.guild.categories)}`\n"
            f"**Threads:** `{len(interaction.guild.threads)}`\n",
            inline=True,
        )

        embed.add_field(
            name="<:settings:1168250174611660971> Server Members",
            value=f"**All Members:** `{len(interaction.guild.members)}`\n"
            f"**Humans:** `{list_of_users}`\n"
            f"**Bots:** `{list_of_bots}`\n"
            f"**Administrators:** `{len([r for r in interaction.guild.roles if r.permissions.administrator])}`\n"
            f"**Moderators:** `{len([r for r in interaction.guild.roles if r.permissions.kick_members])}`\n"
            f"**Joined at:** {format_dt(interaction.user.joined_at, style='f')}",
            inline=False,
        )

        embed.set_thumbnail(url=interaction.guild.icon)
        embed.set_image(url=interaction.guild.banner)
        await interaction.send(embed=embed)

    @commands.slash_command(
            name="clear", 
            description="Clear messages from chat"
    )
    async def clear(
        self, interaction: disnake.MessageCommandInteraction, 
        amount: int, 
        channel: disnake.TextChannel = commands.Param(
            name="channel",
            description="The channel to clear messages from",
            default=None,
        )
    ):
        if channel is None:
            channel = interaction.channel

        if amount > 100:
            await interaction.send(embed=disnake.Embed(
                title="Sorry, the maximum amount of messages to delete is 100",
                color=disnake.Color.red()).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar),
                           delete_after=10)
            return
        try:
            deleted = await channel.purge(limit=amount)
        except disnake.Forbidden:
            await interaction.send(embed=disnake.Embed(
                title="Sorry, the bot doesn't have enough permissions to delete messages",
                color=disnake.Color.red()).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar),
                           delete_after=10)
            return
        except disnake.HTTPException:
            await interaction.send(embed=disnake.Embed(
                title="Sorry, the bot doesn't have enough permissions to delete messages",
                color=disnake.Color.red()).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar),
                           delete_after=10)
            return

        embed = disnake.Embed(color=0x2F3136)
        embed.title = "<a:loading:1168599537682755584> Cleaning messages..."
        embed.description = f"Deleted **{len(deleted)}** messages"
        embed.set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)
        await interaction.channel.send(embed=embed, delete_after=10)

    @commands.slash_command(
        name="botinfo",
        description="Display information about the bot."
    )
    async def botinfo(self, interaction: disnake.MessageCommandInteraction):
        ch = []
        for guild in self.bot.guilds:
            for channel in guild.channels:
                ch.append(channel.name)
        embed = disnake.Embed(
            title="Information about Synth",
            description="**Synth** - is a multi-functional Discord bot.",
            color=0x2F3136
        ).set_thumbnail(url = self.bot.user.avatar)
        embed.add_field(
            name="Main",
            value=f"<:ping:1168968111920255086> Ping: **{round(self.bot.latency * 1000)} ms\n**"
                  f"<:ram:1168969950275321927> RAM: **{round(memory_usage()[0], 2)} mb**\n"
                  f"<:uptime:1168968110154457088> Uptime: {format_dt(startup, style = 'F')}\n",
            inline=False
        )
        embed.add_field(
            name="Popularity",
            value=f"<:gear:1168228790183415868> Servers: **{len(self.bot.guilds)}**\n"
                  f"<:moderator:1168622624629334136> Big servers (1000+): **{len([g for g in self.bot.guilds if g.member_count >= 1000])}**\n"
                  f"<:users:1168968100637589607> Users: **{len(set(self.bot.get_all_members()))}**\n"
                  f"<:channel:1168968099194744912> Channels: **{len(ch)}**\n",
            inline=False
        )
        embed.add_field(
            name="Other Information",
            value=f"<:staff:1168622635228344403> Created at: **31/10/2023**\n"
                  f"<:information:1168237956591530065> Bot version: **v1.0.0.**\n"
                  f"<:python:1168970645980315658> Python version: **3.11.6**\n"
                  f"<:crown:1168970928970023042> Owners: [Snaky](https://discord.com/users/999682446675161148), "
                    f"[Weever](https://discord.com/users/419159175009009675), "
                    f"[LazyDev](https://discord.com/users/1167458549132181668)",
            inline=False
        )
        embed.set_footer(text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar)
        support = 'Support server'
        website = 'Website'

        support = disnake.ui.Button(label=support, url='https://discord.gg/7vT3H3tVYp')
        website = disnake.ui.Button(label=website, url='https://synth.xyz/')

        await interaction.send(embed=embed, components=[support, website])

    @commands.slash_command(
            name="add-roles", 
            description="Add a specific role to all users"
    )
    async def addroles(
        self, interaction: disnake.MessageCommandInteraction,
        role: disnake.Role = commands.Param(
            name="role",
            description="The role to add to all users",
            required=True
        )
    ):
        total_members = len(interaction.guild.members)
        failed_members = []

        if not role.permissions.administrator:
            msg = await interaction.send(embed=disnake.Embed(
                title=f"<a:loading:1168599537682755584> Please wait...",
                description=f"Adding {role.mention} to **{total_members}** members.\n"
                            f"Please do not delete this message, until the proccess is done.",
                color=0x2F3136
            ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))

            for member in interaction.guild.members:
                try:
                    await member.add_roles(role)
                except disnake.Forbidden:
                    failed_members.append(member)

            if failed_members:
                failed_count = len(failed_members)
                await msg.edit(embed=disnake.Embed(
                    description=f"Successfully added role to **{total_members - failed_count}/{total_members}** members. "
                                f"Failed to add role to **{failed_count}** members.",
                    color=0x2F3136
                ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))
            else:
                await msg.edit(embed=disnake.Embed(
                    description=f"Successfully added role to all **{total_members}** members.",
                    color=0x2F3136
                ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))
        else:
            await interaction.send(embed=disnake.Embed(
                description=f"<a:error:1168599839899144253> | Sorry, this role has administrator permissions," 
                            f"so I can't give it to all members",
                color=0xFF0000
            ))

    @commands.slash_command(
            name="remove-roles", 
            description="Remove a specific role from all users"
    )
    async def removeroles(
        self, interaction: disnake.MessageCommandInteraction,
        role: disnake.Role = commands.Param(
            name="role",
            description="The role to remove from all users",
            required=True
        )
    ):
        total_members = len(interaction.guild.members)
        failed_members = []

        if not role.permissions.administrator:
            msg = await interaction.send(embed=disnake.Embed(
                title=f"<a:loading:1168599537682755584> Please wait...",
                description=f"Removing {role.mention} from **{total_members}** members.\n"
                            f"Please do not delete this message, until the proccess is done.",
                color=0x2F3136
            ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))

            for member in interaction.guild.members:
                try:
                    await member.remove_roles(role)
                except disnake.Forbidden:
                    failed_members.append(member)

            if failed_members:
                failed_count = len(failed_members)
                await msg.edit(embed=disnake.Embed(
                    description=f"Successfully removed role from **{total_members - failed_count}/{total_members}** members. "
                                f"Failed to remove role from **{failed_count}** members.",
                    color=0x2F3136
                ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))
            else:
                await msg.edit(embed=disnake.Embed(
                    description=f"Successfully removed role from all **{total_members}** members.",
                    color=0x2F3136
                ).set_footer(text=f"Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar))
        else:
            await interaction.send(embed=disnake.Embed(
                description=f"<a:error:1168599839899144253> | Sorry, this role has administrator permissions," 
                            f"so I can't remove it from all members",
                color=0xFF0000
            ))

    


def setup(bot: commands.Bot):
    bot.add_cog(BasicUtility(bot=bot))
