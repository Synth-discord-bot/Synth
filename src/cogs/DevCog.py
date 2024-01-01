import disnake
from disnake.ext import commands
from traceback import format_exception
import contextlib
import io
import textwrap


class PanelView(disnake.ui.Select):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(
            placeholder="Choose an option",
            min_values=1,
            max_values=1,
            options=[
                disnake.SelectOption(
                    emoji="<:list:1169690529643114547>",
                    label="Eval",
                    description="Exec some code",
                    value="eval",
                ),
                disnake.SelectOption(
                    emoji="<:category:1169684586666663999>",
                    label="Load",
                    description="Load the cog",
                    value="load",
                ),
                disnake.SelectOption(
                    emoji="<:wrench:1169690509929889802>",
                    label="Unload",
                    description="Unload the cog",
                    value="unload",
                ),
                disnake.SelectOption(
                    emoji="<:store:1169690541986959464>",
                    label="Reload",
                    description="Reload the cog",
                    value="reload",
                ),
            ],
        )
        self.bot = bot

    def clean_code(self, content):
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:])[:-3]
        else:
            return content

    async def callback(self, interaction: disnake.Interaction) -> None:
        selected_option = interaction.values[0]
        if selected_option == "reload":
            modal = disnake.ui.Modal(
                title="Realod cog",
                custom_id="reaload_cog",
                components=[
                    disnake.ui.TextInput(
                        label="Enter the cog name you'd like to reload",
                        custom_id="reload_cog_input",
                        placeholder="cog... (withought .py)",
                    )
                ],
            )
            await interaction.response.send_modal(modal=modal)
            modal_response = await self.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == "reaload_cog"
                and i.user == interaction.user,
            )
            await modal_response.response.defer(ephemeral=True)
            try:
                embed=disnake.Embed(color=disnake.Color.green())
                embed.title="Reloaded cog successfully"
                embed.description=f"Reloaded {modal_response.text_values['reload_cog_input']} successfully."
                self.bot.reload_extension(f"src.cogs.{modal_response.text_values['reload_cog_input']}")
                await modal_response.followup.send(embed=embed, ephemeral=True)
            except BaseException as e:
                embed=disnake.Embed(color=disnake.Color.red())
                embed.title="Error while reloading cog"
                embed.description="Error:\n" + "\n".join(format_exception(e, e, e.__traceback__))
                await modal_response.followup.send(embed=embed, ephemeral=True)

        elif selected_option == "load":
            modal = disnake.ui.Modal(
                title="Load cog",
                custom_id="load_cog",
                components=[
                    disnake.ui.TextInput(
                        label="Enter the cog name you'd like to load",
                        custom_id="load_cog_input",
                        placeholder="cog... (withought .py)",
                    )
                ],
            )
            await interaction.response.send_modal(modal=modal)
            modal_response = await self.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == "load_cog"
                and i.user == interaction.user,
            )
            await modal_response.response.defer(ephemeral=True)
            try:
                embed=disnake.Embed(color=disnake.Color.green())
                embed.title="Loaded cog successfully"
                embed.description=f"Loaded {modal_response.text_values['load_cog_input']} successfully."
                self.bot.load_extension(f"src.cogs.{modal_response.text_values['load_cog_input']}")
                await modal_response.followup.send(embed=embed, ephemeral=True)
            except BaseException as e:
                embed=disnake.Embed(color=disnake.Color.red())
                embed.title="Error while loading cog"
                embed.description="Error:\n" + "\n".join(format_exception(e, e, e.__traceback__))
                await modal_response.followup.send(embed=embed, ephemeral=True)

        elif selected_option == "unload":
            modal = disnake.ui.Modal(
                title="Unload cog",
                custom_id="unload_cog",
                components=[
                    disnake.ui.TextInput(
                        label="Enter the cog name you'd like to unload",
                        custom_id="unload_cog_input",
                        placeholder="cog... (withought .py)",
                    )
                ],
            )
            await interaction.response.send_modal(modal=modal)
            modal_response = await self.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == "unload_cog"
                and i.user == interaction.user,
            )
            await modal_response.response.defer(ephemeral=True)
            try:
                embed=disnake.Embed(color=disnake.Color.green())
                embed.title="Unloaded cog successfully"
                embed.description=f"Unloaded {modal_response.text_values['unload_cog_input']} successfully."
                self.bot.unload_extension(f"src.cogs.{modal_response.text_values['unload_cog_input']}")
                await modal_response.followup.send(embed=embed, ephemeral=True)
            except BaseException as e:
                embed=disnake.Embed(color=disnake.Color.red())
                embed.title="Error while unloading cog"
                embed.description="Error:\n" + "\n".join(format_exception(e, e, e.__traceback__))
                await modal_response.followup.send(embed=embed, ephemeral=True)

        elif selected_option == "eval":
            modal = disnake.ui.Modal(
                title="Write the code",
                custom_id="code",
                components=[
                    disnake.ui.TextInput(
                        label="Code:",
                        custom_id="code_input",
                        placeholder="Code",
                        style=disnake.TextInputStyle.long
                    )
                ]
            )
            await interaction.response.send_modal(modal=modal)
            modal_response = await self.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == "code"
                and i.user == interaction.user,
            )

            await modal_response.response.defer(ephemeral=True)
            pending_embed = disnake.Embed(description='Code is processing...', color=disnake.Colour.from_rgb(255, 255, 0))
            message = await modal_response.followup.send(embed=pending_embed, ephemeral=True)

            success_embed = disnake.Embed(title='Code processing - success', color=disnake.Colour.from_rgb(0, 255, 0))

            code = self.clean_code(modal_response.text_values['code_input'])
            local_variables = {
                "disnake": disnake,
                "commands": commands,
                "client": self.bot,
                "bot": self.bot,
                "ctx": commands.Context,
                "interaction": interaction,
                "channel": interaction.channel,
                "author": interaction.user,
                "guild": interaction.guild
            }

            stdout = io.StringIO()

            try:
                with contextlib.redirect_stdout(stdout):
                    exec(f"async def func():\n{textwrap.indent(code, '    ')}", local_variables)
                    obj = await local_variables["func"]()
                    result = stdout.getvalue()

                    success_embed.add_field(name='Processed code:', value=f'```py\n{code}\n```', inline=False)

                    if obj is not None:
                        data_type = type(obj).__name__
                        success_embed.add_field(name='Data type:', value=f'```\n{data_type}\n```', inline=False)
                        success_embed.add_field(name='Returned:', value=f'```\n{obj}\n```', inline=False)

                    if result:
                        success_embed.add_field(name='Result:', value=f'```py\nConsole:\n\n{result}\n```', inline=False)

                    await message.edit(embed=success_embed)

            except Exception as e:
                result = "".join(format_exception(e, e, e.__traceback__))
                fail_embed = disnake.Embed(title='Code processing - failed', color=disnake.Colour.from_rgb(255, 0, 0))
                fail_embed.add_field(name='Processed code:', value=f'```py\n{code}\n```', inline=False)
                fail_embed.add_field(name='Error:', value=f'```py\n{e}\n```', inline=False)
                await message.edit(embed=fail_embed)

class Developers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super(Developers, self).__init__()
        self.bot = bot

    # TODO: BLACKLIST SETTINGS

    @commands.slash_command(name="panel", description="Panel menu", guild_ids=[1109511263509291098])
    @commands.is_owner()
    async def panel_menu(self, interaction):
        embed=disnake.Embed(color=disnake.Color.blurple())
        embed.title="Control panel for Synth"
        embed.description="Via select menu, you can control the bot cogs and exec some code."
        embed.set_footer(
            text="Synth © 2023 | All Rights Reserved", 
            icon_url=self.bot.user.avatar
        )
        await interaction.send(
            embed=embed, 
            ephemeral=True, 
            view=disnake.ui.View().add_item(PanelView(self.bot))
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Developers(bot))
