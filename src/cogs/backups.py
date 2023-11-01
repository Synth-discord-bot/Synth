import io
import os

import disnake
import ujson
from disnake.ext import commands

from src.utils import backups
from src.utils.backup import Backup as BackupGuild
from src.utils.misc import is_owner, has_bot_permissions, save_file_to_memory


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
        if ctx.invoked_subcommand is None:
            embed = disnake.Embed(
                title="<:backup:1168599276520226826> Backup commands",
                color=0x2F3136,
                description=(
                    f"`{ctx.prefix}backup create` – Create/update backup\n"
                    f"`{ctx.prefix}backup delete` – Delete backup\n"
                    f"`{ctx.prefix}backup load` – Load backup\n"
                    f"`{ctx.prefix}backup file` – JSON file of server backup"
                ),
            )

            if backups.check_backup(ctx.guild):
                data = await backups.get(guild_id=ctx.guild.id)
                data = data["backup_data"]
                embed.add_field(
                    name="Last Backup:",
                    value=f"<t:{data['info']['created']}:f> (<t:{data['info']['created']}:R>)",
                )

            await ctx.send(embed=embed)

    @backup.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @is_owner()
    async def create(self, ctx: commands.Context) -> None:
        global msg
        embed = disnake.Embed(color=0x2F3136)
        try:
            embed.title = "<a:loading:1168599537682755584> Please wait..."
            embed.description = "Creating a server backup..."
            msg = await ctx.send(embed=embed)

            backup_data = await BackupGuild(ctx.guild).create()

            await self.backups.update_backups_info(ctx.guild.id, backup_data)

            embed.colour = 0x2F3136
            embed.title = "Finished"
            embed.description = "Server backup has been successfully created"

            with io.StringIO() as temp_file:
                ujson.dump(backup_data, temp_file, indent=4)
                temp_file.seek(0)
                await msg.edit(
                    embed=embed, file=disnake.File(fp=temp_file, filename="backup.json")
                )

        except (Exception, ExceptionGroup) as e:
            raise e
            embed.colour = 0x2F3136
            embed.title = "An error occurred"
            embed.description = "An error occurred when trying to save the server."
            await msg.edit(embed=embed)

    @backup.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @is_owner()
    @has_bot_permissions()
    async def load(self, ctx: commands.Context) -> None:
        embed = disnake.Embed(color=0x2F3136)
        if ctx.message.attachments:
            temp_file = await save_file_to_memory(ctx.message.attachments[0])
            data = ujson.load(temp_file)
        else:
            data = await self.backups.get(ctx.guild.id, to_return="backup_data")

            if not data:
                embed.title = "An error occurred"
                embed.description = "There is no backup for this server"
                await ctx.send(embed=embed)
                return

        embed.title = "<a:loading:1168599537682755584> Loading Backup"
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)

        msg = await ctx.send(embed=embed)

        await BackupGuild(ctx.guild).restore(data=data, message=msg)

    @backup.command()
    @commands.cooldown(1, 50, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def file(self, ctx: commands.Context) -> None:
        if backups.check_backup(ctx.guild):
            backup = {
                "guild": {},
                "text_channels": {},
                "voice_channels": {},
                "categories": {},
                "roles": {},
            }
            data = await self.backups.get(ctx.guild.id, to_return="backup_data")

            backup["guild"]["name"] = data["guild"]["name"]
            backup["guild"]["afk_timeout"] = data["guild"]["afk_timeout"]
            backup["guild"]["description"] = data["guild"]["description"]
            backup["text_channels"] = data["text"]
            backup["voice_channels"] = data["voice"]
            backup["categories"] = data["category"]
            backup["roles"] = data["roles"]

            with open(f"{str(ctx.guild.id)}.json", "w") as f:
                ujson.dump(backup, f, indent=4)

            await ctx.send(file=disnake.File(f"{str(ctx.guild.id)}.json"))
            os.remove(f"{str(ctx.guild.id)}.json")
        else:
            embed = disnake.Embed(
                colour=0x2F3136,
                title="An error occurred",
                description="There isn't any backup created for this server",
            )

            await ctx.send(embed=embed)

    @backup.command()
    @is_owner()
    async def delete(self, ctx: commands.Context) -> None:
        embed = disnake.Embed(color=0x2F3136)

        if backups.check_backup(ctx.guild):
            await self.backups.remove_from_db({"_id": ctx.guild.id})
            embed.title = "Finished"
            embed.description = "Server backup has been successfully deleted"
            await ctx.send(embed=embed)
        else:
            embed.title = "An error occurred"
            embed.description = "Server backup hasn't been deleted."
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)
            await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Backup(bot))
