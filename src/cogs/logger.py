import datetime

import disnake
from disnake.ext import commands
from disnake.ext.commands import TextChannelConverter

from src.utils import logger
from src.utils.misc import check_channel


class LogsCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.logger = logger

    async def cog_load(self):
        await self.logger.fetch_and_cache_all()

    @commands.slash_command(name="logger")
    async def logger(self, _: disnake.ApplicationCommandInteraction):
        pass

    @logger.sub_command(name="set_channel")
    async def set_log_channel(
        self,
        interaction: disnake.MessageCommandInteraction,
        main_log_channel: disnake.TextChannel,
        guild_log_channel: disnake.TextChannel = None,
        invite_log_channel: disnake.TextChannel = None,
        message_log_channel: disnake.TextChannel = None,
    ):
        main_log = await check_channel(
            channel=main_log_channel, interaction=interaction
        )
        if main_log:
            guild_log = invite_log = message_log = False
            if guild_log_channel:
                guild_log = await check_channel(
                    channel=guild_log_channel, interaction=interaction
                )
            if invite_log_channel:
                invite_log = await check_channel(
                    channel=invite_log_channel, interaction=interaction
                )
            if message_log_channel:
                message_log = await check_channel(
                    channel=message_log_channel, interaction=interaction
                )
            await self.logger.create_logger(
                guild_id=interaction.guild,
                main_log_channel=main_log_channel,
                guild_log_channel=(
                    guild_log_channel
                    if guild_log_channel is not None and guild_log
                    else main_log_channel
                ),
                invite_log_channel=(
                    invite_log_channel
                    if invite_log_channel is not None and invite_log
                    else main_log_channel
                ),
                message_log_channel=(
                    message_log_channel
                    if message_log_channel is not None and message_log
                    else main_log_channel
                ),
            )
            return await interaction.edit_original_response(
                embed=disnake.Embed(
                    title="Logger",
                    description="Successfully setup loggers to channel(s)!",
                )
            )
        return
        # # title
        # await interaction.send("Please send channel id/mention to setup main log channel", delete_after=15)
        # message = await self.bot.wait_for(
        #     "message", check=lambda x: x.author == interaction.author, timeout=15
        # )
        # main_channel = await TextChannelConverter().convert(ctx=interaction, argument=message.channel.id)
        # await message.delete()

        # # description
        # await interaction.channel.send(
        #     f"New title: `{name}`.\n\nWrite new description:"
        # )
        # msg = await self.bot.wait_for(
        #     "message", check=lambda x: x.author == interaction.author, timeout=None
        # )
        # description = msg.content
        # await msg.delete()
        #
        # # channel
        # await interaction.channel.send(
        #     f"New title: `{name}`\n\nNew description: `{msg.content}`. Write id or mention of channel:",
        #     delete_after=30,
        # )
        # msg = await self.bot.wait_for(
        #     "message", check=lambda x: x.author == interaction.author, timeout=None
        # )
        # channel_id = msg.content
        # await msg.delete()
        # msg = await interaction.channel.send("Checking channel..")
        #
        # # convert string to channel
        # try:
        #     channel = await TextChannelConverter().convert(
        #         ctx=interaction, argument=channel_id  # type: ignore
        #     )
        # except BadArgument:
        #     return await msg.edit("This channel does not exist.", delete_after=10)
        #
        # try:
        #     await channel.send(".", delete_after=0.05)
        #     channel_id = channel.id
        # except (disnake.HTTPException, disnake.Forbidden, TypeError):
        #     return await msg.edit(
        #         "This channel does not have permissions to send messages."
        #     )
        #
        # # TODO: Добавить возможность изменять цвет формы (или кнопки/dropdown menu??).
        # #  Изменять текст в кпопке или dropdown menu
        # await self.forms.update_form_info(
        #     guild_id=interaction.guild.id,
        #     form_name=name,
        #     form_description=description,
        #     form_channel_id=channel_id,
        #     form_type=form_type,
        # )
        # embed = disnake.Embed(title=name, description=description, color=0x2F3136)
        # await channel.send(embed=embed)
        # return await msg.edit("Form has been created", delete_after=10)
        # await check_channel(channel=channel, interaction=interaction)


def setup(bot: commands.Bot):
    bot.add_cog(LogsCog(bot))
