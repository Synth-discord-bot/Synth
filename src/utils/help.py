from typing import Mapping, Optional, List, Set, Union

from disnake import Embed, ui, SelectOption, Interaction
from disnake.ext import commands


class HelpDropdown(ui.Select):
    def __init__(
        self, help_command: "CustomHelpCommand", options: list[SelectOption]
    ) -> None:
        super().__init__(
            placeholder="Choose a category",
            min_values=1,
            max_values=1,
            options=options,
        )
        self._help_command = help_command

    async def callback(self, interaction: Interaction):
        embed = (
            await self._help_command.cog_help_embed(
                self._help_command.context.bot.get_cog(self.values[0])
            )
            if self.values[0] != self.options[0].value
            else await self._help_command.bot_help_embed(
                self._help_command.get_bot_mapping()
            )
        )
        await interaction.response.edit_message(embed=embed)


class HelpView(ui.View):
    def __init__(
        self,
        help_command: "CustomHelpCommand",
        options: list[SelectOption],
        *,
        timeout: Optional[float] = 120.0,
    ) -> None:
        super().__init__(timeout=timeout)
        self.add_item(HelpDropdown(help_command, options))
        self._help_command = help_command

    async def on_timeout(self) -> None:
        self.clear_items()
        await self._help_command.response.edit(view=self)

    async def interaction_check(self, interaction: Interaction) -> bool:
        return self._help_command.context.author == interaction.user


class CustomHelpCommand(commands.MinimalHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.response = None

    def get_command_signature(self, command: commands.Command) -> str:
        command_signature = command.signature.replace("=", " or ")
        return (
            f"{self.context.clean_prefix}{command.qualified_name} {command_signature}"
        )

    async def _cog_select_options(self) -> list[SelectOption]:
        options: list[SelectOption] = [
            SelectOption(
                label="Home",
                emoji="<:home:1169690507253911733>",
                description="Return to main menu",
            )
        ]

        for cog, _ in self.get_bot_mapping().items():
            if cog and (not cog.qualified_name.startswith("Event")):
                options.append(
                    SelectOption(
                        label=cog.qualified_name if cog else "No Category",
                        emoji=getattr(cog, "EMOJI", None),
                        description=cog.description[:100]
                        if cog and cog.description
                        else None,
                    )
                )

        return options

    async def embed_help(
        self,
        title: str,
        description: Optional[str] = None,
        mapping: Optional[Mapping] = None,
        command_list: Union[
            List[commands.Command], Optional[Set[commands.Command]]
        ] = None,
    ) -> Embed:
        embed = Embed(title=title)

        if description:
            embed.description = description

        if command_list:
            filtered_cog = await self.filter_commands(command_list, sort=True)
            for command in filtered_cog:
                embed.add_field(
                    name=self.get_command_signature(command),
                    value=command.short_doc.format(prefix=self.context.prefix) or "...",
                    inline=False,
                )

        if mapping:
            for cog, command_list in mapping.items():
                if cog and (not cog.qualified_name.startswith("Event")):
                    if filtered := await self.filter_commands(command_list, sort=True):
                        name = cog.qualified_name if cog else "No category"
                        emoji = getattr(cog, "EMOJI", None)
                        cog_label = f"{emoji} {name}" if emoji else name
                        cmd_list = "\u2002".join(
                            f"`{self.context.clean_prefix}{cmd.name}`"
                            for cmd in filtered
                        )
                        value = (
                            f"{cog.description}\n{cmd_list}"
                            if cog and cog.description
                            else cmd_list
                        )
                        embed.add_field(name=cog_label, value=value)

        return embed

    async def bot_help_embed(self, mapping: Optional[Mapping]) -> Embed:
        return await self.embed_help(
            title="Bot Commands",
            description=self.context.bot.description,
            mapping=mapping,
        )

    async def send_bot_help(self, mapping: Optional[Mapping]) -> None:
        embed = await self.bot_help_embed(mapping)
        options = await self._cog_select_options()
        self.response = await self.get_destination().send(
            embed=embed, view=HelpView(self, options)
        )

    async def send_command_help(self, command: commands.Command) -> None:
        emoji = getattr(command.cog, "EMOJI", None)
        embed = await self.embed_help(
            title=f"{emoji} {command.qualified_name}"
            if emoji
            else command.qualified_name,
            description=command.help,
            command_list=command.commands
            if isinstance(command, commands.Group)
            else None,
        )
        await self.get_destination().send(embed=embed)

    async def cog_help_embed(self, cog: Optional[commands.Cog]) -> Embed:
        if cog is None:
            return await self.embed_help(
                title=f"No category", command_list=self.get_bot_mapping()[None]
            )
        emoji = getattr(cog, "EMOJI", None)
        return await self.embed_help(
            title=f"{emoji} {cog.qualified_name}\n" if emoji else cog.qualified_name,
            description=cog.description,
            command_list=cog.get_commands(),
        )

    async def send_cog_help(self, cog: commands.Cog) -> None:
        embed = await self.cog_help_embed(cog)
        await self.get_destination().send(embed=embed)

    send_group_help = send_command_help


