from discord.ext import commands
import discord
from bot.core.player import play_audio

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join")
    async def join(self, ctx):
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("🚫 Debes estar en un canal de voz.")

    @commands.command(name="leave")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("❌ No estoy en un canal de voz.")

    @commands.command(name="play")
    async def play(self, ctx, url: str):
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        await play_audio(ctx, url)

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))