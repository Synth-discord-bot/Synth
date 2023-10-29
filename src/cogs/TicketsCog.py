import disnake
from disnake.ext import commands
from src.utils import ticket


class SetupTicketSettings(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(
        label="Title",
        custom_id="title_ticket_settings",
        emoji="🗒️",
        style=disnake.ButtonStyle.gray,
    )
    async def title_ticket(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Title",
            custom_id="title_modal",
            components=[
                disnake.ui.TextInput(
                    label="Enter title:",
                    custom_id="title_textinput",
                    style=disnake.TextInputStyle.short,
                    placeholder="Example: New Ticket",
                )
            ],
        )

    @disnake.ui.button(
        label="Description",
        custom_id="desc_ticket_settings",
        emoji="🗒️",
        style=disnake.ButtonStyle.gray,
    )
    async def description_ticket(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_modal(
            title="Description",
            custom_id="desc_modal",
            components=[
                disnake.ui.TextInput(
                    label="Enter description:",
                    custom_id="desc_textinput",
                    style=disnake.TextInputStyle.short,
                    placeholder="Example: If u have pro...",
                )
            ],
        )

    @disnake.ui.button(
        label="Select or button",  # переделать 100%
        custom_id="selector_ticket_settings",
        emoji="🗒️",
        style=disnake.ButtonStyle.gray,
    )
    async def selector_ticket(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.send(
            "Soon", ephemeral=True
        )  # Button/Select (отдельным сообщением мб?)


class Ticket(commands.Cog):
    """Helper commands to setup ticket system"""

    EMOJI = "🎫"

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.ticket_db = ticket

    async def cog_load(self) -> None:
        await self.ticket_db.fetch_and_cache_all()

    @commands.slash_command(name="setup", description="Setup Tickets")
    async def ticket_setup(
        self, interaction: disnake.MessageCommandInteraction
    ) -> None:
        await interaction.send("Ticket Setup", view=SetupTicketSettings())

    @commands.Cog.listener()
    async def on_modal_submit(self, interaction: disnake.ModalInteraction):
        print(interaction.__dir__())
        if interaction.custom_id == "title_modal":
            title = interaction.text_values.get("title_textinput", "")
            await interaction.send(f"New title: `{title}`")
        elif interaction.custom_id == "desc_modal":
            desc = interaction.text_values.get("desc_textinput", "")
            await interaction.send(f"New description: `{desc}`")


def setup(bot):
    bot.add_cog(Ticket(bot))
