import discord
from yt_dlp import YoutubeDL

async def play_audio(ctx, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'cookiefile': '/etc/secrets/cookies.txt'  # Asegúrate que exista en Render
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']

        source = await discord.FFmpegOpusAudio.from_probe(audio_url)
        ctx.voice_client.stop()
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 Reproduciendo: **{info.get('title', 'Desconocido')}**")
    except Exception as e:
        await ctx.send("❌ Error al reproducir el audio.")
        print(f"[Error] {e}")
