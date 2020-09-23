import random
import discord
import urllib
import secrets
import asyncio
import aiohttp
import re
import praw

from io import BytesIO
from discord.ext import commands
from utils import lists, permissions, http, default, argparser
from requests import Session


session = Session()
reddit = praw.Reddit(client_id="eF4i6KOndUjY2A",
     client_secret="S7UrsF_2ZoMMvmvyoE22Ulq_-c4",	
     user_agent="BmBro"
)

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
        abstract = []
        try:
            for submission in reddit.subreddit(subreddit).hot(limit=100):
                if any(i in submission.url for i in ['gfycat', '.gifv', '.gif', '.jpg', '.png', '.jpeg']) and not submission.over_18:
                    abstract.append(submission.url)
            index = random.randint(0, len(abstract))
            await ctx.send(abstract[index])
        except:
            await ctx.send(f"`The following subreddit doesn't exist:` ```{subreddit}```")

def setup(bot):
    bot.add_cog(BmBros_Commands(bot))
