from disnake.ext import commands
from disnake.ext.commands import TextChannelConverter, BadArgument
import disnake
from src.utils import forms


class ButtonOrSelect(disnake.ui.Select):
    def __init__(self, bot: commands.Bot, forms: forms):
        super().__init__(
            placeholder="Choose a category",
            min_values=1,
            max_values=1,
            options=[
                disnake.SelectOption(
                    emoji="<:dot:1168250169146482839>",
                    label="Dropdown",
                    description="Dropdown form customization",
                    value="dropdown",
                ),
                disnake.SelectOption(
                    emoji="<:dot:1168250169146482839>",
                    label="Buttons",
                    description="Buttons form customization",
                    value="buttons",
                ),
            ],
        )
        self.bot = bot
        self.forms = forms

    async def callback(self, interaction: disnake.MessageInteraction) -> None:
        form_type = None
        if interaction.values[0] == "buttons":
            form_type = "button"
        if interaction.values[0] == "dropdown":
            form_type = "dropdown"

        # title
        await interaction.send("Write new title:", delete_after=15)
        msg = await self.bot.wait_for(
            "message", check=lambda x: x.author == interaction.author, timeout=15
        )
        name = msg.content
        await msg.delete()

        # description
        await interaction.channel.send(
            f"New title: `{name}`.\n\nWrite new description:"
        )
        msg = await self.bot.wait_for(
            "message", check=lambda x: x.author == interaction.author, timeout=None
        )
        description = msg.content
        await msg.delete()

        # channel
        await interaction.channel.send(
            f"New title: `{name}`\n\nNew description: `{msg.content}`. Write id or mention of channel:",
            delete_after=30,
        )
        msg = await self.bot.wait_for(
            "message", check=lambda x: x.author == interaction.author, timeout=None
        )
        channel_id = msg.content
        await msg.delete()
        msg = await interaction.channel.send("Checking channel..")

        # convert string to channel
        try:
            channel = await TextChannelConverter().convert(
                ctx=interaction, argument=channel_id
            )
        except BadArgument:
            await msg.edit("This channel does not exist.", delete_after=10)

        try:
            await channel.send(".", delete_after=0.05)
            channel_id = channel.id
        except (disnake.HTTPException, disnake.Forbidden):
            await msg.edit("This channel does not have permissions to send messages.")

        await self.forms.update_form_info(
            guild_id=interaction.guild.id,
            form_name=name,
            form_description=description,
            form_channel_id=channel_id,
            form_type=form_type,
        )

        await msg.edit("Form has been created", delete_after=10)


class FormsView(disnake.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @disnake.ui.button(label="Create", style=disnake.ButtonStyle.green)
    async def create_form(
        self, _: disnake.ui.Button, interaction: disnake.Interaction, name: str
    ) -> None:
        FormEmbed = disnake.Embed(colour=0x43ADF3)
        FormEmbed.title = "Creating Form"
        FormEmbed.description = (
            "To create a form, please choose one of the options below:"
        )

        modal = disnake.ui.Modal(
            title="Form",
            components=[disnake.ui.TextInput(custom_id="form_name", label="")],
        )

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
    def __init__(self, bot: commands.Bot, forms: forms):
        super().__init__(timeout=None)
        self.bot = bot
        self.forms = forms

    @disnake.ui.button(
        label="Title", custom_id="title_button", style=disnake.ButtonStyle.gray
    )
    async def title_button(self, _: disnake.ui.Button, interaction):
        await interaction.send("Write new title:")
        msg = await self.bot.wait_for(
            "message", check=lambda x: x.author == interaction.author, timeout=15
        )
        title = msg.content
        await msg.delete()
        await interaction.channel.send(f"New title: `{title}`", delete_after=10)


class FormsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.forms = forms

    async def cog_load(self) -> None:
        await self.forms.fetch_and_cache_all()

    @commands.slash_command()
    async def form(self, _) -> None:
        pass

    @form.sub_command()
    async def create(
        self, interaction: disnake.MessageCommandInteraction, name: str
    ) -> None:
        setup_form_embed = disnake.Embed(title="Title", description="Description")
        button_or_select = disnake.ui.Button(
            label="Button/Select", style=disnake.ButtonStyle.gray, disabled=True
        )

        select = disnake.ui.View()
        select.add_item(ButtonOrSelect(self.bot, forms=self.forms))

        await interaction.send(
            f"Create a {name} form. Please choose one of the options below. Setup form:",
            view=select,
        )
        await interaction.channel.send(
            embed=setup_form_embed, components=[button_or_select]
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
    bot.add_cog(FormsCog(bot=bot))
