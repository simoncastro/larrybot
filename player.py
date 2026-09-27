import asyncio
import discord
import sys
import yt_dlp


YDL_OPTIONS = {
    "quiet": True,
    "format": "bestaudio/best",
    "cookiefile": "cookies.txt",
    "noplaylist": True,
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

class Player():

    async def play_song(self, song, voice_client):
        audio_url = await self.get_playable_url(song.url)

        source = discord.FFmpegPCMAudio(
            audio_url,
            stderr=sys.stderr,
            **FFMPEG_OPTIONS
        )

        loop = asyncio.get_running_loop()
        fut = loop.create_future()

        def resolve_future():
            if not fut.done():
                fut.set_result(None)

        def after_playing(error):
            print("AFTER PLAYING:", error)
            loop.call_soon_threadsafe(resolve_future)

        voice_client.play(
            source, 
            after= after_playing)

        await fut

    async def get_playable_url(self, url):
        def extract():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                return ydl.extract_info(url, download=False)

        loop = asyncio.get_running_loop()
        #yt-dlp is blocking, so don't run it directly on Discord's event loop
        info = await loop.run_in_executor(None, extract)

        return info.get("url")
