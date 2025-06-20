from discord.ext import commands
from discord import FFmpegPCMAudio, Embed
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

    def convert_to_invidious(self, url: str) -> str:
        """Convierte una URL de YouTube a una de Invidious."""
        invidious_instance = "https://vid.puffyan.us"
        video_id = ""

        if "watch?v=" in url:
            video_id = url.split("watch?v=")[-1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
        elif "invidio" in url:
            return url  # Ya es Invidious

        if not video_id:
            raise ValueError("No se pudo extraer el ID del video.")

        return f"{invidious_instance}/watch?v={video_id}"

    def download_audio(self, url):
        invidious_url = self.convert_to_invidious(url)

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': 'in_playlist',
            'default_search': 'auto',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(invidious_url, download=False)
            return info['url'], info.get('title', 'Unknown Title')

    @commands.command(name="play", help="Reproduce una canción desde YouTube o la añade a la cola.")
    async def play(self, ctx, url: str):
        queue = self.get_queue(ctx.guild.id)

        if not ctx.voice_client:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(embed=Embed(description="❌ Debes estar en un canal de voz.", color=0xff0000))
                return

        try:
            audio_url, title = self.download_audio(url)
        except Exception as e:
            await ctx.send(embed=Embed(description=f"❌ Error al procesar la canción: {str(e)}", color=0xff0000))
            return

        queue.add((audio_url, title))

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

        embed = Embed(title="🎵 Añadido a la cola", description=f"**{title}**", color=0x00ffcc)
        await ctx.send(embed=embed)

    async def play_next(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        next_item = queue.get_next()

        if next_item is None:
            await ctx.send(embed=Embed(description="✅ La cola está vacía.", color=0x00ff00))
            return

        url, title = next_item
        source = FFmpegPCMAudio(url)
        ctx.voice_client.play(
            source,
            after=lambda e: self.bot.loop.create_task(self.play_next(ctx))
        )
        embed = Embed(title="▶️ Reproduciendo ahora", description=f"**{title}**", color=0x3498db)
        await ctx.send(embed=embed)

    @commands.command(name="queue", help="Muestra la lista de canciones en la cola.")
    async def queue_cmd(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        current_queue = queue.view()
        if not current_queue:
            await ctx.send(embed=Embed(description="📭 La cola está vacía.", color=0xffcc00))
        else:
            embed = Embed(title="🎶 Cola de reproducción", color=0x9b59b6)
            for i, (_, title) in enumerate(current_queue, 1):
                embed.add_field(name=f"{i}.", value=title, inline=False)
            await ctx.send(embed=embed)

    @commands.command(name="skip", help="Salta la canción actual y reproduce la siguiente.")
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send(embed=Embed(description="⏭️ Canción saltada.", color=0xf1c40f))
        else:
            await ctx.send(embed=Embed(description="❌ No se está reproduciendo nada.", color=0xff0000))

    @commands.command(name="pause", help="Pausa la reproducción actual.")
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send(embed=Embed(description="⏸️ Música en pausa.", color=0xe67e22))
        else:
            await ctx.send(embed=Embed(description="❌ No hay música reproduciéndose.", color=0xff0000))

    @commands.command(name="resume", help="Reanuda la reproducción pausada.")
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send(embed=Embed(description="▶️ Música reanudada.", color=0x2ecc71))
        else:
            await ctx.send(embed=Embed(description="❌ No hay música pausada.", color=0xff0000))

    @commands.command(name="stop", help="Detiene la música y limpia la cola.")
    async def stop(self, ctx):
        vc = ctx.voice_client
        if vc:
            vc.stop()
            self.get_queue(ctx.guild.id).clear()
            await ctx.send(embed=Embed(description="🛑 Reproducción detenida y cola limpiada.", color=0xc0392b))
        else:
            await ctx.send(embed=Embed(description="❌ No estoy en un canal de voz.", color=0xff0000))

    @commands.command(name="leave", help="Me desconecto del canal de voz.")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send(embed=Embed(description="👋 Me he salido del canal de voz.", color=0x95a5a6))
        else:
            await ctx.send(embed=Embed(description="❌ No estoy en un canal de voz.", color=0xff0000))

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))
