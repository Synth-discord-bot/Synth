from typing import Union

import disnake
from disnake import Localized
from disnake.ext import commands
from disnake.utils import format_dt

from src.utils.misc import check_if_user_is_developer

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
            1048576: "⚠️",
            133172312: "<:synth_dev:1168623393717899314>"
        }

    @commands.slash_command(name = Localized("user", key = "USER_COMMAND_NAME"), description = Localized("Display information about user.", key = "USER_COMMAND_DESC"))
    async def user(self, interaction: disnake.MessageCommandInteraction, user: Union[disnake.User, disnake.Member] = commands.Param(description=Localized("Choice user", key="USER_COMMAND_USER_DESC"), name = Localized("user", key="USER_COMMAND_USER_NAME"), default = None)):
        if user is None:
            user = interaction.user
        
        embed = disnake.Embed(
            title = f"@{user.name} / {user.id} {'' if not check_if_user_is_developer(bot=self.bot, user_id=user.id) else ' <:synth_dev:1168623393717899314>'}",
            color = 0x2b2d31,
            description = f"[Link to DM](discord://discord.com/users/{user.id})",
        )
        embed.add_field(name="Created at", value=format_dt(user.created_at, style="f"), inline=False)

        embed.set_thumbnail(url=user.display_avatar.url)
        if user.banner:
            embed.set_image(url=user.banner.url)
            
        if isinstance(user, disnake.Member):
            embed.add_field(name = "Joined at", value=format_dt(user.joined_at, style="f"), inline=False)
            embed.add_field(name="Status", value=user.status, inline=False)
            embed.add_field(name="Is on mobile?", value=user.is_on_mobile(), inline=False)
            embed.add_field(
                name="Roles:", 
                value = " ".join(
                    [
                        role.mention 
                        for role in user.roles 
                        if not role.is_default() 
                        and role.name != "@everyone"
                    ]
                ), 
                inline=False
                )
            embed.add_field(name="Top role", value=user.top_role.mention, inline=False)
        
        flags = " ".join([user_badges for badge, user_badges in self.badges.items() if user.public_flags._has_flag(badge)])
        
        if flags != "":
            embed.add_field(name="Flags", value=flags, inline=False)
        
        await interaction.send(embed=embed)
        
    @commands.slash_command(name=Localized("server", key="SERVER_COMMAND_NAME"), description = Localized("Display information about server.", key="SERVER_COMMAND_DESC"))
    async def server(self, interaction: disnake.MessageCommandInteraction):
        emoji_count = len(interaction.guild.emojis)
        list_of_bots = len([m for m in interaction.guild.members if m.bot])
        list_of_users = len([m for m in interaction.guild.members if not m.bot])

        embed = disnake.Embed(
            title = f"{interaction.guild.name}'s information",
            color = 0x2b2d31
        )
        embed.add_field(
            name="<:gear:1168228790183415868> Main Information",
            value = f"**Emojis:** `{emoji_count}`\n"
                    f"**Members:** `{len(interaction.guild.members)}`\n"
                    f"**Owner:** `{interaction.guild.owner}`\n"
                    f"**Roles:** `{len(interaction.guild.roles)}`\n"
                    f"**Created at:** {format_dt(interaction.guild.created_at, style='f')}\n"
                    f"**Icon:** [click]({interaction.guild.icon})\n"
                    f"**Boost:** `{interaction.guild.premium_subscription_count}`\n",
            inline=True
        )
        
        embed.add_field(
            name="<:link:1168250171524649060> Server Channels",
            value = f"**Channels:** `{len(interaction.guild.channels)}`\n"
                    f"**Text Channels:** `{len(interaction.guild.text_channels)}`\n"
                    f"**Voice Channels:** `{len(interaction.guild.voice_channels)}`\n"
                    f"**Categories:** `{len(interaction.guild.categories)}`\n"
                    f"**Threads:** `{len(interaction.guild.threads)}`\n",
            inline=True
        )

        embed.add_field(
            name="<:settings:1168250174611660971> Server Members",
            value = f"**All Members:** `{len(interaction.guild.members)}`\n"
                    f"**Humans:** `{list_of_users}`\n"
                    f"**Bots:** `{list_of_bots}`\n"
                    f"**Administrators:** `{len([r for r in interaction.guild.roles if r.permissions.administrator])}`\n"
                    f"**Moderators:** `{len([r for r in interaction.guild.roles if r.permissions.kick_members])}`\n"
                    f"**Joined at:** {format_dt(interaction.user.joined_at, style='f')}",
            inline=False
        )

        embed.set_thumbnail(url=interaction.guild.icon)
        embed.set_image(url=interaction.guild.banner)
        await interaction.send(embed=embed)

        

def setup(bot: commands.Bot):
    bot.add_cog(BasicUtility(bot = bot))