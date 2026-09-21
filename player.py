import asyncio
import yt_dlp
import discord
from dataclasses import asdict, dataclass
from storage import save_queue, load_queue_from_save


YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": False,
    # "extractor_args":{
    #     "youtube":{
    #         "player_client":["mweb"]
    #     }}
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
        self.load()
        self.voice_client = None
        self.voice_ready = asyncio.Event()

    async def worker(self):
        while True:
            print("WORKER: waiting for voice")
            await self.voice_ready.wait()
            print("WORKER: voice ready")

            song = await self.next_song()
            print("WORKER: got song:", song.title)

            await self.play_song(song)

    async def add_song(self, url, requested_by):
        info = await self.extract_song_data(url)
        
        title = info.get("title", "Unknown title")

        song = Song(
            url= url, 
            title= title, 
            requested_by= requested_by)

        await self.queue.put(song)

        self.save()


    async def next_song(self):
        song = await self.queue.get()
        print("NEXT SONG: removing", song.title)
        self.save()

        return song

    async def play_song(self, song):
        info = await self.extract_song_data(song.url)
        audio_url = info["url"]

        print("PLAY: extracted audio URL")
        print("PLAY: duration:", info.get("duration"))

        source = discord.FFmpegPCMAudio(
            audio_url,
            stderr=None,
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

        print("PLAY: starting Discord audio")
        self.voice_client.play(
            source, 
            after= after_playing)

        await fut

    def is_empty(self):
        return self.queue.empty()

    def save(self):
        print("SAVE:", len(self.queue._queue), "songs")
        queue_dict = [asdict(song) for song in self.queue._queue]
        save_queue(queue_dict)

    def load(self):
        try:
            song_dict = load_queue_from_save()
            for song_data in song_dict:
                self.queue.put_nowait(Song(**song_data))
        except FileNotFoundError:
            return

    async def extract_song_data(self, url):
        def extract():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                return ydl.extract_info(url, download=False)
            

        loop = asyncio.get_running_loop()
        #yt-dlp is blocking, so don't run it directly on Discord's event loop
        info = await loop.run_in_executor(None, extract)


        return info

    def set_voice_client(self, voice_client):
        self.voice_client = voice_client
        self.voice_ready.set()

    def clear_voice_client(self):
        print("CLEAR VOICE CLIENT")
        self.voice_client = None
        self.voice_ready.clear()
