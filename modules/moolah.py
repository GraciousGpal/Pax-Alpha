import asyncio
import datetime
import logging
import traceback
from datetime import date
from difflib import get_close_matches

import discord
from discord.ext import commands
from prettytable import PrettyTable

from modules import search, is_admin, transaction, InsufficientFunds


class moolah_economy:
    """
    The Place to be for all your Moolah Needs!
    """

    def __init__(self, bot):
        self.bot = bot
        self.Description = "Moolah Runs the World!, Adds Economy to the Server."
        self.tax = self.bot.loop.create_task(self.taxing())
        self.provision = self.bot.loop.create_task(self.mining())
        self.datacheck = self.bot.loop.create_task(self.datacheck())

    @commands.command()
    async def topdog(self, ctx):
        """
        Shows the Top 10 Holders of Moolah and your Position
        :param ctx:
        :return:
        """
        dictonary = self.bot.master[str(ctx.guild.id)]["members"]
        lista = [f for f in dictonary]
        topdog = sorted(lista, key=lambda x: (
            dictonary[str(x)]['moolah']), reverse=True)
        value = topdog.index(str(ctx.message.author.id))
        listb = [topdog[value + f] for f in [-2, -1, 0, 1, 2]]
        yourposition = [(f, dictonary[f]["name"], dictonary[
                         f]["moolah"]) for f in listb]
        x = PrettyTable()
        x.field_names = ["Position", "Names", "Moolah"]
        for item in range(0, (10 if len(lista) >= 10 else len(lista))):
            if item == 0:
                x.add_row(["TOPDOG", dictonary[topdog[item]][
                          "name"], dictonary[topdog[item]]["moolah"]])
            if dictonary[topdog[item]]["name"] == ctx.message.author.name and item != 0:
                x.add_row(
                    [item + 1, "->>" + dictonary[topdog[item]]["name"] + "<<-", dictonary[topdog[item]]["moolah"]])
            elif item != 0:
                x.add_row([item + 1, dictonary[topdog[item]]
                           ["name"], dictonary[topdog[item]]["moolah"]])
        if str(ctx.message.author.id) in topdog[:10]:
            pass
        else:
            x.add_row(["..........", "..........", ".........."])
            for xx, y, z in zip([topdog.index(f) for f in listb], [f[1] for f in yourposition],
                                [f[2] for f in yourposition]):
                if y == ctx.message.author.name:
                    x.add_row([str(xx), "->>" + y + "<<-", str(z)])
                else:
                    x.add_row([xx, y, z])

        await ctx.send(":moneybag:  __***Top Ten Personnalle with Moolah***__ :moneybag: \n```" + str(
            x) + "\nEstimated amount of moolah left in the Mines: {}```".format(
            "∞" if str(ctx.guild.id) == '205438531429072897' else (
                self.bot.master[str(ctx.guild.id)]["storage"]["mine"] if self.bot.master[str(ctx.guild.id)]["storage"][
                    "mine"] >= 100 else "Mine Exhausted")))

    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def sellrole(self, ctx, role=None, price=None):
        """
        Sets a Role for Sale! [Admin Use Only]
        :param ctx:
        :param role:
        :param price:
        :return:
        """
        if role is not None and price is not None:
            dictonary = self.bot.master[str(ctx.guild.id)]["roles"]
            match = get_close_matches(
                role, [dictonary[f]["name"] for f in [f for f in dictonary]])[0]
            Role = discord.utils.get(ctx.message.guild.roles, name=match)
            dictonary[str(Role.id)]["sale"] = True
            dictonary[str(Role.id)]["price"] = abs(int(price))
            await ctx.send("{} Set for sale for {} Moolah".format(Role.name, dictonary[str(Role.id)]["price"]))
        elif role is None:
            await ctx.send("Enter a Role to sell e.g .sellrole Knight 100")
        elif price is None:
            await ctx.send("Enter a price for Role [{}] e.g .sellrole Knight 100".format(role))
        elif role is None and price is None:
            await ctx.send("Enter a price and Role [{}] e.g .sellrole Knight 100".format(role))

    @commands.command()
    @commands.guild_only()
    async def buyrole(self, ctx, *, role=None):
        """
        Buys the specified Role! just type .buyrole to display all avaliable roles to buy
        e.g. .buyrole to display role avaliable to buy
        :param ctx:
        :param role:
        :return:
        """
        if role is None:
            temp = []
            dictonary = self.bot.master[str(ctx.guild.id)]["roles"]
            forsale = [x for x in dictonary if dictonary[x] > 0]
            if len(forsale) == 0:
                x = "No Roles available for purchase"
            else:
                for x in forsale:
                    temp.append(
                        ([f.name for f in ctx.guild.roles if str(f.id) == str(x)][0], dictonary[x]))
                x = PrettyTable()
                x.field_names = ["Role Name", "Moolah"]
                for xx in temp:
                    x.add_row([xx[0], xx[1]])
            await ctx.send("```" + str(x) + "```")
        else:
            dictonary = self.bot.master[str(ctx.guild.id)]
            dictonaryroles = dictonary["roles"]
            tempm = get_close_matches(
                role, [dictonaryroles[f]["name"] for f in [f for f in dictonaryroles]])
            match = None if tempm is None else [0]
            role = discord.utils.get(ctx.message.guild.roles, name=match)
            try:
                if role is not None and dictonaryroles[str(role.id)] > 0:
                    if int(dictonary["members"][str(ctx.message.author.id)]["moolah"]) >= int(
                            dictonaryroles[str(role.id)]):
                        dictonary["members"][str(ctx.message.author.id)]["moolah"] -= abs(
                            int(dictonaryroles[str(role.id)]))
                        await ctx.message.author.add_roles(role,
                                                           reason="Purchased Time:{}".format(datetime.datetime.now()))
                        await ctx.send("{} Has been Purchased.".format(role))
                    else:
                        await ctx.send("You do not Have enough Moolah for this Purchase [{} Needed]".format(abs(
                            dictonaryroles[str(role.id)] - dictonary["members"][str(ctx.message.author.id)][
                                "moolah"])))
                elif dictonaryroles[str(role.id)] == 0:
                    await ctx.send("{} isnt for sale yet..".format(role))
                elif role is None:
                    await ctx.send("{} isnt Found or Incorrect Input . try: e.g. .buyrole Knight".format(role))
            except Exception as e:
                logging.error(e)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def add(self, ctx, user, amount):
        """
        Adds Moolah to the user
        :param ctx:
        :param user:
        :param amount:
        :return:
        """
        user = await search(ctx, user)
        self.bot.master[str(ctx.guild.id)]["members"][str(user.id)][
            "moolah"] += abs(int(amount))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def remove(self, ctx, user, amount):
        """
        Removes Moolah from the user
        :param ctx:
        :param user:
        :param amount:
        :return:
        """
        user = await search(ctx, user)
        self.bot.master[str(ctx.guild.id)]["members"][str(user.id)][
            "moolah"] -= abs(int(amount))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def set(self, ctx, user, amount):
        """
        Sets users moolah to a specified amount
        :param ctx:
        :param user:
        :param amount:
        :return:
        """
        user = await search(ctx, user)
        self.bot.master[str(ctx.guild.id)]["members"][str(user.id)][
            "moolah"] = abs(int(amount))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reset(self, ctx, serverv=None):
        """
        Resets the Moolah Bank on the server.
        :param ctx:
        :param serverv:
        :return:
        """
        try:
            for server in self.bot.guilds:
                if int(server.id) == int(serverv):
                    dictonary = self.bot.master[str(ctx.guild.id)]["members"] = {
                        str(x.id): {"name": str(x.name), "moolah": 0, "karma": 0} for x in server.members}
                    self.bot.master[str(server.id)]["storage"]["mine"] = int(
                        len(server.members) * 0.05 * 1000)
                    self.bot.master[str(server.id)]["storage"][
                        "welfare_pool"] = 1000
                    await ctx.send("```Moolah & Karma reset on {}```".format(server.name))
        except Exception as e:
            await ctx.send(
                "```Error Occurred Resetting {} Server: \n```".format(
                    (str(ctx.guild.id) if serverv is None else serverv), e))
            logging.error(e)

    async def on_message(self, message):
        amount = 2
        if "moolah_economy" in self.bot.master[str(message.guild.id)]["modules"]:
            if not "." in message.content[0:1]:
                if message.author is not None and message.author.bot is not True:
                    self.bot.master[str(message.guild.id)]["members"][str(message.author.id)]["moolah"] += abs(
                        int(amount))

    async def mining(self):
        """
        Continuous function that distributes moolah to the miners
        :return:
        """
        amount = 100
        await self.bot.wait_until_ready()

        # Loading...
        for guild in self.bot.guilds:
            try:
                var = self.bot.master[str(guild.id)]["storage"]["mine"]
            except Exception as e:
                self.bot.master[str(guild.id)]["storage"]["mine"] = int(
                    len(guild.members) * 0.05 * 1000)
                logging.error(e)
                traceback.print_exc()

        while True:
            await asyncio.sleep(1800)
            try:
                for guild in self.bot.guilds:
                    if "moolah_economy" in self.bot.master[str(guild.id)]["modules"]:
                        for channel in guild.voice_channels:
                            if len(channel.members) == 2 and True in [members for members in channel.members if
                                                                      members.bot is True]:
                                pass
                            elif (len(channel.members) > 1 and channel.id != guild.afk_channel.id) and str(guild.id) == '205438531429072897':
                                for member in channel.members:
                                    if member.bot is not True:
                                        self.bot.master[str(guild.id)]["storage"]["mine"] = await self.increment(guild,
                                                                                                                 amount,
                                                                                                                 member)
                                logging.info(
                                    "Moolah Distributed! Server: {} {}".format(guild.id, self.bot.master[str(guild.id)][
                                        "storage"]["mine"]))

                            elif len(channel.members) > 1 and channel.id != guild.afk_channel.id and \
                                    not self.bot.master[str(guild.id)]["storage"]["mine"] <= 100:

                                for member in channel.members:
                                    if member.bot is not True:
                                        self.bot.master[str(guild.id)]["storage"]["mine"] = await self.increment(guild,
                                                                                                                 amount,
                                                                                                                 member)
                                logging.info(
                                    "Moolah Distributed! Server: {} {}".format(guild.id, self.bot.master[str(guild.id)][
                                        "storage"]["mine"]))
            except Exception as e:
                logging.error(e)
                traceback.print_exc()

    async def taxing(self):
        """
        Tax is taken every monday
        :return:
        """
        await self.bot.wait_until_ready()
        await asyncio.sleep(5)

        # Data Check and Fix for Welfare Pool
        for guild in self.bot.guilds:
            try:
                x = self.bot.master[str(guild.id)]["storage"]["welfare_pool"]
            except Exception as e:
                self.bot.master[str(guild.id)]["storage"][
                    "welfare_pool"] = 1000

        # Main Tax Section
        try:
            if date.today().weekday() == 0:
                for guild in self.bot.guilds:
                    if "moolah_economy" in self.bot.master[str(guild.id)]["modules"]:
                        for member in guild.members:
                            money = int(self.bot.master[str(guild.id)][
                                        "members"][str(member.id)]["moolah"])
                            tax_payed = 0
                            try:
                                if 15000 <= money <= 25000:
                                    tax_payed = int((money - 15000) * 0.005)
                                    transaction(self.bot, member).remove(
                                        tax_payed)
                                    self.bot.master[str(guild.id)]["storage"]["welfare_pool"] = int(
                                        (money - 15000) * 0.005)
                                elif 25000 < money <= 50000:
                                    tax_payed = 50 + \
                                        int((money - 25000) * 0.015)
                                    transaction(self.bot, member).remove(
                                        tax_payed)
                                    self.bot.master[str(guild.id)]["storage"]["welfare_pool"] = 50 + int(
                                        (money - 25000) * 0.015)
                                elif 50000 < money <= 250000:
                                    tax_payed = 425 + \
                                        int((money - 50000) * 0.025)
                                    transaction(self.bot, member).remove(
                                        tax_payed)
                                    self.bot.master[str(guild.id)]["storage"]["welfare_pool"] = 425 + int(
                                        (money - 50000) * 0.025)
                                elif 250000 < money <= 500000:
                                    tax_payed = 5425 + \
                                        int((money - 250000) * 0.030)
                                    transaction(self.bot, member).remove(
                                        tax_payed)
                                    self.bot.master[str(guild.id)]["storage"]["welfare_pool"] = 5425 + int(
                                        (money - 250000) * 0.030)
                                logging.debug(
                                    "User : {} Balance:{} Tax Payed: {} ".format(member.name, money, tax_payed))
                            except InsufficientFunds:
                                logging.error(
                                    "{} is too poor to pay tax".format(member.name))
                                pass

        except Exception as e:
            logging.error(e)
            traceback.print_exc()
        await asyncio.sleep(518400)

    async def datacheck(self):
        await self.bot.wait_until_ready()
        while True:
            now = datetime.datetime.now()
            if date.today().weekday() == 4 and now.hour == 0 and now.minute == 0:
                moolah_restock = {
                    x.id: int(len(x.members) * 0.05 * 1000) for x in self.bot.guilds}
                for guild_ids in moolah_restock:
                    self.bot.master[str(guild_ids)]["storage"][
                        "mine"] = moolah_restock[guild_ids]
                logging.info(
                    "+++++++++++++++++++Moolah Mines Restocked!+++++++++++++++++++")
                for guild in self.bot.guilds:
                    if self.bot.master[str(guild.id)]["storage"]["mine"] < (int(len(guild.members) * 0.05 * 1000)):
                        self.bot.master[str(guild.id)]["storage"]["mine"] = (
                            int(len(guild.members) * 0.05 * 1000))
                await asyncio.sleep(100000)
            await asyncio.sleep(20)

    async def increment(self, guild, value, member):
        newvalue = value
        guild_mine = self.bot.master[str(guild.id)]["storage"]["mine"]
        if guild_mine >= 100:
            if member.voice.self_mute and not member.voice.self_deaf:
                newvalue = value * 0.6
            elif member.voice.self_deaf and not member.voice.self_mute:
                newvalue = value * 0.1
            elif member.voice.self_deaf and member.voice.self_mute:
                newvalue = value * 0.1
            logging.info("{} Given to {}".format(int(newvalue), member.name))
        self.bot.master[str(guild.id)]["members"][str(member.id)][
            "moolah"] += int(newvalue)
        guild_mine -= abs(int(newvalue)
                          ) if guild_mine >= 100 else (guild_mine == 0)
        return guild_mine


def setup(bot):
    bot.add_cog(moolah_economy(bot))


if __name__ == "__main__":
    print("Testing moolah.py")
