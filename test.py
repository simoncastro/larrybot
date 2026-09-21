import asyncio
from player import Song
from storage import load_queue_from_save, save_queue

queue = asyncio.Queue()

queue.put_nowait(Song(url="test 1", title="titre test 1", requested_by="Simon"))
queue.put_nowait(Song(url="test 2", title="titre test 2", requested_by="Jillome"))
queue.put_nowait(Song(url="test 3", title="titre test 3", requested_by="Francis"))
queue.put_nowait(Song(url="test 4", title="titre test 4", requested_by="Gael"))

save_queue(queue)

queue = None

queue = load_queue_from_save()

save_queue(queue)
