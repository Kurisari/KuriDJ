import discord
import yt_dlp

ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'cookies': '/etc/secrets/cookies.txt'
}

async def play_audio(ctx, url):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']

        source = await discord.FFmpegOpusAudio.from_probe(audio_url)
        ctx.voice_client.stop()
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 Reproduciendo: **{info.get('title', 'Desconocido')}**")
    except Exception as e:
        await ctx.send("❌ Error al reproducir el audio.")
        print(f"[Error] {e}")
