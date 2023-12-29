import datetime

import disnake
import mafic
from disnake import Message
from disnake.ext import commands
from disnake.ui import View

from src.utils import private_rooms, main_db
from src.utils.rooms import Buttons


class PrivateRooms(commands.Cog, name="Private Rooms"):
    """Private Rooms"""

    EMOJI = "🎶"

    def __init__(self, bot: commands.Bot):
        super(PrivateRooms, self).__init__()
        self.bot = bot
        self.private_rooms = private_rooms
        self.settings_db = main_db

    async def cog_load(self) -> None:
        await self.private_rooms.fetch_and_cache_all()

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.guild:
            if rooms := await self.private_rooms.get_private_room(
                message.guild.id, to_return="channels"
            ):
                for room in rooms:
                    if (
                        message.channel.id == room
                        and message.author.id != self.bot.user.id
                    ):
                        await message.delete()
                        break

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState,
    ):
        if after.channel and len(after.channel.members) != 0:
            is_main_room = await self.private_rooms.get_private_room(
                member.guild.id, to_return="main_channel_id"
            )
            if is_main_room and is_main_room == after.channel.id:
                channel = await member.guild.create_voice_channel(
                    name=f"Room {member.display_name}", category=after.channel.category
                )
                await member.move_to(channel=channel)

                embed = disnake.Embed(
                    title="Private Rooms Settings",
                    colour=0x2F3136,
                )
                embed.description = """
                    <:store:1169690541986959464> - edit channel name
                    <:members:1169684583369949285> - change user count
                    <:list:1169690529643114547> - remove the slot limit
                    <:invite:1169690514430382160> - open/close the room for everyone
                    <:ban:1170712517308317756> - kick user from the room
                    <:hammer:1169685339720384512> - give/remove access for the room
                    <:mute:1170712518725992529> - mute/unmute user
                    <:owner:1169684595697004616> - transfer ownership of the room
                """
                await channel.send(
                    content=member.mention,
                    embed=embed,
                    view=Buttons(bot=self.bot, author=member, channel=channel),
                )
                await self.private_rooms.create_private_room(member, channel)
                return
        elif before.channel and len(before.channel.members) == 0:
            if room_channels := await self.private_rooms.get_private_room(
                member.guild.id, to_return="channels"
            ):
                for room in room_channels:
                    if room_id := room.get("channel_id", None):
                        if room_id == before.channel.id:
                            await before.channel.delete()
                            await self.private_rooms.delete_private_room(
                                member, before.channel
                            )
                            break

        elif after.channel != before.channel and member.voice.mute:
            await member.edit(mute=False)

    @commands.slash_command(name="setup-voice")
    async def setup_voice(self, interaction: disnake.MessageCommandInteraction):
        """
        Creates a voice channel for private rooms
        """
        await interaction.send(
            embed=disnake.Embed(
                title="Voice Setup", description="Please, wait...", color=0x2F3236
            )
        )
        voice = await interaction.guild.create_voice_channel(
            name="Create a private room", reason="Voice Setup"
        )
        await interaction.edit_original_message(
            embed=disnake.Embed(
                title="Voice Setup",
                description="Successfully created the private room\nFinalizing...",
                color=0x2F3236,
            )
        )
        await self.private_rooms.create_main_room(interaction.guild_id, voice)
        await interaction.response.defer()
        await interaction.edit(
            embed=disnake.Embed(
                title="Voice Rooms Setup",
                description=f"Successfully created the private room. Channel: {voice.mention}",
                color=0x2F3236,
            )
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(PrivateRooms(bot))
