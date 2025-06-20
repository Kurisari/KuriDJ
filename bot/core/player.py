import discord
import aiohttp
import re

INVIDIOUS_BASE = "https://invidious.snopyta.org"

async def get_audio_url(video_id):
    api_url = f"{INVIDIOUS_BASE}/api/v1/videos/{video_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                raise Exception(f"Error al obtener info del video: {resp.status}")
            data = await resp.json()
            # Tomamos el primer audio adaptativo disponible
            audio_url = data['adaptiveFormats'][0]['url']
            return audio_url

async def play_audio(ctx, url):
    # Extraemos el ID del video de la URL
    match = re.search(r"v=([\w-]+)", url)
    if not match:
        await ctx.send("❌ URL inválida de YouTube.")
        return
    video_id = match.group(1)

    try:
        audio_url = await get_audio_url(video_id)
    except Exception as e:
        await ctx.send(f"❌ Error al obtener el audio: {e}")
        print(f"[Error] {e}")
        return

    source = await discord.FFmpegOpusAudio.from_probe(audio_url)

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    ctx.voice_client.play(source)

    await ctx.send(f"🎶 Reproduciendo audio del video: https://youtu.be/{video_id}")
