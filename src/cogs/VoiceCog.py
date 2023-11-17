import datetime

import disnake
import mafic
from disnake.ext import commands
from disnake.ui import View

from src.utils import private_rooms, main_db
from src.utils.misc import EmbedPaginator
from src.utils.rooms import Buttons


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
    def __init__(self, message_id: int, *, timeout: float | None = None) -> None:
        self.message_id = message_id
        self.settings_db = main_db
        super().__init__(timeout=timeout)

    @disnake.ui.button(label="Skip", style=disnake.ButtonStyle.green)
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

    @disnake.ui.button(label="Resume/Pause", style=disnake.ButtonStyle.gray)
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

    @disnake.ui.button(label="Queue", style=disnake.ButtonStyle.blurple)
    async def queue(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        player: MusicPlayer

        if player := interaction.guild.voice_client:  # type: ignore
            embed = disnake.Embed(
                title="Music Queue",
                description="",
                color=self.settings_db.get_embed_color(interaction.guild.id),
            )

            if len(player.queue) > 0:
                for index, music in enumerate(player.queue, start=1):
                    if index > 10:
                        break

                    embed.description += (
                        f"`{index}.` **{music.author} - {music.title}**\n"
                    )

                embed.set_footer(text="Page 1")

                paginator = EmbedPaginator(
                    interaction, interaction.user, embed, player.queue[10:], None, 10
                )
                return await paginator.send_message(interaction)
            else:
                embed.description = "No music in the queue\n"

            embed.set_footer(text="Synth © 2023 | All Rights Reserved")

            await interaction.response.send_message(embed=embed)

    @disnake.ui.button(label="Disconnect", style=disnake.ButtonStyle.danger)
    async def dc(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction):
        player: MusicPlayer

        if player := interaction.guild.voice_client:  # type: ignore
            await player.disconnect()
            await interaction.response.send_message(
                embed=disnake.Embed(
                    title="Disconnecting...",
                    description="I have disconnected from voice channel",
                    color=self.settings_db.get_embed_color(interaction.guild.id),
                ),
                ephemeral=True,
            )


class Music(commands.Cog, name="Voice Commands"):
    """Music commands"""

    EMOJI = "🎶"

    def __init__(self, bot: commands.Bot):
        super(Music, self).__init__()
        self.bot = bot
        self.pool = mafic.NodePool(self.bot)
        self.bot.loop.create_task(self.add_nodes())
        self.private_rooms = private_rooms
        self.settings_db = main_db

    async def cog_load(self) -> None:
        await self.private_rooms.fetch_and_cache_all()

    async def add_nodes(self):
        await self.pool.create_node(
            label="MAIN",
            host="localhost",
            port=2333,
            password="youshallnotpass",
        )

    # async def cog_load(self) -> None:
    #     async def setup_hook(self) -> None:
    #         sc = spotify.SpotifyClient(
    #             client_id='35e4a1289f4745f494aa9e6c418c9a0a',
    #             client_secret='2fe747df85f34bbdb23557e7ce31dc9b'
    #         )
    #         node: wavelink.Node = wavelink.Node(uri='http://localhost:2333', password='youshallnotpass')
    #         await wavelink.NodePool.connect(client=self.bot, nodes=[node], spotify=sc)

    ########################
    #        MUSIC         #
    ########################

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str = None):
        """
        Play a song from spotify
        """
        if not query:
            return await ctx.send("Please provide a query/URL to search")

        if not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first")

        voice = ctx.author.voice.channel

        player: MusicPlayer = ctx.guild.voice_client or await voice.connect(
            cls=MusicPlayer  # type: ignore
        )

        tracks = await player.fetch_tracks(query, search_type="spsearch")
        if not tracks:
            return await ctx.send("No tracks found.")

        embed = disnake.Embed(color=self.settings_db.get_embed_color(ctx.guild.id))

        if player.current:
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
            message = await voice.send(embed=embed, delete_after=15)
            await message.edit(embed=embed, delete_after=15, view=QueueView(message.id))

        else:
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

                message = await voice.send(embed=embed)
                return await message.edit(embed=embed, view=QueueView(message.id))
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
                embed.add_field(
                    name="Message deletion in:",
                    value=f"**`15 seconds`**",
                    inline=True,
                )
                embed.set_image(url=tracks[0].artwork_url)

                embed.set_footer(text="Synth © 2023 | All Rights Reserved")

            message = await voice.send(embed=embed, delete_after=15)
            await message.edit(embed=embed, delete_after=15, view=QueueView(message.id))

    @commands.Cog.listener()
    async def on_track_end(self, event: mafic.TrackEndEvent[MusicPlayer]):
        if event.player.queue:
            track = event.player.queue.pop(0)
            await event.player.play(track)

            embed = disnake.Embed(
                title=f"Now playing - {track.title}",
                description=f"[{track.title}]({str(track.uri)})",
                color=self.settings_db.get_embed_color(event.guild.id),
            )
            embed.add_field(name="Artist:", value=f"**`{track.author}`**", inline=True)
            embed.add_field(
                name="Duration:",
                value=f"`{str(datetime.timedelta(seconds=round(track.length / 1000)))}`",
                inline=True,
            )
            embed.set_footer(text="Synth © 2023 | All Rights Reserved")
            embed.set_image(url=track.artwork_url)

            # Send the embed message and store the message ID
            message = await event.player.voice_channel.send(embed=embed)

            # Pass the message ID to the QueueView constructor
            return await message.edit(
                embed=embed, view=QueueView(message_id=message.id)
            )
        else:
            return await event.player.disconnect(force=True)

    @commands.Cog.listener()
    async def on_track_start(self, event: mafic.TrackStartEvent) -> None:
        assert isinstance(event.player, MusicPlayer)

    #####################
    ### PRIVATE ROOMS ###
    #####################

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.guild:
            if rooms := await self.private_rooms.get_private_room(
                message.guild.id, to_return="channels"
            ):
                for room in rooms:
                    if message.channel.id == room and message.author.id != self.bot.user.id:
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

    @commands.command(
        name="setup-voice",
        aliases=["voice-setup", "voice-s", "setup-v", "vs"],
    )
    async def setup_voice(self, ctx: commands.Context):
        """
        Creates a voice channel for private rooms
        """
        message = await ctx.send(
            embed=disnake.Embed(
                title="Voice Setup", description="Please, wait...", color=0x2F3236
            )
        )
        voice = await ctx.guild.create_voice_channel(
            name="Create a private room", reason="Voice Setup"
        )
        await message.edit(
            embed=disnake.Embed(
                title="Voice Setup",
                description="Successfully created the private room\nFinalizing...",
                color=0x2F3236,
            )
        )
        await self.private_rooms.create_main_room(ctx.guild.id, voice)
        await message.edit(
            embed=disnake.Embed(
                title="Voice Rooms Setup",
                description=f"Successfully created the private room. Channel: {voice.mention}",
                color=0x2F3236,
            )
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Music(bot))
