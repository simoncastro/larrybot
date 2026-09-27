import asyncio

from queue_manager import QueueManager
from worker import Worker



class FakePlayer:
    async def play_song(self, song, voice_client):
        print(f"FAKE PLAY: {song.title}")
        print(f"URL: {song.url}")
        print(f"Requested by: {song.requested_by}")

class FakeVoiceClient:
    pass

async def main():
    queue_manager = QueueManager()
    player = FakePlayer()
    worker = Worker(
        queue_manager=queue_manager,
        player=player,
    )
    voice_client = FakeVoiceClient
    worker.set_voice_client(voice_client)

    #await queue_manager.add_playlist("https://www.youtube.com/playlist?list=PLHP7snBXNHgqvlTYiqFzn4yT0RMg5Wo-k", "Simon")
    await queue_manager.add_song("https://www.youtube.com/watch?v=qkUVToIfrKg", "Simon")

    await worker.play_songs()


if __name__ == "__main__":
    asyncio.run(main())