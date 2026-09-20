import asyncio
import os
import discord

from discord.ext import commands
from dotenv import load_dotenv
from player import Player

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

class LarryBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.player = Player()

    async def setup_hook(self):
        self.audio_task = asyncio.create_task(
            self.player.worker()
        )

        await self.add_cog(Controls(self))

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print(f"Bot ID: {self.user.id}")


class Controls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_in_channel(self, ctx):
        if ctx.voice_client is None:
            await ctx.send("I'm not in a voice channel.")
            return False
        else:
            return True

    @commands.command()
    async def play(self, ctx, url):
        if ctx.voice_client is None:
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

        try:
            await self.bot.player.add_song(voice_client, url, ctx.author)
        except Exception as error:
            print(error)
            await ctx.send("Couldn't load that URL.")


    @commands.command()
    async def stop(self, ctx):
        if not await self.is_in_channel(ctx):
            return

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Stopped.")
        else:
            await ctx.send("There is no song that I could stop!")

    @commands.command()
    async def leave(self, ctx):
        if not await self.is_in_channel(ctx):
            return

        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected.")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing from .env")

bot = LarryBot()

bot.run(TOKEN)