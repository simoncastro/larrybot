import json


def save_queue(queue_dict):
    with open("datafile.json", "w") as write:
        json.dump(queue_dict, write)

def load_queue_from_save():
    with open("datafile.json") as json_data:
        songs_data = json.load(json_data)

    return songs_data