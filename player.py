import asyncio
import yt_dlp
import discord
from dataclasses import dataclass


YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": False,
    "extractor_args":{
        "youtube":{
            "player_client":["mweb"]
        }}
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

@dataclass
class Song():
    url:str
    title: str
    requested_by: str

class Player():

    def __init__(self):
        self.queue = asyncio.Queue()
        self.voice_client = None

    async def worker(self):
        while True:
            song = await self.next_song()
            await self.play_song(song)

    async def add_song(self, voice_client, url, requested_by):
        self.voice_client = voice_client

        def extract():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                return ydl.extract_info(url, download=False)
            
        try:
            loop = asyncio.get_running_loop()
            #yt-dlp is blocking, so don't run it directly on Discord's event loop
            info = await loop.run_in_executor(None, extract)
        except:
            raise

        audio_url = info["url"]
        title = info.get("title", "Unknown title")

        song = Song(
            url= audio_url, 
            title= title, 
            requested_by= requested_by)

        await self.queue.put(song)


    async def next_song(self):
        return await self.queue.get()

    async def play_song(self, song):
        source = discord.FFmpegPCMAudio(
            song.url,
            stderr=None,
            **FFMPEG_OPTIONS
        )

        loop = asyncio.get_running_loop()
        fut = loop.create_future()

        def after_playing(error):
            print("AFTER PLAYING:", error)
            loop.call_soon_threadsafe(fut.set_result, None)

        self.voice_client.play(
            source, 
            after= after_playing)

        await fut


    def is_empty(self):
        return self.queue.empty()
