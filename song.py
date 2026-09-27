from dataclasses import dataclass


@dataclass
class Song():
    url:str
    title:str
    requested_by:str