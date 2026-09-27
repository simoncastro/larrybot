import asyncio

class Worker():
    def __init__(self, queue_manager, player):
        self.queue_manager = queue_manager
        self.player = player
        self.voice_client = None
        self.voice_ready = asyncio.Event()

    async def play_songs(self):
        while True:
            print("WORKER: waiting for voice")
            await self.voice_ready.wait()

            song = await self.queue_manager.next_song()
            print("WORKER: got song:", song.title)

            await self.player.play_song(song, self.voice_client)

    def set_voice_client(self, voice_client):
        self.voice_client = voice_client
        self.voice_ready.set()

    def clear_voice_client(self):
        self.voice_client = None
        self.voice_ready.clear()