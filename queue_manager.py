import asyncio
import yt_dlp

from dataclasses import asdict
from storage import save_queue, load_queue_from_save
from song import Song
from enum import Enum

YDL_OPTIONS = {
    "quiet": True,
    "cookiefile": "cookies.txt",
}

SONG_YDL_OPTIONS = {
    **YDL_OPTIONS,
    "format": "bestaudio/best",
    "noplaylist": True,
}

PLAYLIST_YDL_OPTIONS = {
    **YDL_OPTIONS,
    "extract_flat": True,
}

class Type(Enum):
    SONG = 1
    PLAYLIST = 2

class QueueManager():

    def __init__(self):
        self.queue = asyncio.Queue()
        self.load()

    async def add_song(self, url, requested_by):
        info = await self.extract_data(url, Type.SONG)
        
        title = info.get("title", "Unknown title")

        song = Song(
            url= url, 
            title= title, 
            requested_by= requested_by)

        await self.queue.put(song)

        self.save()

    async def add_playlist(self, url, requested_by):
        playlist_data = await self.extract_data(url, Type.PLAYLIST)

        songs_data = playlist_data.get("entries", [])

        for song_data in songs_data:
            url = song_data.get("url")

            if not url:
                continue

            song = Song(
                url= url,
                title= song_data.get("title", "Unknown title"),
                requested_by=requested_by,
            )

            await self.queue.put(song)

        self.save()

    async def next_song(self):
        song = await self.queue.get()
        self.save()

        return song

    def clear_queue(self):
        self.queue = asyncio.Queue()
        self.save()

    async def extract_data(self, url, type):
        if type == Type.SONG:
            options = SONG_YDL_OPTIONS
        elif type == Type.PLAYLIST:
            options = PLAYLIST_YDL_OPTIONS
        else:
            raise ValueError(f"Unsupported type: {type}")
                
        def extract():
            with yt_dlp.YoutubeDL(options) as ydl:
                return ydl.extract_info(url, download=False)

        loop = asyncio.get_running_loop()
        #yt-dlp is blocking, so don't run it directly on Discord's event loop
        info = await loop.run_in_executor(None, extract)

        return info
    
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
