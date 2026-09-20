import subprocess
import sys
import asyncio

import yt_dlp

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": False,
    "cookiesfrombrowser": ("firefox",)
}

YOUTUBE_URL =  "https://www.youtube.com/watch?v=qkUVToIfrKg"

def extract():
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        return ydl.extract_info(YOUTUBE_URL, download=False)

def test_ffmpeg(url):
    ffmpeg = [
        "ffmpeg",
        "-reconnect", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",
        "-i", url,
        "-f", "s16le",
        "-ar", "48000",
        "-ac", "2",
        "-loglevel", "info",
        "-blocksize", "8192",
        "-vn","pipe:1",
    ]

    with open("ffmpeg-debug.log", "a") as log:
        process = subprocess.Popen(
            ffmpeg,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        while True:
            data = process.stdout.read(3840)
            if len(data) != 3840:
                print(len(data))
                print(process.wait())
                break

async def main():
    #url = 'https://rr1---sn-tt1e7nl6.googlevideo.com/videoplayback?expire=1789909787&ei=u4avaoyvM_qd2_gPvt_JQA&ip=198.44.157.147&id=o-ANSrVh_4pC4GK5UTHdQCyMLoxx95f408xtPLYIozAsYB&itag=251&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&cps=385&met=1789888187%2C&mh=xH&mm=31%2C26&mn=sn-tt1e7nl6%2Csn-ojvgq5-5m&ms=au%2Conr&mv=m&mvi=1&pl=24&rms=au%2Cau&pcm2=yes&initcwndbps=2521250&siu=1&bui=AR3QkAmpgxjJ9mkWq9m1VXjK6Qyp-KNWA-hLPPxCnxlwKSuYIS5z6xwE9PrDW5k53VGPBDrw8w&spc=I-rgIQIfG9iXmrb8W3tsdHcBYquxj_EGCqcf3lhGYqLxkcZX4if-R7KmnHHwzmZzEWEgzQ1CMDaua0ZZVhhZD7es1nE&vprv=1&svpuc=1&mime=audio%2Fwebm&ns=yTUesyfB9mH7vNeHyHsUtI8Y&rqh=1&gir=yes&clen=2947508&dur=233.201&lmt=1745253000866053&mt=1789887654&fvip=4&keepalive=yes&fexp=51565116%2C52227521&c=WEB_EMBEDDED_PLAYER&sefc=1&txp=5532534&n=wxodZSbka8g4LQ&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cpcm2%2Csiu%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AE0s2JYwRQIgeZ_0NfgVQCXUgNN_cPTIVbLPOEr-1WSP8fDNYCzRGZQCIQClAvbmgCXhjdsvonVcmYpTkFej3mM1CMD8YlQ0trJ0fw%3D%3D&lsparams=cps%2Cmet%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIhAOkC4oEhASZTF3EyV5Ktip8aDgXW8U4KDR05ojVc11kRAiAuxV_1L8Ja64HEhK7vVIyTKnW03TzPRPIrzgGjBIpl5w%3D%3D'

        
    info = extract()
    url = info["url"]
    print("EXTRACTED")

    test_ffmpeg(url)

    await asyncio.sleep(3)

    test_ffmpeg(url)


    print("STDIN :", sys.stdin, "closed:", sys.stdin.closed)
    print("STDOUT:", sys.stdout, "closed:", sys.stdout.closed)
    print("STDERR:", sys.stderr, "closed:", sys.stderr.closed)

    print("stdin fd :", sys.stdin.fileno())
    print("stdout fd:", sys.stdout.fileno())
    print("stderr fd:", sys.stderr.fileno())





asyncio.run(main())