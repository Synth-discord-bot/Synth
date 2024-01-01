import datetime
from typing import Dict

import disnake
import mafic
from disnake import Message
from disnake.ext import commands
from disnake.ui import View

from src.utils import main_db
from src.utils.misc import EmbedPaginator


class MusicPlayer(mafic.Player[commands.Bot]):
    def __init__(
        self,
        client: commands.Bot,
        channel: disnake.VoiceChannel,
    ) -> None:
        super().__init__(client, channel)

        self.queue: list[mafic.Track] = []
        self.voice_channel: disnake.VoiceChannel = channel


class QueueView(View):
    def __init__(
        self, bot: commands.bot, message_id: int, *, timeout: float | None = None
    ) -> None:
        self.message_id = message_id
        self.bot = bot
        super().__init__(timeout=timeout)

    @disnake.ui.button(label="Skip", style=disnake.ButtonStyle.green, row=0)
    async def skip(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        player: MusicPlayer

        if player := interaction.guild.voice_client:  # type: ignore
            if not player.queue:
                return await interaction.response.send_message(
                    "Sorry, the music queue is empty!",
                    ephemeral=True,
                )

            try:
                await player.stop()
                message = await interaction.channel.fetch_message(self.message_id)
                await message.delete()
                await interaction.response.defer()

            except (mafic.PlayerNotConnected, disnake.Forbidden):
                return await interaction.send(
                    "Sorry, there was an error while processing your request.",
                    ephemeral=True,
                )

    @disnake.ui.button(label="Resume/Pause", style=disnake.ButtonStyle.gray, row=0)
    async def resume_and_pause(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        player: MusicPlayer

        if player := interaction.guild.voice_client:  # type: ignore
            if player.paused:
                await player.resume()
                await interaction.response.edit_message(content=f"")
            else:
                await player.pause()
                await interaction.response.edit_message(content=f"")

    @disnake.ui.button(label="Volume", style=disnake.ButtonStyle.green, row=0)
    async def _volume(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        player: MusicPlayer

        if player := interaction.guild.voice_client:  # type: ignore
            modal = disnake.ui.Modal(
                title="Enter the volume",
                custom_id="volume",
                components=[
                    disnake.ui.TextInput(
                        label="New volume:",
                        custom_id="new_volume",
                        style=disnake.TextInputStyle.short,
                    )
                ],
            )
            await interaction.response.send_modal(modal=modal)
            response_modal = await self.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == "volume" and i.user == interaction.user,
            )
            new_volume = int(response_modal.text_values["new_volume"])
            
            error_embed = disnake.Embed(color=disnake.Color.red())
            if new_volume > 100 or new_volume < 1:
                error_embed.title = f"Please enter a number, between `1` and `100`"
                return await response_modal.response.send_message(embed=error_embed, ephemeral=True)

            await player.set_volume(new_volume)
            embed = disnake.Embed(
                title=f"Set volume to {new_volume}", color=disnake.Color.green()
            )
            await response_modal.response.send_message(embed=embed, ephemeral=True)

    @disnake.ui.button(label="Queue", style=disnake.ButtonStyle.blurple, row=1)
    async def queue(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        player: MusicPlayer

        if player := interaction.guild.voice_client:  # type: ignore
            embed = disnake.Embed(
                title="Music Queue",
                description="",
                color=0x2F3236,
            )

            if len(player.queue) > 0:
                for index, music in enumerate(player.queue, start=1):
                    if index > 10:
                        break

                    embed.description += (
                        f"`{index}.` **{music.author} - {music.title}**\n"
                    )

                embed.set_footer(text="Page 0")

                paginator = EmbedPaginator(
                    interaction, interaction.user, embed, player.queue[10:], None, 10
                )
                return await paginator.send_message(interaction)
            else:
                embed.description = "No music in the queue\n"

            embed.set_footer(text="Synth © 2023 | All Rights Reserved")

            await interaction.response.send_message(embed=embed, ephemeral=True)

    @disnake.ui.button(label="Disconnect", style=disnake.ButtonStyle.danger, row=1)
    async def dc(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction):
        player: MusicPlayer

        if player := interaction.guild.voice_client:  # type: ignore
            await player.disconnect()
            await interaction.response.send_message(
                embed=disnake.Embed(
                    title="Disconnecting...",
                    description="I have disconnected from voice channel",
                    color=0x2F3236,
                ),
                ephemeral=True,
            )


class Music(commands.Cog, name="Music Commands"):
    """Commands that help you to manage music."""

    EMOJI = "🎶"

    def __init__(self, bot: commands.Bot):
        super(Music, self).__init__()
        self.bot = bot
        self.pool = mafic.NodePool(self.bot)
        self.bot.loop.create_task(self.add_nodes())
        self.channels: Dict[int, disnake.TextChannel] = {}  # guild_id: channel

    async def add_nodes(self) -> None:
        await self.pool.create_node(
            label="MAIN",
            host="localhost",
            port=2333,
            password="youshallnotpass",
        )

    @commands.slash_command(description="Search and play music from Spotify")
    async def play(
        self, interaction: disnake.MessageCommandInteraction, *, query: str = None
    ):
        ErrorEmbed = disnake.Embed(color=disnake.Color.red())
        if not query:
            ErrorEmbed.title = "Please provide a query/URL to search"
            return await interaction.send(embed=ErrorEmbed, ephemeral=True)

        if not getattr(interaction.author.voice, "channel", None):
            ErrorEmbed.title = "Join a voice channel first"
            return await interaction.send(embed=ErrorEmbed, ephemeral=True)

        voice = interaction.author.voice.channel

        player: MusicPlayer = interaction.guild.voice_client or await voice.connect(
            cls=MusicPlayer  # type: ignore
        )

        tracks = await player.fetch_tracks(query, search_type="spsearch")

        if not tracks:
            ErrorEmbed.title = f"No tracks found, by `{query}` query..."
            return await interaction.send(embed=ErrorEmbed)

        embed = disnake.Embed(color=0x2F3236)

        # self.invoked_channel = interaction.channel.id
        self.channels[interaction.guild.id] = interaction.channel

        if player.current:
            await interaction.response.defer()

            embed.title = "Queue"

            if isinstance(tracks, mafic.Playlist):
                player.queue.extend(tracks.tracks)
                embed.description = f"Added playlist **{tracks.name}** ({len(tracks.tracks)} tracks) to the queue."
            else:
                player.queue.append(tracks[0])
                embed.description = f"Added track **[{tracks[0].title}]({str(tracks[0].uri)})** to the queue."
                embed.add_field(
                    name="Artist:", value=f"**`{tracks[0].author}`**", inline=True
                )
                embed.add_field(
                    name="Duration:",
                    value=f"`{str(datetime.timedelta(seconds=round(tracks[0].length / 1000)))}`",
                    inline=True,
                )
                embed.add_field(
                    name="Message deletion in:",
                    value=f"**`15 seconds`**",
                    inline=True,
                )
                embed.set_image(url=tracks[0].artwork_url)

            embed.set_footer(text="Synth © 2023 | All Rights Reserved")
            message = await interaction.followup.send(embed=embed, delete_after=15)
            await message.edit(embed=embed, view=QueueView(self.bot, message.id))

        else:
            await interaction.response.defer()

            if isinstance(tracks, mafic.Playlist):
                player.queue.extend(tracks.tracks[1:])
                await player.play(tracks.tracks[0])

                embed.title = f"Now playing - {tracks.tracks[0].title}"
                embed.description = (
                    f"[{tracks.tracks[0].title}]({str(tracks.tracks[0].uri)})"
                    f"\nAdded playlist {tracks.name} ({len(tracks.tracks) - 1} tracks) to the queue."
                )
                embed.add_field(
                    name="Artist:",
                    value=f"**`{tracks.tracks[0].author}`**",
                    inline=True,
                )
                embed.add_field(
                    name="Duration:",
                    value=f"`{str(datetime.timedelta(seconds=round(tracks.tracks[0].length / 1000)))}`",
                    inline=True,
                )
                embed.set_image(url=tracks.tracks[0].artwork_url)

                message = await interaction.followup.send(embed=embed)
                return await message.edit(
                    embed=embed, view=QueueView(self.bot, message.id)
                )
            else:
                await player.play(tracks[0])

                embed.title = f"Now playing - {tracks[0].title}"
                embed.description = f"[{tracks[0].title}]({str(tracks[0].uri)})"
                embed.add_field(
                    name="Artist:", value=f"**`{tracks[0].author}`**", inline=True
                )
                embed.add_field(
                    name="Duration:",
                    value=f"`{str(datetime.timedelta(seconds=round(tracks[0].length / 1000)))}`",
                    inline=True,
                )
                embed.set_image(url=tracks[0].artwork_url)

                embed.set_footer(text="Synth © 2023 | All Rights Reserved")

            message = await interaction.followup.send(embed=embed)
            await message.edit(embed=embed, view=QueueView(self.bot, message.id))

    @commands.Cog.listener()
    async def on_track_end(self, event: mafic.TrackEndEvent[MusicPlayer]):
        if not event.player.queue or event.player.voice_channel.members == 0:
            if event.player.guild.id in self.channels:
                del self.channels[event.player.guild.id]

            return await event.player.disconnect()

        track = event.player.queue.pop(0)
        await event.player.play(track)

        embed = disnake.Embed(
            title=f"Now playing - {track.title}",
            description=f"[{track.title}]({str(track.uri)})",
            color=0x2F3236,
        )
        embed.add_field(name="Artist:", value=f"**`{track.author}`**", inline=True)
        embed.add_field(
            name="Duration:",
            value=f"`{str(datetime.timedelta(seconds=round(track.length / 1000)))}`",
            inline=True,
        )
        embed.set_footer(text="Synth © 2023 | All Rights Reserved")
        embed.set_image(url=track.artwork_url)

        if channel := self.channels.get(event.player.guild.id):
            message = await channel.send(embed=embed)

            return await message.edit(
                embed=embed, view=QueueView(self.bot, message_id=message.id)
            )

    @commands.Cog.listener()
    async def on_track_start(self, event: mafic.TrackStartEvent) -> None:
        assert isinstance(event.player, MusicPlayer)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Music(bot))
