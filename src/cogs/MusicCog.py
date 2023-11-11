import disnake
from disnake.ext import commands
from disnake.ui import View
import mafic
import datetime


class MusicPlayer(mafic.Player[commands.Bot]):
    def __init__(
        self,
        client: commands.Bot,
        channel: disnake.VoiceChannel,
    ) -> None:
        super().__init__(client, channel)

        # Mafic does not provide a queue system right now, low priority.
        self.queue: list[mafic.Track] = []
        self.voice_channel: disnake.VoiceChannel = channel


class QueueView(View):
    def __init__(self, *, timeout: float | None = None) -> None:
        super().__init__(timeout=timeout)

    @disnake.ui.button(label="Skip", style=disnake.ButtonStyle.green)
    async def skip(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        player: MusicPlayer

        if player := interaction.guild.voice_client:  # type: ignore
            if not player.queue:
                return await interaction.response.send_message(
                    "Queue is empty, write `>>play` to play some music or I will disconnect at the end of the music!",
                    ephemeral=True,
                )

            try:
                track = player.queue.pop(0)
                await player.play(track)
                await interaction.send(
                    "Successfully skipped", ephemeral=True, delete_after=2
                )
                await interaction.delete_original_response()

            except (mafic.PlayerNotConnected, disnake.Forbidden):
                return await interaction.send(
                    "Queue empty, write `>>play` to play some music or I will disconnect at the end of the music!",
                    ephemeral=True,
                )

    @disnake.ui.button(label="Resume/Pause", style=disnake.ButtonStyle.blurple)
    async def resume_and_pause(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        player: MusicPlayer

        if player := interaction.guild.voice_client:  # type: ignore
            if player.paused:
                await player.resume()
                await interaction.response.edit_message(
                    content=f"Resumed track [{player.current.title}]({str(player.current.uri)})"
                )
            else:
                await player.pause()
                # await interaction.defer()
                await interaction.response.edit_message(
                    content=f"Paused track [{player.current.title}]({str(player.current.uri)})"
                )

    @disnake.ui.button(label="Disconnect", style=disnake.ButtonStyle.danger)
    async def dc(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction):
        player: MusicPlayer

        if player := interaction.guild.voice_client:  # type: ignore
            await player.disconnect()
            await interaction.response.send_message(
                embed=disnake.Embed(
                    title="Disconnect",
                    description="I have disconnected",
                    color=0x2F3136,
                )
            )


class Music(commands.Cog):
    """Music commands"""

    def __init__(self, bot: commands.Bot):
        super(Music, self).__init__()
        self.bot = bot
        self.pool = mafic.NodePool(self.bot)
        self.bot.loop.create_task(self.add_nodes())

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

    @commands.Cog.listener()
    async def on_track_end(self, event: mafic.TrackEndEvent[MusicPlayer]):
        if event.player.queue:
            await event.player.play(event.player.queue.pop(0))

    @commands.Cog.listener()
    async def on_track_start(self, event: mafic.TrackStartEvent) -> None:
        if event.player.queue:
            await event.player.play(event.player.queue.pop(0))

        if event.track:
            embed = disnake.Embed(
                title=f"Now playing - {event.track.title}",
                description=f"[{event.track.title}]({str(event.track.uri)})",
                color=0x2F3136,
            )
            embed.add_field(
                name="Artist:", value=f"**`{event.track.author}`**", inline=True
            )
            embed.add_field(
                name="Duration:",
                value=f"**`{str(datetime.timedelta(milliseconds=event.track.length))}`**",
                inline=True,
            )
            embed.set_footer(text="Synth © 2023 | All Rights Reserved")
            return await event.player.voice_channel.send(
                embed=embed,
                view=QueueView(),
                delete_after=datetime.timedelta(
                    milliseconds=event.track.length
                ).total_seconds(),
            )
        return await event.player.disconnect(force=True)

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        if not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("Join a voice channel first")

        voice = ctx.author.voice.channel

        player: MusicPlayer = ctx.guild.voice_client or await voice.connect(
            cls=MusicPlayer  # type: ignore
        )

        tracks = await player.fetch_tracks(query)
        if not tracks:
            return await ctx.send("No tracks found.")

        embed = disnake.Embed(color=0x2F3136)

        if player.current:
            embed.title = "Queue"
            if isinstance(tracks, mafic.Playlist):
                player.queue.extend(tracks.tracks[1:])
                embed.description = f"Added playlist {tracks.name} ({len(tracks.tracks)} tracks) to the queue."
            else:
                player.queue.append(tracks[0])
                embed.description = f"Added track [{tracks[0].title}]({str(tracks[0].uri)}) to the queue."
                embed.add_field(
                    name="Artist:", value=f"**`{tracks[0].author}`**", inline=True
                )
                embed.add_field(
                    name="Duration:",
                    value=f"**`{str(datetime.timedelta(milliseconds=tracks[0].length))}`**",
                    inline=True,
                )

            embed.set_footer(text="Synth © 2023 | All Rights Reserved")
            return await voice.send(embed=embed, delete_after=15)
        else:
            await player.play(tracks[0])


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Music(bot))
