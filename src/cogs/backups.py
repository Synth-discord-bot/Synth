import io
import os
from typing import Optional

import disnake
import ujson
from disnake.ext import commands

from src.utils import backups
from src.utils.backup import Backup as BackupGuild
from src.utils.misc import save_file_to_memory


# class Confirmation(disnake.ui.View):
#     def __init__(self) -> None:
#         super().__init__(timeout=60.0)
#         self.backups = backups
#
#     @disnake.ui.button(label="Yes", custom_id="confirm_yes", style=disnake.ButtonStyle.green)
#     async def confirm_yes(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction):
#         backup_data = await BackupGuild(interaction.guild).create()
#
#         await self.backups.update_backups_info(interaction.guild.id, backup_data)
#
#         embed = disnake.Embed(color=0x2F3136)
#         embed.title = "Finished"
#         embed.description = f"Server backup has been successfully created"
#
#         with io.StringIO() as temp_file:
#             ujson.dump(backup_data, temp_file, indent=4)
#             temp_file.seek(0)
#             file_data = temp_file.read().encode()
#             await interaction.edit_original_message(
#                 embed=embed, file=disnake.File(fp=io.BytesIO(file_data), filename="backup.json")
#             )
#
#     @disnake.ui.button(label="No", custom_id="confirm_no", style=disnake.ButtonStyle.red)
#     async def confirm_no(self, _: disnake.ui.Button, interaction: disnake.MessageInteraction):
#         return await interaction.edit_original_response(content="????")
#
#     #так нам це для лоад теж треба, ы для деліта, ати лиш для кріейт робиш

class BackupsView(disnake.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.backups = backups

    async def confirm(self, interaction: disnake.InteractionMessage, embed: disnake.Embed = None) -> Optional[str]:
        buttons = [
            disnake.ui.Button(
                label="Yes",
                custom_id="confirm_yes",
                style=disnake.ButtonStyle.green,
            ),
            disnake.ui.Button(
                label="No",
                custom_id="confirm_no",
                style=disnake.ButtonStyle.red
            )
        ]

        if not embed:
            embed = disnake.Embed(
                title="Confirmation",
                description="Are you sure?",
                color=0x2F3136
            )

        await interaction.send(embed=embed, ephemeral=True, components=buttons)

        interaction = await self.bot.wait_for(
            "button_click",
            check=lambda i:
            i.author == interaction.author and
            i.id == interaction.id,
            timeout=60.0
        )
        return interaction.data.custom_id or None

    @disnake.ui.button(label="Save", style=disnake.ButtonStyle.green)
    async def create_backup(
            self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        embed = disnake.Embed(color=0x2F3136)
        try:
            embed.title = "<a:loading:1168599537682755584> Please wait..."
            embed.description = "Creating a server backup..."
            await interaction.send(embed=embed, ephemeral=True)

            backup_data = await BackupGuild(interaction.guild).create()

            await self.backups.update_backups_info(interaction.guild.id, backup_data)

            embed.title = "Finished"
            embed.description = f"Server backup has been successfully created"

            with io.StringIO() as temp_file:
                ujson.dump(backup_data, temp_file, indent=4)
                temp_file.seek(0)
                file_data = temp_file.read().encode()
                await interaction.edit_original_message(
                    embed=embed, file=disnake.File(fp=io.BytesIO(file_data), filename="backup.json")
                )

        except (Exception, ExceptionGroup) as e:
            embed.title = "An error occurred"
            embed.description = "An error occurred when trying to save the server."
            await interaction.edit_original_message(embed=embed)
            raise e

    @disnake.ui.button(label="Load", style=disnake.ButtonStyle.blurple)
    async def load_backup(
            self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        embed = disnake.Embed(color=0x2F3136)
        if interaction.message.attachments:
            temp_file = await save_file_to_memory(interaction.message.attachments[0])
            data = ujson.load(temp_file)
        else:
            data = await self.backups.get(interaction.guild.id, to_return="backup_data")

            if not data:
                embed.title = "An error occurred"
                embed.description = "There is no backup for this server"
                await interaction.send(embed=embed)
                return

        embed.title = "<a:loading:1168599537682755584> Loading Backup"
        embed.set_footer(text=interaction.author, icon_url=interaction.author.avatar)

        await interaction.send(embed=embed)

        await BackupGuild(interaction.guild).restore(data=data, message=interaction.message)

    @disnake.ui.button(label="Delete", style=disnake.ButtonStyle.red)
    async def delete_backup(
            self, _: disnake.ui.Button, interaction: disnake.InteractionMessage
    ) -> None:

        ConfirmEmbed = disnake.Embed(
            title="Confirmation",
            description="Are you sure you want to **delete** the current server backup?",
            color=0x2F3136
        )
        print(await self.confirm(interaction=interaction, embed=ConfirmEmbed))
        if await self.confirm(interaction=interaction, embed=ConfirmEmbed) == "confirm_yes":
            await interaction.send("yes")
        else:
            await interaction.send("no")

    @disnake.ui.button(label="File", style=disnake.ButtonStyle.gray)
    async def backup_file(
            self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        if backups.check_backup(interaction.guild):
            backup = {
                "guild": {},
                "text_channels": {},
                "voice_channels": {},
                "categories": {},
                "roles": {},
            }
            data = await self.backups.get(interaction.guild.id, to_return="backup_data")

            backup["guild"]["name"] = data["guild"]["name"]
            backup["guild"]["afk_timeout"] = data["guild"]["afk_timeout"]
            backup["guild"]["description"] = data["guild"]["description"]
            backup["text_channels"] = data["text"]
            backup["voice_channels"] = data["voice"]
            backup["categories"] = data["category"]
            backup["roles"] = data["roles"]

            with open(f"{str(interaction.guild.name)}.json", "w") as f:
                ujson.dump(backup, f, indent=4)

            await interaction.send(file=disnake.File(f"{str(interaction.guild.name)}.json"), ephemeral=True)
            os.remove(f"{str(interaction.guild.name)}.json")
        else:
            embed = disnake.Embed(
                title="An error occurred",
                description="There isn't any backup created for this server",
                colour=0xF00707
            )

            await interaction.send(embed=embed, ephemeral=True)


class Backup(commands.Cog):
    """Backup commands"""

    EMOJI = "📅"

    def __init__(self, bot: commands.Bot) -> None:
        super(Backup, self).__init__()
        self.bot = bot
        self.backups = backups

    async def cog_load(self) -> None:
        await self.backups.fetch_and_cache_all()

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def backup(self, ctx: commands.Context) -> None:
        # if ctx.invoked_subcommand is None:
        #     embed = disnake.Embed(
        #         title="<:backup:1168599276520226826> Backup commands",
        #         color=0x2F3136,
        #         description=(
        #             f"`{ctx.prefix}backup create` – Create/update backup\n"
        #             f"`{ctx.prefix}backup delete` – Delete backup\n"
        #             f"`{ctx.prefix}backup load` – Load backup\n"
        #             f"`{ctx.prefix}backup file` – JSON file of server backup"
        #         ),
        #     )
        #
        #     if backups.check_backup(ctx.guild):
        #         data = await backups.get(guild_id=ctx.guild.id)
        #         data = data["backup_data"]
        #         embed.add_field(
        #             name="Last Backup:",
        #             value=f"<t:{data['info']['created']}:f> (<t:{data['info']['created']}:R>)",
        #         )
        #
        #     await ctx.send(embed=embed)
        embed = disnake.Embed(color=0x2F3136)
        embed.title = "Backup system"
        embed.add_field(
            name="Information",
            value=f"<:pin:1169690524073087088> Using this panel you can save your server backup.\n"
                  f"<:pin:1169690524073087088> Our system, is one of the most powerful backup system in discord.\n"
                  f"<:pin:1169690524073087088> To **interact with backups** use emojis under this message.\n",
            inline=False
        )

        if backups.check_backup(ctx.guild):
            data = await backups.get(guild_id=ctx.guild.id)
            data = data["backup_data"]
            embed.add_field(name="Last backup",
                            value=f"<t:{data['info']['created']}:f> (<t:{data['info']['created']}:R>)", inline=False)
        embed.set_footer(
            text="Synth © 2023 | All Rights Reserved", icon_url=self.bot.user.avatar
        )
        await ctx.send(embed=embed, view=BackupsView(self.bot))

    # @backup.command()
    # @commands.cooldown(1, 5, commands.BucketType.guild)
    # @is_owner()
    # async def create(self, ctx: commands.Context) -> None:
    #     global msg
    #     embed = disnake.Embed(color=0x2F3136)
    #     try:
    #         embed.title = "<a:loading:1168599537682755584> Please wait..."
    #         embed.description = "Creating a server backup..."
    #         msg = await ctx.send(embed=embed)
    #
    #         backup_data = await BackupGuild(ctx.guild).create()
    #
    #         await self.backups.update_backups_info(ctx.guild.id, backup_data)
    #
    #         embed.colour = 0x2F3136
    #         embed.title = "Finished"
    #         embed.description = "Server backup has been successfully created"
    #
    #         with io.StringIO() as temp_file:
    #             ujson.dump(backup_data, temp_file, indent=4)
    #             temp_file.seek(0)
    #             file_data = temp_file.read().encode()
    #             await msg.edit(
    #                 embed=embed, file=disnake.File(fp=io.BytesIO(file_data), filename="backup.json")
    #             )
    #
    #     except (Exception, ExceptionGroup) as e:
    #         embed.colour = 0x2F3136
    #         embed.title = "An error occurred"
    #         embed.description = "An error occurred when trying to save the server."
    #         await msg.edit(embed=embed)
    #         raise e
    #
    # @backup.command()
    # @commands.cooldown(1, 5, commands.BucketType.guild)
    # @is_owner()
    # @has_bot_permissions()
    # async def load(self, ctx: commands.Context) -> None:
    #     embed = disnake.Embed(color=0x2F3136)
    #     if ctx.message.attachments:
    #         temp_file = await save_file_to_memory(ctx.message.attachments[0])
    #         data = ujson.load(temp_file)
    #     else:
    #         data = await self.backups.get(ctx.guild.id, to_return="backup_data")
    #
    #         if not data:
    #             embed.title = "An error occurred"
    #             embed.description = "There is no backup for this server"
    #             await ctx.send(embed=embed)
    #             return
    #
    #     embed.title = "<a:loading:1168599537682755584> Loading Backup"
    #     embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)
    #
    #     msg = await ctx.send(embed=embed)
    #
    #     await BackupGuild(ctx.guild).restore(data=data, message=msg)
    #
    # @backup.command()
    # @commands.cooldown(1, 50, commands.BucketType.guild)
    # @commands.has_permissions(administrator=True)
    # async def file(self, ctx: commands.Context) -> None:
    #     if backups.check_backup(ctx.guild):
    #         backup = {
    #             "guild": {},
    #             "text_channels": {},
    #             "voice_channels": {},
    #             "categories": {},
    #             "roles": {},
    #         }
    #         data = await self.backups.get(ctx.guild.id, to_return="backup_data")
    #
    #         backup["guild"]["name"] = data["guild"]["name"]
    #         backup["guild"]["afk_timeout"] = data["guild"]["afk_timeout"]
    #         backup["guild"]["description"] = data["guild"]["description"]
    #         backup["text_channels"] = data["text"]
    #         backup["voice_channels"] = data["voice"]
    #         backup["categories"] = data["category"]
    #         backup["roles"] = data["roles"]
    #
    #         with open(f"{str(ctx.guild.id)}.json", "w") as f:
    #             ujson.dump(backup, f, indent=4)
    #
    #         await ctx.send(file=disnake.File(f"{str(ctx.guild.id)}.json"))
    #         os.remove(f"{str(ctx.guild.id)}.json")
    #     else:
    #         embed = disnake.Embed(
    #             colour=0x2F3136,
    #             title="An error occurred",
    #             description="There isn't any backup created for this server",
    #         )
    #
    #         await ctx.send(embed=embed)
    #
    # @backup.command()
    # @is_owner()
    # async def delete(self, ctx: commands.Context) -> None:
    #     embed = disnake.Embed(color=0x2F3136)
    #
    #     if backups.check_backup(ctx.guild):
    #         await self.backups.remove_from_db({"_id": ctx.guild.id})
    #         embed.title = "Finished"
    #         embed.description = "Server backup has been successfully deleted"
    #         await ctx.send(embed=embed)
    #     else:
    #         embed.title = "An error occurred"
    #         embed.description = "Server backup hasn't been deleted."
    #         embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)
    #         await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Backup(bot))
