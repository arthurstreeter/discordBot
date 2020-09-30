import random
import discord
import urllib
import secrets
import asyncio
import aiohttp
import re
import youtube_dl

from io import BytesIO
from discord.ext import commands
from utils import lists, permissions, http, default, argparser
from requests import Session
from utils.default import load, write
from datetime import datetime

ydl_opts = {'format': 'bestaudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Music_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
    @commands.command(aliases=["yt","youtube","music"])
    async def play(self, ctx, *, url: str):
        def get_song_url(url):
            query_string = urllib.parse.urlencode({"search_query" : url})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            search_results = re.findall(r'\"videoId\"\:\"(.{11})', html_content.read().decode())
            url = "http://www.youtube.com/watch?v=" + search_results[0]
            alturl = "http://www.youtube.com/watch?v=" + search_results[1]
            return url, alturl
        try:
            channel = ctx.author.voice.channel
        except:
            return await ctx.send("You're not here, broskie.")
        guild = ctx.guild
        textchannel = str(ctx.channel.name).strip()
        if textchannel != "music":
            return
        if "http" not in url:
            url, alturl = get_song_url(url)
        
        vc: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=guild)

        if channel != None and vc == None:
            vc = await discord.VoiceChannel.connect(channel)
        if vc.is_playing:
            vc.stop()
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    source = ydl.extract_info(url, download=False)['formats'][0]['url']
                    title = ydl.extract_info(url, download=False)['title']
                    vidtime = ydl.extract_info(url, download=False)['duration']
        except:
            url = alturl
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    source = ydl.extract_info(url, download=False)['formats'][0]['url']
                    title = ydl.extract_info(url, download=False)['title']
                    vidtime = ydl.extract_info(url, download=False)['duration']
        vc.play(discord.FFmpegPCMAudio(source, **FFMPEG_OPTIONS), after=print('songended'))
        vc.source = discord.PCMVolumeTransformer(vc.source, volume=.25)
        ytLogo = "https://cdn.iconscout.com/icon/free/png-256/youtube-85-226402.png"
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name="YouTube Player", icon_url=ytLogo)
        embed.set_footer(text=f"Playing : {title}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("⏯")
        await msg.add_reaction("⏹")
        def reaction_check(reaction, user):
            if user != msg.author and str(reaction.emoji) in ["⏯","⏹"]:
                return True
            else:
                return False
        try:
            while vc.is_playing or vc.is_paused:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=vidtime, check=reaction_check)
                emote = str(reaction)
                if emote == "⏯":
                    if vc.is_playing():
                        vc.pause()
                        await msg.remove_reaction(reaction, user)
                    elif vc.is_paused():
                        vc.resume()
                        await msg.remove_reaction(reaction, user)
                elif emote == "⏹":
                    vc.stop()
                    await vc.disconnect()
                    await msg.delete()
                    return
                await asyncio.sleep(.5)
        except asyncio.TimeoutError:
            msg.delete()


    @commands.command(aliases=["kill", "getout","silence","SILENCE"])
    async def stop(self, ctx):
        guild = ctx.guild
        vc: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=guild)
        if vc:
            vc.stop()
            await vc.disconnect()

    @commands.command()
    async def pause(self, ctx):
        guild = ctx.guild
        vc: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=guild)
        if vc:
            vc.pause()

    @commands.command(aliases=["start"])
    async def resume(self, ctx):
        guild = ctx.guild
        vc: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=guild)
        if vc:
            vc.resume()

def setup(bot):
    bot.add_cog(Music_Commands(bot))
