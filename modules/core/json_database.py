import codecs
import json
import sys
import os


def js_r(filename):
    with open(filename, encoding='utf-8') as fh:
        return json.load(fh)


def js_w(filename, data):
    with codecs.open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, default=str)


class guildModel:

    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild

    def create(self):
        guild_id = str(self.guild.id)
        # Initialize frame
        self.bot.master[guild_id] = {
            "roles": {}, "members": {}, "modules": {}, "storage": {}}

        # populate frame with member data
        for member in self.guild.members:
            member_id = str(member.id)
            try:
                var = self.bot.master[guild_id]["members"][member_id]
            except KeyError:
                self.bot.master[guild_id]["members"][member_id] = {
                    "name": member.name, "moolah": 0, "karma": 0}

        # populate frame with role data
        for role in self.guild.roles:
            try:
                var = self.bot.master[guild_id]["roles"][role.id]
            except KeyError:
                self.bot.master[guild_id]["roles"][role.id] = 0

        # populate frame with Global member data
        for member in self.guild.members:
            member_id = str(member.id)
            try:
                var2 = self.bot.master["global"]
            except KeyError:
                self.bot.master["global"] = {}
            try:
                var2 = self.bot.master["global"][member_id]
            except KeyError:

                var2 = self.bot.master["global"][member_id] = {
                    "name": member.name, "moolah": 0}


class transaction:

    def __init__(self, bot, usr=None):
        self.bot = bot
        self.usr = usr
        self.transaction = 0

    def add(self, trans=None, globe=False):
        self.transaction = self.tran_check(trans)
        if globe == False:
            self.bot.master[str(self.usr.guild.id)]["members"][
                str(self.usr.id)]["moolah"] += self.transaction
        else:
            self.bot.master["global"][str(self.usr.id)][
                "moolah"] += self.transaction
        self.negative_check()

    def remove(self, trans=None, globe=False):
        self.transaction = self.tran_check(trans)
        if globe == False:
            balance = self.bot.master[str(self.usr.guild.id)]["members"][
                str(self.usr.id)]["moolah"]
            if self.hasenough(balance):
                self.bot.master[str(self.usr.guild.id)]["members"][
                    str(self.usr.id)]["moolah"] -= self.transaction
        else:
            balance = self.bot.master["global"][self.usr.id]["moolah"]
            if self.hasenough(balance):
                self.bot.master["global"][self.usr.id][
                    "moolah"] -= self.transaction

        self.negative_check()

    def hasenough(self, amount):
        balance = self.bot.master[str(self.usr.guild.id)]["members"][
            str(self.usr.id)]["moolah"]
        if balance < amount:
            raise InsufficientFunds(
                "{} in Balance, transaction {}".format(balance, amount))
        else:
            return True

    def tran_check(self, trans):
        self.transaction = abs(trans) if type(trans) is int else int(trans)
        if self.transaction > 2147483647:
            raise transactionOverloaded(
                "{} is over the transaction limit.".format(self.transaction))
        return self.transaction

    def negative_check(self):
        if self.bot.master[str(self.usr.guild.id)]["members"][str(self.usr.id)]["moolah"] < 0:
            self.bot.master[str(self.usr.guild.id)]["members"][
                str(self.usr.id)]["moolah"] = 0


class InsufficientFunds(Exception):
    pass


class transactionOverloaded(Exception):
    pass


class fakeuser:

    def __init__(self):
        self.id = "197766036072693760"
        self.guild = fakeguild()


class fakeguild:

    def __init__(self):
        self.id = "205438531429072897"


if __name__ == "__main__":
    import discord
    from modules import search
    from discord.ext import commands

    class MyClient(commands.Bot):
        async def on_ready(self):
            self.master = {}
            print('Logged on as {0}!'.format(self.user))
            guildModel(bot, bot.guilds[0]).create()
            print(bot.master)

    bot = MyClient(command_prefix=commands.when_mentioned_or(
        "+"))

    @bot.command()
    async def test(ctx, message):
        print("Got here")
        user = await search(ctx, message)
        await ctx.send(user)
    bot.run(os.environ['DISCORDAPI'],
            bot=True, reconnect=True)
