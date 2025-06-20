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
    bot.remove_command("help")

    @bot.event
    async def on_ready():
        print(f"✅ Conectado como {bot.user}")

    async def load():
        await bot.load_extension("bot.commands.general")
        await bot.load_extension("bot.commands.music")
        await bot.load_extension("bot.utils.help")

    import asyncio
    asyncio.run(load())
    bot.run(config.DISCORD_TOKEN)
