import asyncio
import os

import discord
import yt_dlp
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": False,
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Bot ID: {bot.user.id}")


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.command()
async def play(ctx, url: str):
    # User must be in a voice channel
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel.")
        return

    channel = ctx.author.voice.channel

    # Connect or move LarryBot to the user's voice channel
    if ctx.voice_client is None:
        voice_client = await channel.connect()
    else:
        voice_client = ctx.voice_client

        if voice_client.channel != channel:
            await voice_client.move_to(channel)

    # Stop the currently playing song
    if voice_client.is_playing():
        voice_client.stop()

    await ctx.send("Loading...")

    # yt-dlp is blocking, so don't run it directly on Discord's event loop
    loop = asyncio.get_running_loop()

    def extract():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        info = await loop.run_in_executor(None, extract)
    except Exception as error:
        print(error)
        await ctx.send("Couldn't load that URL.")
        return

    audio_url = info["url"]
    title = info.get("title", "Unknown title")

    source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)

    voice_client.play(source)

    await ctx.send(f"Now playing: **{title}**")


@bot.command()
async def stop(ctx):
    if ctx.voice_client is None:
        await ctx.send("I'm not in a voice channel.")
        return

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Stopped.")
    else:
        await ctx.send("There is no song that I could stop!")


@bot.command()
async def leave(ctx):
    if ctx.voice_client is None:
        await ctx.send("I'm not in a voice channel.")
        return

    await ctx.voice_client.disconnect()
    await ctx.send("Disconnected.")


if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing from .env")

bot.run(TOKEN)