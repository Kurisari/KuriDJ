from discord.ext import commands
import discord
from bot.core.player import play_audio

from discord.ext import commands
from discord import FFmpegPCMAudio
from yt_dlp import YoutubeDL
from bot.utils.queue import MusicQueue

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}  # guild_id: MusicQueue()

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = MusicQueue()
        return self.queues[guild_id]
    
    @commands.command(name="play")
    async def play(self, ctx, url: str):
        queue = self.get_queue(ctx.guild.id)

        def download_audio(url):
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'noplaylist': True,
                'extract_flat': 'in_playlist',
                'default_search': 'auto',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info['url'], info.get('title', 'Unknown Title')

        if not ctx.voice_client:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("❌ Debes estar en un canal de voz.")
                return

        audio_url, title = download_audio(url)
        queue.add((audio_url, title))

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

        await ctx.send(f"🎵 Añadido a la cola: **{title}**")

    async def play_next(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        next_item = queue.get_next()

        if next_item is None:
            await ctx.send("✅ La cola está vacía.")
            return

        url, title = next_item
        source = FFmpegPCMAudio(url)
        ctx.voice_client.play(
            source,
            after=lambda e: self.bot.loop.create_task(self.play_next(ctx))
        )
        await ctx.send(f"▶️ Reproduciendo: **{title}**")
    
    @commands.command(name="queue")
    async def queue_cmd(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        current_queue = queue.view()
        if not current_queue:
            await ctx.send("📭 La cola está vacía.")
        else:
            msg = "**🎶 Cola de reproducción:**\n"
            for i, (_, title) in enumerate(current_queue, 1):
                msg += f"{i}. {title}\n"
            await ctx.send(msg)

    @commands.command(name="skip")
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Canción saltada.")
        else:
            await ctx.send("❌ No se está reproduciendo nada.")
    
    @commands.command(name="pause")
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("⏸️ Música en pausa.")
        else:
            await ctx.send("❌ No hay música reproduciéndose.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("▶️ Música reanudada.")
        else:
            await ctx.send("❌ No hay música pausada.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        vc = ctx.voice_client
        if vc:
            vc.stop()
            self.get_queue(ctx.guild.id).clear()
            await ctx.send("🛑 Reproducción detenida y cola limpiada.")
        else:
            await ctx.send("❌ No estoy en un canal de voz.")

    @commands.command(name="leave")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("❌ No estoy en un canal de voz.")

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))