import asyncio
import io
from typing import Optional

import disnake
import ujson
from disnake.ext import commands

from src.utils import backups, main_db, commands_db
from src.utils.backup import Backup as BackupGuild
from src.utils.misc import save_file_to_memory, ConfirmEnum, custom_cooldown


class BackupsView(disnake.ui.View):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.backups = backups
        self.settings_db = main_db

    async def confirm(
        self, interaction: disnake.MessageInteraction, embed: disnake.Embed = None
    ) -> Optional[str]:
        buttons = [
            disnake.ui.Button(
                label="Yes",
                custom_id="confirm_yes",
                style=disnake.ButtonStyle.green,
            ),
            disnake.ui.Button(
                label="No", custom_id="confirm_no", style=disnake.ButtonStyle.red
            ),
        ]

        if not embed:
            embed = disnake.Embed(
                title="Confirmation",
                description="Are you sure?",
                color=self.settings_db.get_embed_color(interaction.guild.id),
            )

        await interaction.send(embed=embed, ephemeral=True, components=buttons)

        interaction = await self.bot.wait_for(
            "button_click",
            check=lambda i: i.author == interaction.author
            and i.channel_id == interaction.channel_id,
            timeout=60.0,
        )

        return interaction.data.get("custom_id", None) or None

    @disnake.ui.button(label="Save", style=disnake.ButtonStyle.green)
    async def create_backup(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        embed = disnake.Embed(
            color=self.settings_db.get_embed_color(interaction.guild.id)
        )

        confirm_embed = disnake.Embed(
            title="Confirmation",
            description="Are you sure you want to **create** server backup?",
            color=self.settings_db.get_embed_color(interaction.guild.id),
        )
        response = await self.confirm(interaction=interaction, embed=confirm_embed)
        if response == ConfirmEnum.OK:
            try:
                embed.title = "<a:loading:1168599537682755584> Please wait..."
                embed.description = "Creating a server backup..."
                await interaction.edit_original_response(embed=embed)

                backup_data = await BackupGuild(interaction.guild).create()

                await self.backups.update_backups_info(
                    interaction.guild.id, backup_data
                )

                embed.title = "Finished"
                embed.description = (
                    "Server backup has been successfully created."
                    " Remember to backup this file in a safe place."
                )

                with io.StringIO() as temp_file:
                    ujson.dump(backup_data, temp_file, indent=4)
                    temp_file.seek(0)
                    file_data = temp_file.read().encode()
                    await interaction.edit_original_message(
                        embed=embed,
                        file=disnake.File(
                            fp=io.BytesIO(file_data), filename="backup.json"
                        ),
                        view=None,
                    )

            except (Exception, ExceptionGroup) as e:
                embed.title = "An error occurred"
                embed.description = "An error occurred when trying to save the server."
                await interaction.edit_original_message(embed=embed)
                raise e
        else:
            await interaction.followup.send(
                content="Operation cancelled", embed=None, ephemeral=True
            )
            await interaction.edit_original_message(
                content="Operation cancelled", embed=None, view=None
            )

    @disnake.ui.button(label="Load", style=disnake.ButtonStyle.blurple)
    async def load_backup(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        embed = disnake.Embed(
            color=self.settings_db.get_embed_color(interaction.guild.id)
        )

        confirm_embed = disnake.Embed(
            title="Confirmation",
            description="Are you sure you want to **load** server backup?",
            color=self.settings_db.get_embed_color(interaction.guild.id),
        )
        response = await self.confirm(interaction=interaction, embed=confirm_embed)
        if response == ConfirmEnum.OK:
            data = await self.backups.get(interaction.guild.id, to_return="backup_data")

            if not data:
                embed.title = "An error occurred"
                embed.description = (
                    "There is no backup in database. "
                    "If you have a backup file, please send it now. (You have one minute)"
                )
                await interaction.edit_original_response(embed=embed, view=None)
                try:
                    message: Optional[disnake.Message] = await self.bot.wait_for(
                        "message",
                        check=lambda m: m.author == interaction.author
                        and m.channel.id == interaction.channel_id
                        and m.attachments,
                        timeout=None,
                    )
                    if message.attachments:
                        data = await save_file_to_memory(
                            message.attachments[0], to_dict=True
                        )
                        await message.delete()
                except asyncio.TimeoutError:
                    await interaction.send(content="timeout.", ephemeral=True)

            embed.title = "<a:loading:1168599537682755584> Loading Backup"
            embed.description = None
            embed.set_footer(
                text=interaction.author, icon_url=interaction.author.avatar
            )

            try:
                await interaction.response.defer()
            except disnake.errors.InteractionResponded:
                pass

            await interaction.edit_original_response(embed=embed)

            await BackupGuild(interaction.guild).restore(data=data, message=interaction)
        else:
            await interaction.followup.send(
                content="OK. Operation cancelled", embed=None, ephemeral=True
            )
            await interaction.edit_original_message(
                content="Operation cancelled", embed=None, view=None
            )

    @disnake.ui.button(label="Delete", style=disnake.ButtonStyle.red)
    async def delete_backup(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        if not await self.backups.get(interaction.guild.id, to_return="backup_data"):
            embed = disnake.Embed(
                title="An error occurred",
                description="There is no backup for this server",
                color=self.settings_db.get_embed_color(interaction.guild.id),
            )
            await interaction.send(embed=embed)
            return

        embed = disnake.Embed(
            title="Confirmation",
            description="Are you sure you want to **delete** the current server backup?",
            color=self.settings_db.get_embed_color(interaction.guild.id),
        )
        response = await self.confirm(interaction=interaction, embed=embed)
        if response == ConfirmEnum.OK:
            await self.backups.delete_backup(interaction.guild.id)
            embed.title = "Success"
            embed.description = "Successfully deleted backup from the database"
            await interaction.edit_original_response(embed=embed, view=None)
        else:
            await interaction.followup.send(
                content="OK. Operation cancelled", embed=None
            )

    @disnake.ui.button(label="File", style=disnake.ButtonStyle.gray)
    async def backup_file(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        if backups.check_backup(interaction.guild):
            data = await self.backups.get(interaction.guild.id, to_return="backup_data")

            with io.StringIO() as temp_file:
                ujson.dump(data, temp_file, indent=4)
                temp_file.seek(0)
                file_data = temp_file.read().encode()
                await interaction.send(
                    file=disnake.File(fp=io.BytesIO(file_data), filename="backup.json"),
                    ephemeral=True,
                )
        else:
            embed = disnake.Embed(
                title="An error occurred",
                description="There isn't any backup created for this server",
                colour=0xF00707,
            )

            await interaction.send(embed=embed, ephemeral=True)


class Backup(commands.Cog):
    """Backup commands"""

    EMOJI = "<:category:1169684586666663999>"

    def __init__(self, bot: commands.Bot) -> None:
        super(Backup, self).__init__()
        self.bot = bot
        self.backups = backups
        self.settings_db = main_db
        self.commands_db = commands_db

    async def cog_load(self) -> None:
        await self.backups.fetch_and_cache_all()

    @commands.slash_command(name="backup", description="Backup system")  # TODO: locale
    @commands.has_permissions(administrator=True)
    async def backup(self, interaction: disnake.MessageCommandInteraction) -> None:
        embed = disnake.Embed(
            color=self.settings_db.get_embed_color(interaction.guild_id)
        )
        embed.title = "Backup system"
        embed.add_field(
            name="Information",
            value=f"<:pin:1169690524073087088> Using this panel you can save your server backup.\n"
            f"<:pin:1169690524073087088> Our system, is one of the most powerful backup system in discord.\n"
            f"<:pin:1169690524073087088> To **interact with backups** use emojis under this message.\n",
            inline=False,
        )

        if backups.check_backup(interaction.guild):
            data = await backups.get(guild_id=interaction.guild_id)
            if data and data.get("backup_data", None):
                data = data.get("backup_data", None)
                embed.add_field(
                    name="Last backup",
                    value=f"<t:{data['info']['created']}:f> (<t:{data['info']['created']}:R>)",
                    inline=False,
                )
        embed.set_footer(
            text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await interaction.send(embed=embed, view=BackupsView(self.bot), ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Backup(bot))
