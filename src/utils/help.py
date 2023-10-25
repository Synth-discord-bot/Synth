from typing import Mapping, Optional, List, Set, Union

from disnake import Embed
from disnake.ext import commands


class CustomHelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command: commands.Command) -> str:
        command_signature = command.signature.replace("=", " or ")
        return (
            f"{self.context.clean_prefix}{command.qualified_name} {command_signature}"
        )

    async def embed_help(
        self,
        title: str,
        description: Optional[str] = None,
        mapping: Optional[Mapping] = None,
        command_set: Union[
            List[commands.Command], Optional[Set[commands.Command]]
        ] = None,
    ) -> Embed:
        embed = Embed(title=title)
        if description:
            embed.description = description

        if command_set:
            filtered_cog = await self.filter_commands(command_set, sort=True)
            for command in filtered_cog:
                embed.add_field(
                    name=self.get_command_signature(command),
                    value=command.short_doc.format(prefix=self.context.prefix) or "...",
                    inline=False,
                )

        if mapping:
            for cog_name, cog_commands in mapping.items():
                filtered_commands = await self.filter_commands(
                    commands=cog_commands, sort=True
                )
                if not filtered_commands:
                    continue

                name = cog_name.qualified_name if cog_name else "No category"
                command_list = "\u2002".join(
                    f"```{self.context.clean_prefix}{command.name}```"
                    for command in filtered_commands
                )
                value = (
                    f"**{cog_name.description}**\n{command_list}"
                    if cog_name and cog_name.description
                    else cog_commands
                )
                embed.add_field(name=name, value=value, inline=False)

        return embed

    async def send_bot_help(
        self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]
    ) -> None:
        await self.get_destination().send(
            embed=await self.embed_help(
                title="Bot Commands",
                description=self.context.bot.description,
                mapping=mapping,
            )
        )

    async def send_command_help(self, command: commands.Command) -> None:
        await self.get_destination().send(
            embed=await self.embed_help(
                title=f"{command.qualified_name} | Help",
                description=f"**{self.context.prefix}{command.qualified_name}**\n{command.help}",
                command_set=command.commands
                if isinstance(command, commands.Group)
                else None,
            )
        )

    async def send_cog_help(self, cog: commands.Cog) -> None:
        await self.get_destination().send(
            embed=await self.embed_help(
                title=f"{cog.qualified_name} | Help",
                description=cog.description,
                command_set=cog.get_commands(),
            )
        )
