from typing import Optional

import disnake
from disnake.ext import commands
from disnake.interactions import MessageInteraction

from src.utils import main_db, commands_db


class LanguageSettings(disnake.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.settings_db = main_db
        self.commands_db = commands_db

    @disnake.ui.string_select(
        cls=disnake.ui.StringSelect,  # type: ignore
        options=[
            disnake.SelectOption(label="Russian", value="russian_language", emoji="🇷🇺"),
            disnake.SelectOption(label="English", value="english_language", emoji="🇬🇧"),
            disnake.SelectOption(
                label="Ukrainian", value="ukrainian_language", emoji="🇺🇦"
            ),
            disnake.SelectOption(label="German", value="german_language", emoji="🇩🇪"),
        ],
        placeholder="Choice a language for bot",
    )
    async def callback(
        self, _: disnake.ui.StringSelect, interaction: disnake.MessageInteraction
    ):
        if _.values[0] == "russian_language":
            await interaction.response.send_message(
                "Вы выбрали Русский язык", ephemeral=True
            )
        elif _.values[0] == "english_language":
            await interaction.response.send_message(
                "You selected English", ephemeral=True
            )
        elif _.values[0] == "ukrainian_language":
            await interaction.response.send_message(
                "Ви обрали Українську мову", ephemeral=True
            )
        elif _.values[0] == "german_language":
            await interaction.response.send_message(
                "Du hast Deutsch ausgewaehlt", ephemeral=True
            )


class PrefixSettings(disnake.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.settings_db = main_db
        self.commands_db = commands_db

    @disnake.ui.button(
        label="Change",
        custom_id="prefix_button",
        style=disnake.ButtonStyle.green,
    )
    async def callback(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        modal = disnake.ui.Modal(
            title="Write new prefix",
            custom_id="prefix",
            components=[
                disnake.ui.TextInput(
                    label="New prefix:",
                    custom_id="new_prefix",
                    style=disnake.TextInputStyle.short,
                    max_length=3,
                    min_length=1,
                )
            ],
        )
        await interaction.response.send_modal(modal=modal)
        response_modal = await self.bot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == "prefix" and i.user == interaction.user,
        )
        await self.settings_db.set_prefix(
            interaction.guild.id, response_modal.text_values["new_prefix"]
        )
        await response_modal.response.send_message(
            f"New prefix is `{response_modal.text_values['new_prefix']}`",
            ephemeral=True,
        )


class EmbedColorSettings(disnake.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.settings_db = main_db
        self.commands_db = commands_db

    @disnake.ui.button(
        label="Change",
        custom_id="embed_color_button",
        style=disnake.ButtonStyle.green,
    )
    async def callback(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        modal = disnake.ui.Modal(
            title="Write new embed color",
            custom_id="embed_color",
            components=[
                disnake.ui.TextInput(
                    label="New embed color (hex):",
                    custom_id="new_embed_color",
                    style=disnake.TextInputStyle.short,
                    max_length=8,
                    min_length=8,
                    placeholder="0x2F3236",
                )
            ],
        )
        await interaction.response.send_modal(modal=modal)
        modal_response = await self.bot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == "embed_color" and i.user == interaction.user,
        )
        if not modal_response.text_values["new_embed_color"].startswith("0x"):
            return await modal_response.response.send_message(
                "Embed color must start with `0x`", ephemeral=True
            )
        await self.settings_db.add_embed_color(
            interaction.guild.id, modal_response.text_values["new_embed_color"]
        )
        await modal_response.response.send_message(
            f"New embed color is `{modal_response.text_values['new_embed_color']}`",
            ephemeral=True,
        )  # type: ignore


class CommandsSlashCommands(disnake.ui.StringSelect):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.settings_db = main_db
        self.commands_db = commands_db

    async def callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        is_disabled = await self.settings_db.check_command(
            inter.guild_id, command=inter.values[0], add_if_not_exists=False
        )

        if is_disabled:
            await self.settings_db.delete_command(inter.guild_id, inter.values[0])
            await inter.edit_original_message(
                f"Command `{inter.values[0]}` is now enabled", view=None
            )
        else:
            await self.settings_db.add_command(inter.guild_id, inter.values[0])
            await inter.edit_original_message(
                f"Command `{inter.values[0]}` is now disabled", view=None
            )


class CommandsContextCommands(disnake.ui.StringSelect):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.settings_db = main_db
        self.commands_db = commands_db

    async def callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        await inter.send(
            f"Send new cooldown for `{inter.values[0]}` in seconds", ephemeral=True
        )
        new_cooldown = await self.bot.wait_for(
            "message",
            check=lambda m: m.author == inter.user
            and m.channel == inter.channel
            and m.content,
        )
        if not new_cooldown.content.isdigit():
            return await new_cooldown.response.send_message(
                "Cooldown must be a number", ephemeral=True
            )
        await self.commands_db.set_cooldown(
            inter.guild_id, inter.values[0], int(new_cooldown.content)
        )
        await new_cooldown.delete()
        await inter.send(
            f"New cooldown is `{new_cooldown.content}` for `{inter.values[0]}`",
            ephemeral=True,
        )


class CommandsContextSettings(disnake.ui.StringSelect):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.commands_db = commands_db

    async def callback(self, inter: disnake.MessageInteraction):
        if inter.values[0] in self.bot.cogs.keys():
            cog: Optional[commands.Cog] = self.bot.get_cog(inter.values[0])

            slash_commands = CommandsContextCommands(bot=self.bot)

            if s_commands := cog.get_commands():
                for command in s_commands:
                    slash_commands.add_option(label=command.name)

            view = disnake.ui.View()
            view.add_item(slash_commands)
            await inter.response.defer()
            await inter.edit_original_message(view=view)


class CommandsSlashSettings(disnake.ui.StringSelect):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.commands_db = commands_db

    async def callback(self, inter: disnake.MessageInteraction):
        if inter.values[0] in self.bot.cogs.keys():
            cog: Optional[commands.Cog] = self.bot.get_cog(inter.values[0])

            slash_commands = CommandsSlashCommands(bot=self.bot)

            if s_commands := cog.get_slash_commands():
                for command in s_commands:
                    slash_commands.add_option(label=command.name)

            view = disnake.ui.View()
            view.add_item(slash_commands)
            await inter.response.defer()
            await inter.edit_original_message(view=view)


class CommandsSettings(disnake.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.settings_db = main_db
        self.commands_db = commands_db

    @disnake.ui.string_select(
        cls=disnake.ui.StringSelect,  # type: ignore
        options=[
            disnake.SelectOption(label="Slash commands", value="slash", emoji="📖"),
            disnake.SelectOption(label="Context commands", value="context", emoji="✏️"),
        ],
    )
    async def select_callback(
        self, select: disnake.ui.StringSelect, interaction: MessageInteraction
    ):
        if select.values[0] == "context":
            slash_settings = CommandsContextSettings(bot=self.bot)

            for name, cog in self.bot.cogs.items():
                if not name.startswith("Event") and not name.startswith("Settings"):
                    slash_settings.add_option(
                        label=name,
                        description=cog.description,
                        emoji=getattr(cog, "EMOJI", None),
                    )

            view = disnake.ui.View()
            view.add_item(slash_settings)

            await interaction.response.send_message(view=view, ephemeral=True)

        elif select.values[0] == "slash":
            slash_settings = CommandsSlashSettings(bot=self.bot)

            for name, cog in self.bot.cogs.items():
                if not name.startswith("Event") and not name.startswith("Settings"):
                    slash_settings.add_option(
                        label=name,
                        description=cog.description,
                        emoji=getattr(cog, "EMOJI", None),
                    )

            view = disnake.ui.View()
            view.add_item(slash_settings)

            await interaction.response.send_message(view=view, ephemeral=True)
