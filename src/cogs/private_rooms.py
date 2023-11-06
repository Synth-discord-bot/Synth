import disnake
from disnake.ext import commands

from src.utils import private_rooms, PrivateRoomsDatabase


class Buttons(disnake.ui.View):
    def __init__(
        self,
        bot: commands.Bot,
        author: disnake.Member,
        channel: disnake.VoiceChannel,
        voices: PrivateRoomsDatabase = private_rooms,
    ):
        super().__init__(timeout=0)
        self.bot = bot
        self.author = author
        self.voices = voices
        self.channel = channel

    @disnake.ui.button(label="🖊")
    async def pen_callback(
        self, _: disnake.ui.button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            content="Напишите новое название комнаты", ephemeral=True
        )
        msg = await self.bot.wait_for(
            "message", check=lambda x: x.author == interaction.author, timeout=15
        )
        await self.channel.edit(name=msg.content)
        await msg.delete()

    @disnake.ui.button(label="👥")
    async def _users(
        self, _: disnake.ui.button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            content="Введите лимит (например: 9)", ephemeral=True
        )
        msg = await self.bot.wait_for(
            "message", check=lambda x: x.author == interaction.author, timeout=15
        )
        if msg.content.isdigit():
            await self.channel.edit(user_limit=int(msg.content))
        await msg.delete()

    @disnake.ui.button(label="🕵️")
    async def _unlock_slot(
        self, _: disnake.ui.button, interaction: disnake.MessageInteraction
    ):
        await self.channel.edit(user_limit=0)
        await interaction.response.send_message(
            content="Успешно убрал лимит для входа в эту комнату", ephemeral=True
        )

    @disnake.ui.button(label="🔒")
    async def _lock(
        self, _: disnake.ui.button, interaction: disnake.MessageInteraction
    ):
        await self.channel.set_permissions(
            interaction.guild.default_role, connect=False
        )
        await interaction.response.send_message(
            content="Успешно закрыл доступ для всех участников", ephemeral=True
        )

    @disnake.ui.button(label="🔓")
    async def _unlock(
        self, _: disnake.ui.button, interaction: disnake.MessageInteraction
    ):
        await self.channel.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message(
            content="Успешно открыл доступ для всех участников", ephemeral=True
        )

    @disnake.ui.button(label="🚪")
    async def _door(
        self, _: disnake.ui.button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            content="Упомяните пользователей, для того, чтобы выгнать их",
            ephemeral=True,
        )
        msg = await self.bot.wait_for(
            "message",
            check=lambda x: x.author == interaction.author and x.mentions,
            timeout=15,
        )
        for user in msg.mentions:
            if user.voice.channel == self.channel:
                await user.move_to(channel=None)
        await msg.delete()

    @disnake.ui.button(label="✔")
    async def _access(
        self, _: disnake.ui.button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            content="Упомяните пользователей, которым разрешить вход в комнату",
            ephemeral=True,
        )
        msg = await self.bot.wait_for(
            "message",
            check=lambda x: x.author == interaction.author and x.mentions,
            timeout=15,
        )
        for user in msg.mentions:
            await self.channel.set_permissions(user, connect=True)
        await msg.delete()

    @disnake.ui.button(label="❌")
    async def _do_not_access(
        self, _: disnake.ui.button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            content="Упомяните пользователей, которым не разрешать входить в эту комнату",
            ephemeral=True,
        )
        msg = await self.bot.wait_for(
            "message",
            check=lambda x: x.author == interaction.author and x.mentions,
            timeout=15,
        )
        for user in msg.mentions:
            await self.channel.set_permissions(user, connect=False)
        await msg.delete()

    @disnake.ui.button(label="🔉")
    async def _unmute(
        self, _: disnake.ui.button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            content="Упомяните пользователей, которых надо размутить", ephemeral=True
        )
        msg = await self.bot.wait_for(
            "message",
            check=lambda x: x.author == interaction.author and x.mentions,
            timeout=15,
        )
        for u in msg.mentions:
            await self.channel.set_permissions(u, speak=True)
        await msg.delete()

    @disnake.ui.button(label="🔇")
    async def _mute(
        self, _: disnake.ui.button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            content="Упомяните пользователей, которых надо замутить", ephemeral=True
        )
        msg = await self.bot.wait_for(
            "message",
            check=lambda x: x.author == interaction.author and x.mentions,
            timeout=15,
        )
        for u in msg.mentions:
            await self.channel.set_permissions(u, speak=False)
        await msg.delete()

    @disnake.ui.button(label="👑")
    async def _takeown(
        self, _: disnake.ui.button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            content="Укажите участника, которого сделать владельцем комнаты",
            ephemeral=True,
        )
        msg = await self.bot.wait_for(
            "message",
            check=lambda x: x.author == interaction.author and x.mentions,
            timeout=15,
        )
        await msg.delete()
        await self.voices.set_owner(
            guild_id=interaction.guild_id,
            voice_channel=self.channel,
            member=msg.mentions[0],
        )
        await interaction.edit_original_response("Успешно...")

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if info := self.voices.get_items_in_cache({"guild_id": self.channel.guild.id}):
            for channel in info.get("channels"):
                if channel.get("channel_id") == self.channel.id:
                    if interaction.author.id != channel.get("owner_id"):
                        await interaction.response.send_message(
                            "Вы не можете использовать эти кнопки!", ephemeral=True
                        )
                        return False
            return True


class PrivateRoom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.private_rooms = private_rooms

    async def cog_load(self) -> None:
        await self.private_rooms.fetch_and_cache_all()

    @commands.command(
        name="setup-voice", aliases=["voice-setup", "voice-s", "setup-v", "vs"]
    )
    async def setup_voice(self, ctx: commands.Context):
        message = await ctx.send(
            embed=disnake.Embed(title="Voice Setup", description="Please, wait...")
        )
        voice = await ctx.guild.create_voice_channel(
            name="Create private room", reason="Voice Setup"
        )
        await message.edit(
            embed=disnake.Embed(
                title="Voice Setup",
                description="Successfully created the private room Finalizing...",
            )
        )
        await self.private_rooms.create_main_room(ctx.guild.id, voice)
        await message.edit(
            embed=disnake.Embed(
                title="Voice Setup",
                description=f"Successfully created the private room. Channel: {voice.mention}",
            )
        )

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
                    title="Private Room",
                    description="Choose action:",
                    colour=0x2F3136,
                )
                embed.description += """\n
                            🖊 - edit channel name
                            👥 - change user count
                            🕵️ - Remove the slot limit
                            🔒 - close the room to everyone
                            🔓 - open the room to everyone
                            🚪 - kick user from the room
                            ✔ - allow user access to the room
                            ❌ - disallow user access to the room
                            🔉 - unmute user
                            🔇 - mute user
                            👑 - transfer ownership of the room
                                            """
                view = Buttons(bot=self.bot, author=member, channel=channel)
                await channel.send(content=member.mention, embed=embed, view=view)
                await self.private_rooms.create_private_room(member, channel)
                return
        elif before.channel:
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

    @commands.Cog.listener()
    async def on_message(self, message):
        rooms = await self.private_rooms.get_private_room(
            message.guild.id, to_return="channels"
        )
        if rooms:
            for room in rooms:
                if message.channel.id == room and message.author.id != self.bot.user.id:
                    await message.delete()
                    break


def setup(bot: commands.Bot) -> None:
    bot.add_cog(PrivateRoom(bot))
