from discord.ext import commands
from discord import Embed

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def helpme(self, ctx):
        embed = Embed(
            title="📜 Lista de comandos disponibles",
            description="Aquí tienes todos los comandos de KuriDJ",
            color=0x7289da
        )

        for command in self.bot.commands:
            if not command.hidden:
                name = f"`!{command.name} {command.signature}`"  # Aquí agregamos la firma
                desc = command.help or "Sin descripción."
                embed.add_field(name=name, value=desc, inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
