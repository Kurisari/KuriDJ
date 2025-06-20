import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from bot import config

def run_bot():
    load_dotenv()
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=config.BOT_PREFIX, intents=intents)

    # Carga de comandos (cogs)
    from bot.commands.music import MusicCommands
    from bot.commands.general import GeneralCommands

    bot.add_cog(MusicCommands(bot))
    bot.add_cog(GeneralCommands(bot))

    @bot.event
    async def on_ready():
        print(f"✅ Conectado como {bot.user}")

    bot.run(config.DISCORD_TOKEN)
