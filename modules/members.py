import json
import random

import discord
from discord.ext import commands

from modules import search


class members:

    def __init__(self, bot):
        self.bot = bot
        self.modname = __name__
        self.Description = "General member commands eg. joindate"

    @commands.command(pass_context=True, description="Displays the User's/Target's Information")
    async def userinfo(self, ctx, *, member=None):
        """
        Gets User Info
        """
        if member is None:
            memberz = ctx.message.author
        else:
            memberz = await search(ctx, member)

        if memberz is not None:
            embed = discord.Embed(title="User Information :", color=(memberz.top_role.color))
            embed.set_thumbnail(url=memberz.avatar_url)
            embed.add_field(name="Name", value=memberz.name, inline=True)
            embed.add_field(name="Nick", value=memberz.nick, inline=True)
            embed.add_field(name="ID", value=memberz.id, inline=True)
            try:
                moolah = self.bot.master[str(ctx.guild.id)]["members"][str(memberz.id)]["moolah"]
                embed.add_field(name="Moolah", value='**' + str(moolah) + "**", inline=True)
            except:
                embed.add_field(name="Moolah", value='**' + str("Error") + "**", inline=True)
            embed.set_footer(text=memberz.joined_at)
            await ctx.send(embed=embed)
        else:
            await ctx.send("**{}** not found! , Contact your bruh .".format(member))

    @commands.command(name='perms', aliases=['perms_for', 'permissions'])
    @commands.guild_only()
    async def check_permissions(self, ctx, *, member):
        """A simple command which checks a members Guild Permissions.
        If member is not provided, the author will be checked."""
        member = await search(ctx, member)
        if not member:
            member = ctx.author

        # Here we check if the value of each permission is True.
        perms = '\n'.join(
            perm for perm, value in member.guild_permissions if value)

        # And to make it look nice, we wrap it in an Embed.
        embed = discord.Embed(title='Permissions for:',
                              description=ctx.guild.name, colour=member.colour)
        embed.set_author(icon_url=member.avatar_url, name=str(member))

        # \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
        embed.add_field(name='\uFEFF', value=perms)

        await ctx.send(content=None, embed=embed)
        # Thanks to Gio for the Command.

    @commands.command(aliases=['compli'])
    async def compliment(self, ctx, member):
        '''
        Brighten Up Someone's day by complimenting them!
        '''
        self.checklist2 = []
        user = await search(ctx, member)
        with open('data/Scraped-Insults-Compliments/compliments.txt', encoding='utf-8', mode="r") as f:
            data = f.readlines()
        if user.bot:
            with open('data/Scraped-Insults-Compliments/compliments-Robot.txt', encoding='utf-8', mode="r") as f:
                data = f.readlines()
        data = [x.strip('\n') for x in data]
        data = filter(lambda x: x not in self.checklist2, data)
        data = list(data)
        x1 = user.id
        msg = ' '
        if user != None:
            if user.name == "Pax":
                user = ctx.message.author
                msg = "Awww How Sweet!,You Brighten my Day.Alas...if only I could feel.."
                await self.bot.say(user.mention + msg)
            else:
                # await client.delete_message(ctx.message)
                xx = random.choice(data)
                await ctx.send(user.mention + msg + xx)
                self.checklist2.append(xx)
        else:
            # await self.bot.delete_message(ctx.message)
            xx = random.choice(data)
            await ctx.send(ctx.message.author.mention + msg + xx)
            self.checklist2.append(xx)
        if len(data) == len(self.checklist2):
            self.checklist2 = []

    @commands.command()
    async def insult(self, ctx, user):
        '''
        Wasn't stating the obvious enough for your dull mind?
        '''
        self.checklist1 = []
        user = await search(ctx, user)

        def _read_json():
            with open('data/Scraped-Insults-Compliments/insults.json', encoding='utf-8', mode="r") as f:
                data = json.load(f)
            return data

        insults = _read_json()
        insults = filter(lambda x: x not in self.checklist1, insults)
        insults = list(insults)
        msg = ' '
        if user is not None:
            if user.name == "Pax":
                user = ctx.message.author
                msg = " How original. No one else had thought of trying to get the bot to insult itself. I applaud your creativity. Yawn. Perhaps this is why you don't have friends. You don't add anything new to any conversation. You are more of a bot than me, predictable answers, and absolutely dull to have an actual conversation with."
                await ctx.send(user.mention + msg)
            else:
                # await self.bot.delete_message(ctx.message)
                xx = random.choice(insults)
                await ctx.send(user.mention + msg + xx)
                self.checklist1.append(xx)
        else:
            # await self.bot.delete_message(ctx.message)
            xx = random.choice(insults)
            await ctx.send(ctx.message.author.mention + msg + xx)
            self.checklist1.append(xx)
        if len(insults) == len(self.checklist1):
            self.checklist1 = []


def setup(bot):
    bot.add_cog(members(bot))
