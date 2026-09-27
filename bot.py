import asyncio
import os
import discord

from discord.ext import commands
from dotenv import load_dotenv
from player import Player
from queue_manager import QueueManager
from worker import Worker

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

class LarryBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.queue_manager = QueueManager()
        self.player = Player()
        self.worker = Worker(
            queue_manager=self.queue_manager,
            player=self.player
        )

    async def setup_hook(self):
        self.audio_task = asyncio.create_task(
            self.worker.play_songs()
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

    async def prepare_to_play(self, ctx):
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

        return voice_client


    @commands.command(help="Joue le video ou l'ajoute à la fin de la queue s'il y a d'autres vidéos dedans")
    async def play(self, ctx, url):
        voice_client = await self.prepare_to_play(ctx)

        if voice_client is None:
            return

        try:
            self.bot.worker.set_voice_client(voice_client)
            await self.bot.queue_manager.add_song(url, ctx.author.name)
        except Exception as error:
            print(error)
            await ctx.send("Couldn't load that URL.")

    @commands.command(help="Ajoute une liste de lecture, doit venir de la page principale de la liste, pas d'un des vidéos qui sont dedans")
    async def playlist(self, ctx, url):
        voice_client = await self.prepare_to_play(ctx)

        if voice_client is None:
            return

        try:
            self.bot.worker.set_voice_client(voice_client)
            await self.bot.queue_manager.add_playlist(url, ctx.author.name)
        except Exception as error:
            print(error)
            await ctx.send("Couldn't load that URL.")


    @commands.command(help="Arrête la lecture, après resume la chanson en cours sera skip")
    async def stop(self, ctx):
        if not await self.is_in_channel(ctx):
            return

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Stopped.")
        else:
            await ctx.send("There is no song that I could stop!")

    @commands.command(help="Larry quitte le channel")
    async def leave(self, ctx):
        if not await self.is_in_channel(ctx):
            return

        await ctx.voice_client.disconnect()
        self.bot.worker.clear_voice_client()
        await ctx.send("Disconnected.")

    @commands.command(help="Reprend la lecture de la queue")
    async def resume(self, ctx):
        voice_client = await self.prepare_to_play(ctx)

        if voice_client is None:
            return

        self.bot.worker.set_voice_client(voice_client)

    @commands.command(help="Vide la queue")
    async def clear(self, ctx):
        self.bot.queue_manager.clear_queue()
        await ctx.send("Queue cleared.")

    @commands.command(help="affiche la liste des commandes")
    async def h(self, ctx):
        message = "\n".join(
            f"!{command.name} - {command.help}"
            for command in self.bot.commands
        )      

        await ctx.send(message)


if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing from .env")

async def main():
    bot = LarryBot()
    try:
        await bot.start(TOKEN)
    finally:
        bot.worker.clear_voice_client()

        bot.audio_task.cancel()

        try:
            await bot.audio_task
        except asyncio.CancelledError:
            pass

        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())