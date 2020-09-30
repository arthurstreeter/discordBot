import random
import discord
import urllib
import secrets
import asyncio
import aiohttp
import re
import praw
import youtube_dl

from io import BytesIO
from discord.ext import commands
from utils import lists, permissions, http, default, argparser
from requests import Session
from utils.default import load, write
from datetime import datetime
from gtts import gTTS

session = Session()
reddit = praw.Reddit(client_id="eF4i6KOndUjY2A",
     client_secret="S7UrsF_2ZoMMvmvyoE22Ulq_-c4",	
     user_agent="BmBro"
)
simpImage = "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/items/295110/937ced2364feae911477d017567300b09491d670.png"
simpPlus = "https://www.iconfinder.com/data/icons/basic-ui-elements-28/512/1034_Add_new_plus_sign-512.png"
simpMinus = "https://www.clker.com/cliparts/u/P/r/l/4/l/minus-sign-subtract-hi.png"

class BmBros_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
    @commands.command(aliases=['r', 'red'])
    @commands.has_role("HOMIES")
    async def reddit(self, ctx, *, text: str):
        """Reddit bro
        """
        subreddit = text.strip()
        output = ''
        abstract = {}
        subredditcheck = False
        nsfw_counter = 0
        naughty_response = [
            "Looks like someone's tryin'a be dirty.",
            "Rly dude :ResidentSleeper:",
            ":PeepoHmm:",
            ":NOPERS:",
            ":monkaHide:"
        ]
        try:
            for submission in reddit.subreddit(subreddit).hot(limit=100):
                subredditcheck = True
                if any(i in submission.url for i in ['gfycat', '.gifv', '.gif', '.jpg', '.png', '.jpeg', '.mp4']):
                    if submission.over_18 and nsfw_counter < 20:
                        nsfw_counter += 1
                    if nsfw_counter == 20:
                        r = random.randint(0, len(naughty_response)-1)
                        return await ctx.send(f"{naughty_response[r]}")
                    if not submission.over_18:
                        up = int(submission.score)
                        down = int(int(submission.score)*(1-int(submission.upvote_ratio)))
                        if up == down:
                            outcome = f":arrow_up:{up}"
                        else:
                            outcome = f":arrow_up:{up} :arrow_down:{down}"
                        abstract.update({f"```{submission.title}```{outcome}": submission.url})
            title, url = random.choice(list(abstract.items()))

            await ctx.send(f"{title}")
            await ctx.send(url)
        except:
            if subredditcheck == False:
                await ctx.send(f"`The following subreddit doesn't exist:` ```{subreddit}```")
            elif subredditcheck == True:
                if nsfw_counter > 5:
                    r = random.randint(0, len(naughty_response)-1)
                    await ctx.send(f"{naughty_response[r]}")
                else:
                    await ctx.send(f"`No image posts found in the following subreddit:` ```{subreddit}```")

    @commands.command(aliases=["s", "simpify"])
    @commands.has_role("HOMIES")
    @commands.cooldown(rate=1, per=2.0)
    async def simp(self, ctx, user: discord.Member = None, *, text: str  = '+1'):
        """ Simp Rating """
        simpDict = load("data/simps.json")
        time_stamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        if not user:
            return await ctx.send("Can't simp a non-user.")
        user = user.name
        if user not in simpDict['users']:
            simpDict['users'].update({user: {'rating': 0, 'comments': [], 'nicks': []}})
        rater = ctx.author.name
        if rater == user:
            return await ctx.send("Can't simp yourself.")
        else:
            if any(i in text for i in ['+1', 'add', 'plus']):
                simpDict['users'][user]['rating'] += 1
                simpDict['raters'].update({rater: {user: time_stamp}})
                write(simpDict, 'data/simps.json')
                simpSign = simpPlus
                simpColor = "18","142","240"
                simpText = f"Increased by 1 for {user}"
            elif any(i in text for i in ['-1', 'deduct', 'remove']):
                simpDict['users'][user]['rating'] -= 1
                simpDict['raters'].update({rater: {user: time_stamp}})
                write(simpDict, 'data/simps.json')
                simpSign = simpMinus
                simpColor = "240","57","18"
                simpText = f"Decreased by 1 for {user}"
            r,g,b = simpColor
            embed = discord.Embed(color=discord.Color.from_rgb(int(r),int(g),int(b)))
            embed.set_author(name="Simp - O - Meter", icon_url=simpImage)
            embed.set_footer(text=simpText, icon_url=simpSign)
            return await ctx.send(embed=embed)

    @commands.command(aliases=["unsimp","nosimp"])
    @commands.has_role("HOMIES")
    @commands.cooldown(rate=1, per=2.0)
    async def desimp(self, ctx, user: discord.Member = None, *, text: str  = '-1'):
        """ UnSimping """
        await self.simp(ctx, user=user, text=text)

    @commands.command(aliases=["sr", "SR","simpness", "howsimp", "howsimpis", "howmuchsimp"])
    @commands.has_role("HOMIES")
    @commands.cooldown(rate=1, per=2.0)
    async def simpreport(self, ctx, user: discord.Member = None):
        """ Simp Report """
        simpDict = load("data/simps.json")
        if not user:
            user = ctx.author.name
            if user in simpDict['users']:
                rating = simpDict['users'][user]['rating']
                simpText = f"{user} is about {rating}x a simp."
            else:
                return await ctx.send("Can't detect simpness of a non-user.")
        else:
            user = user.name
            if user in simpDict['users']:
                rating = simpDict['users'][user]['rating']
                simpText = f"{user} is about {rating}x a simp."
        embed = discord.Embed(color=discord.Color.from_hsv(rating, .6, .6))
        embed.set_author(name="Simp - O - Meter", icon_url=simpImage)
        embed.set_footer(text=simpText)
        return await ctx.send(embed=embed)



    @commands.command(aliases=["tts"])
    @commands.has_role("HOMIES")
    @commands.cooldown(rate=1, per=2.0)
    async def say(self, ctx, *, text: str):
        """ Text-To-Speech """
        try:
            channel = ctx.author.voice.channel
            author = ctx.author.name
            time_stamp = datetime.now().strftime("%m-%d-%Y%H:%M:%S")
        except:
            return await ctx.send("You're not here, broskie.")
        guild = ctx.guild
        vc: discord.VoiceClient = discord.utils.get(self.bot.voice_clients, guild=guild)

        if channel != None and vc == None:
            vc = await discord.VoiceChannel.connect(channel)
        if vc.is_playing():
            vc.stop()
        filepath = f'data/sounds/{author}{time_stamp}.mp3'
        tts = gTTS(text)
        tts.save(filepath)
        vc.play(discord.FFmpegPCMAudio(filepath), after=print('Phrase played.'))
        vc.source = discord.PCMVolumeTransformer(vc.source, volume=.50)



def setup(bot):
    bot.add_cog(BmBros_Commands(bot))
