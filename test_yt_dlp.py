import yt_dlp

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": False,
    "noplaylist": False,
    #"cookiesfrombrowser": ("firefox",),
    "extractor_args":{
        "youtube":{
            "player_client":["mweb"]
        }}
}

url = "https://www.youtube.com/watch?v=qkUVToIfrKg"

with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
    info = ydl.extract_info(url, download=False)