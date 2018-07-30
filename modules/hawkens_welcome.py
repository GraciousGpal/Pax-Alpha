import io
import json
import logging
import os
import textwrap
import traceback

import discord
import requests
from PIL import Image, ImageDraw, ImageFont
from modules import is_admin
from discord.ext import commands


class hawkens_welcome:
    def __init__(self, bot):
        self.bot = bot
        self.Description = "Hawken welcomes you to the server with his trademark smile"

    async def on_member_join(self, member):
        try:
            if self.bot.master[str(member.guild.id)]["modules"]["hawkens_welcome"] is True:
                await create(member)
        except KeyError:
            self.bot.master[str(member.guild.id)]["modules"]["hawkens_welcome"] = False
            pass

    @commands.command(hidden=True)
    @is_admin()
    async def preview(self, ctx):
        await create(ctx.author)


async def create(member):
    try:
        image_json = requests.get("https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US")
        image_url = json.loads(image_json.content)
        url = "https://www.bing.com" + image_url["images"][0]["url"]
        data = requests.get(url).content
        img = Image.open(io.BytesIO(data))
        user = Image.open('data/hawkens_welcome/user.png')
        img_width, img_height = img.size
        user_width1, user_height1 = user.size
        img.paste(user, (img_width - user_width1, img_height - user_height1), mask=user)

        # Message Formatting
        astr = '''Welcome to our Humble Abode.'''
        author = "- Hawkens"
        para = textwrap.wrap(astr, width=15)

        MAX_W, MAX_H = img_width, img_height
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("data/hawkens_welcome/ITCEDSCR.TTF", 160)

        current_h, pad = 200, 230

        draw.text((current_h - 2, pad), astr, font=font, fill='black')
        draw.text((current_h + 2, pad), astr, font=font, fill='white')
        draw.text((current_h, pad - 1), astr, font=font, fill='black')
        draw.text((current_h, pad + 1), astr, font=font, fill='white')
        draw.text((1350, 370 + 1), author, font=ImageFont.truetype("data/hawkens_welcome/ITCEDSCR.TTF", 60),
                  fill='white')
        img.save('data/hawkens_welcome/temp.png', format='jpeg')
        await member.guild.system_channel.send(file=discord.File('data/hawkens_welcome/temp.png'))

    except Exception as e:
        logging.error(e)
        traceback.print_exc()


def setup(bot):
    if not os.path.exists("data/hawkens_welcome"):
        os.makedirs("data/hawkens_welcome")
    fn = "data/hawkens_welcome/user.png"
    data = {}
    try:
        file = open(fn, 'r')
    except IOError:
        raise IOError
    bot.add_cog(hawkens_welcome(bot))
