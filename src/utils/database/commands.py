from typing import Optional, List, Dict, Any

from .base import BaseDatabase


class CommandsDatabase(BaseDatabase):
    def __init__(self, database_name: str) -> None:
        super().__init__(database_name)

    """
    {
        "id": GUILD_ID,
        "commands": [
            {
                "name":
                "cooldown": COMMAND1_COOLDOWN,
                "disabled": BOOL
            }
        ]
    }
    """

    def get_command(
        self, guild_id: int, command_name: str, to_return: str = None
    ) -> Optional[int]:
        if commands := self.get_items_in_cache({"id": guild_id}, to_return="commands"):
            for command in commands:
                if command.get("name") == command:
                    if to_return:
                        return command.get(to_return, None)
                    
                    return command
                        

    def get_command_cooldown(self, guild_id: int, command: str) -> Optional[int]:
        if commands := self.get_items_in_cache({"id": guild_id}, to_return="commands"):
            for command_ in commands:
                if command_.get("name") == command:
                    return command_.get("cooldown")
    
    async def set_cooldown(
        self, guild_id: int, command: str, cooldown: int
    ):
        if await self.find_one_from_db({"id": guild_id}) is None:
            return await self.update_db({"id": guild_id}, {"commands": []})

        commands = await self._get_commands_list(guild_id=guild_id)
        
        if commands:
            for command_ in commands:
                if command_.get("name") == command:
                    command_.update({"cooldown": cooldown})
            else:
                commands.append({"name": command, "cooldown": cooldown, "disabled": False})
        else:
            commands = [{"name": command, "cooldown": cooldown, "disabled": False}]

        await self.update_db({"id": guild_id}, {"commands": commands})



    async def _get_commands_list(self, guild_id: int) -> List[Dict[str, Any]]:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return []

        return (await self.find_one_from_db({"id": guild_id})).get(
            "commands",
            []
        )
    
    async def check_command(
        self, guild_id: int, command: str, add_if_not_exists: bool = True
    ) -> bool:
        """
        Check if command is disabled in the guild
        """
        
        # check if commands list exists from cache
        commands = self.get_items_in_cache({"id": guild_id}, to_return="commands")
        if commands is not None:
            for command_ in commands:
                if command_.get("name") == command and command_.get("disabled"):
                    return True
            
            return False
        
        # check if commands list exists from database
        else:
            if not (commands := await self.find_one_from_db({"id": guild_id})) and add_if_not_exists:
                # try to find command in database
                commands = (await self.find_one_from_db({"id": guild_id})).get("commands", [])
                if commands:
                    command_: Dict[str, Any]
                    
                    for command_ in commands:
                        if command_.get("name") == command:
                            command_.update({"disabled": True})
                            break
                    
                    await self.update_db({"id": guild_id}, {"commands": [commands]})
            
            commands_list = self.get_command(guild_id=guild_id)
            return command in commands_list
        
        # if await self.find_one_from_db({"id": guild_id}) is None and add_if_not_exists:
            # await self.update_db({"id": guild_id}, {"commands": [command]})

        # commands_list = await self._get_commands_list(guild_id=guild_id)
        # return command in commands_list

    async def add_command(self, guild_id: int, command: str) -> None:
        if await self.find_one_from_db({"id": guild_id}) is None:
            command = {"name": command, "cooldown": 0, "disabled": True}
            return await self.update_db(
                {"id": guild_id}, {"commands": [command]}
            )

        if not await self.check_command(guild_id=guild_id, command=command):
            commands = await self._get_commands_list(guild_id=guild_id)
            for command_ in commands:
                if command_.get("name") == command:
                    command_.update({"disabled": True})
                    break
            # commands.append(, "disabled": True})
            await self.update_db({"id": guild_id}, {"commands": commands})

    async def delete_command(self, guild_id: int, command: str) -> None:
        if await self.find_one_from_db({"id": guild_id}) is None:
            return await self.update_db({"id": guild_id}, {"commands": []})

        commands = await self._get_commands_list(guild_id=guild_id)
        
        for command_ in commands:
            if command_.get("name") == command:
                command_.update({"disabled": False})
                break

        await self.update_db({"id": guild_id}, {"commands": commands})
