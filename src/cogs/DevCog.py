import disnake
from disnake.ext import commands
from traceback import format_exception
import contextlib
import io
import textwrap


class Developers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super(Developers, self).__init__()
        self.bot = bot

    # TODO: EVAL WITHOUGHT INTERNET
    # TODO: BLACKLIST SETTINGS
    # TODO: COGS LOAD/UNLOAD/RELOAD
        
    def clean_code(self, content):
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:])[:-3]
        else:
            return content

    @commands.slash_command(name="eval", guild_ids=[1109511263509291098])
    async def eval_command(self, interaction, *, code):
        if interaction.user.id not in self.bot.owner_ids:
            print(f"{interaction.user.name} | {interaction.user.id} tried to use /eval")

        await interaction.response.defer()
        pending_embed = disnake.Embed(description='Code is processing...', color=disnake.Colour.from_rgb(255, 255, 0))
        message = await interaction.followup.send(embed=pending_embed)

        success_embed = disnake.Embed(title='Code processing - success', color=disnake.Colour.from_rgb(0, 255, 0))

        code = self.clean_code(code)
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


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Developers(bot))
