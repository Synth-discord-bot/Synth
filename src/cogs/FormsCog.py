import disnake
from disnake.ext import commands

from src.utils import forms, FormsDatabase


# class ConfigureModal(disnake.ui.Modal):
#     def __init__(
#             self,
#             bot: commands.Bot,
#             embed_part: str,
#             required: bool = True,
#             placeholder: str = None,
#     ):
#         self.bot = bot
#         self.embed_part = embed_part
#         self.required = required
#         self.placeholder = placeholder
#         self.value = None
#
#         super().__init__(
#             title=f"Enter the new form {embed_part}",
#             components=[
#                 disnake.ui.TextInput(
#                     label=f"Form {embed_part}",
#                     custom_id=f"{embed_part}",
#                     placeholder=placeholder if placeholder else f"Enter the new form {embed_part}",
#                     required=required,
#                 ),
#             ],
#         )
#
#     async def callback(self, inter: disnake.ModalInteraction):
#         self.value = inter.text_values.get(self.embed_part)
#         await inter.response.edit_message(content=f"You entered {self.value}")
#         return self.value


class SelectFormChannel(disnake.ui.ChannelSelect):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.value = None

        # Convert the channel_types parameter to a list of ChannelType objects
        channel_types = [disnake.ChannelType.text]
        super().__init__(
            placeholder="Select channel to send the form",
            channel_types=channel_types,
            custom_id="form_channel",
        )


class ConfigureForm(disnake.ui.Select):
    def __init__(self, bot: commands.Bot, forms_db: FormsDatabase) -> None:
        super().__init__(
            placeholder="Choose an option",
            min_values=1,
            max_values=1,
            options=[
                disnake.SelectOption(
                    label="Title",
                    description="Configure the form title",
                    value="embed_title",
                ),
                disnake.SelectOption(
                    label="Description",
                    description="Configure the from description",
                    value="embed_description",
                ),
            ],
        )
        self.bot = bot
        self.forms = forms_db
        self.new_title = None
        self.new_description = None

    async def callback(self, interaction: disnake.Interaction) -> None:
        selected_option = interaction.values[0]
        if selected_option == "embed_title":
            modal = disnake.ui.Modal(
                title="Write new embed title",
                custom_id="embed_title",
                components=[
                    disnake.ui.TextInput(
                        label="New form title:",
                        custom_id="new_embed_title",
                        placeholder="Title",
                    )
                ],
            )
            await interaction.response.send_modal(modal=modal)
            modal_response = await self.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == "embed_title"
                and i.user == interaction.user,
            )
            await modal_response.response.send_message(
                f"New form title is `{modal_response.text_values['new_embed_title']}`",
                ephemeral=True,
            )  # type: ignore
            self.new_title = modal_response.text_values["new_embed_title"]

        elif selected_option == "embed_description":
            modal = disnake.ui.Modal(
                title="Write new embed description",
                custom_id="embed_description",
                components=[
                    disnake.ui.TextInput(
                        label="New form description:",
                        custom_id="new_embed_description",
                        style=disnake.TextInputStyle.long,
                        placeholder="Description",
                    )
                ],
            )
            await interaction.response.send_modal(modal=modal)
            modal_response = await self.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == "embed_description"
                and i.user == interaction.user,
            )
            await modal_response.response.send_message(
                f"New form description is `{modal_response.text_values['new_embed_description']}`",
                ephemeral=True,
            )  # type: ignore
            self.new_description = modal_response.text_values["new_embed_description"]
            print(self.new_description)

        if self.new_title and self.new_description:  # type: ignore
            view = disnake.ui.View()
            select_form_channel = SelectFormChannel(self.bot)
            view.add_item(select_form_channel)
            await interaction.send("Select a channel:", view=view)

            channel = await self.bot.wait_for(
                "dropdown",
                check=lambda x: x.data.custom_id == "form_channel"
                and x.author == interaction.author
                and x.data.values,
            )
            
            
            await self.forms.update_form_info(
                guild_id=interaction.guild.id,
                form_name=self.new_title,
                form_description=self.new_description,
                form_channel_id=channel.id,
            )

            embed = disnake.Embed(
                title=self.new_title,
                description=self.new_description,
                color=0x2F3136,
            )
            await channel.send(embed=embed)


class FormsView(disnake.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @disnake.ui.button(label="Create", style=disnake.ButtonStyle.green)
    async def create_form(
        self, _: disnake.ui.Button, __: disnake.Interaction, ___: str
    ) -> None:
        form_embed = disnake.Embed(
            title="Creating Form",
            colour=0x2F3136,
            description="To create a form, please choose one of the options below:",
        )

        # modal = disnake.ui.Modal(
        #     title="Form",
        #     components=[disnake.ui.TextInput(custom_id="form_name", label="")],
        # )

    @disnake.ui.button(label="Edit", style=disnake.ButtonStyle.gray)
    async def edit_form(
        self, _: disnake.ui.Button, interaction: disnake.Interaction
    ) -> None:
        await interaction.send(
            "Form has been edited", ephemeral=True, view=FormsView(self.bot)
        )

    @disnake.ui.button(label="Delete", style=disnake.ButtonStyle.red)
    async def delete_form(
        self, _: disnake.ui.Button, interaction: disnake.Interaction
    ) -> None:
        await interaction.send(
            "Form has been deleted", ephemeral=True, view=FormsView(self.bot)
        )


class EditFormView(disnake.ui.View):
    def __init__(self, bot: commands.Bot, forms_db: FormsDatabase) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.forms = forms_db

    @disnake.ui.button(
        label="Title", custom_id="title_button", style=disnake.ButtonStyle.gray
    )
    async def title_button(
        self, _: disnake.ui.Button, interaction: disnake.MessageCommandInteraction
    ) -> None:
        await interaction.send("Write new title:")
        msg = await self.bot.wait_for(
            "message", check=lambda x: x.author == interaction.author, timeout=15
        )
        title = msg.content
        await msg.delete()
        await interaction.channel.send(f"New title: `{title}`", delete_after=10)


class Forms(commands.Cog):
    """Helper commands to setup forms."""

    EMOJI = "<:store:1169690541986959464>"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.forms = forms

    async def cog_load(self) -> None:
        await self.forms.fetch_and_cache_all()

    @commands.slash_command()
    async def form(self, _) -> None:
        pass

    @form.sub_command(description="Create a form (customizable embed message)")
    async def create(self, interaction: disnake.MessageCommandInteraction) -> None:
        setup_form_embed = disnake.Embed(title="Title", description="Description")
        select = disnake.ui.View()
        select.add_item(ConfigureForm(self.bot, forms_db=self.forms))

        await interaction.send(
            f"Create a form. Please choose one of the options below. Setup form:",
            view=select,
            embed=setup_form_embed,
        )


    @form.sub_command()
    async def edit(self, interaction: disnake.MessageCommandInteraction) -> None:
        await interaction.send("Edit", ephemeral=True, view=FormsView(self.bot))

    @form.sub_command()
    async def delete(
        self, interaction: disnake.MessageCommandInteraction, name: str
    ) -> None:
        await interaction.send(
            f"Nigga `{name}`", ephemeral=True, view=FormsView(self.bot)
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Forms(bot=bot))
