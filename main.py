import asyncio
import datetime
import logging
import os
import traceback

import discord
from discord.ext import commands

from modules import js_r, js_w, guildModel, usernotFound


class Consolelogging(object):
    """
    Creates Loggers to log the code and redirect it to log file and std.out
    """

    def __init__(self):
        if not os.path.exists("data/logs"):
            os.makedirs("data/logs")
        initializedtime = datetime.datetime.now()
        tim_e = "[" + str(initializedtime)[0:16].replace(":",
                                                         "-").replace(" ", "][") + "]"
        # set up logging to file
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='data/logs/Console' + tim_e + '.log',
                            filemode='w')
        # define a Handler which writes INFO messages or higher to the
        # sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter(
            '%(asctime)s %(name)-20s %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)
        # Now, we can log to the root logger, or any other logger. First the
        # root...


datalog = Consolelogging()
logging.info("Running pre-boot checks...")
logging.info("Checking Imports...")

# Secondary Imports
try:
    from setuptools.command import easy_install
    import json
    import codecs

    logging.info('Import check Complete')
except ImportError as e:
    package = str(e).split("'")[1]
    logging.error(" Error ! : " + package + " is not installed !..Installing ")
    easy_install.main([package])
    logging.info("RESTART the script please..")


def filecheck(path):
    if not os.path.exists(path):
        open(path, "w+").close()
    # Core File Check
    filechecklist = ["data/logs", "modules",
                     "data/database.json", "settings.json"]
    for files in filechecklist:
        if "." in files:
            if not os.path.exists(files):
                open(files, "w+").close()
        else:
            if not os.path.exists(files):
                os.makedirs(files)


# Runtime File Checks
logFile = ""
logging.info("Checking File systems...")
try:
    logFile = 'data/logs/' + \
        str(datetime.datetime.now()).split(".")[
            0].replace(" ", "_").replace(":", "")
    filecheck(logFile)
    logging.info('File systems check Complete')
    logging.info("BOOTING.......")
except Exception as e:
    logging.error(e)
    logging.error("File System Check failed .. proceed with cation")


def checksettings(self):
    try:
        self.Settings = js_r("settings.json")
    except json.decoder.JSONDecodeError:
        logging.error("Default settings empty or corrupted!...Overwriting..")
        defaultsettings = {
            "owner": 138684247853498369, "default_storage": True}
        js_w("settings.json", defaultsettings)
        self.Settings = js_r("settings.json")


# Main Bot Class
class MyClient(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ***** MASTER RECORD *****
        self.master = {}
        # Stores all the Configuration data
        self.Settings = {}
        checksettings(self)
        self.remove_command('clear')
        # Folder check variables
        self.path_to_watch = "modules"
        # Scans the Folder for Files
        self.before = dict([(f, None) for f in os.listdir(self.path_to_watch)])
        self.foldercheck = True
        self.loaded = []  # Lists loaded modules
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())
        self.bg_data = self.loop.create_task(self.databaseStore())

    async def on_ready(self):

        # Initial module Loading..
        plist = [f for f in self.before if ".py" in f]
        if '__init__.py' in plist:
            plist.remove("__init__.py")
        [load_mods(self.path_to_watch + "." + f.replace(".py", ""), self)
         for f in plist]

        # ********************* default DATABASE LOADING ..********************
        if self.Settings["default_storage"]:
            try:
                self.master = js_r('data/database.json')
            except json.decoder.JSONDecodeError:
                logging.error(
                    "Default database empty or corrupted!...Overwriting..")
                for guild in bot.guilds:
                    guildModel(bot, guild).create()
                js_w("data/database.json", self.master)

        # Changes our bots Playing Status. type=1(streaming) for a standard
        # game
        # await bot.change_presence(
        # game=discord.Game(name='Playing The Game of Life', type=1,
        # url='https://twitch.tv/darkprotege'))
        logging.info("______________________________________________")
        logging.info(f'Logged in as: {bot.user.name} - {bot.user.id}')
        logging.info(f"Framework Version: {discord.__version__}")
        logging.info("______________________________________________")
        logging.info(f'Successfully logged in and booted...!')
        await self.change_presence(game=discord.Game(name="-help to get help!"))

    async def on_member_join(self, member):
        tmpdict = self.master[str(member.guild.id)]
        try:
            money = tmpdict["members"][str(member.id)]["moolah"]
            karma = tmpdict["members"][str(member.id)]["karma"]
        except Exception as e:
            money, karma = None, None
            logging.error(e)
        tmpdict["members"][str(member.id)] = {"moolah": 0 if money is None else money,
                                              "karma": 0 if karma is None else karma}

    async def on_member_update(self, before, after):
        tmpdict = self.master[str(after.guild.id)]
        try:
            tmpdict["members"][str(after.id)]["name"] = after.name
        except KeyError:
            tmpdict["members"][str(after.id)] = {
                "name": after.name, "moolah": 0, "karma": 0}
        pass

    async def on_guild_join(self, guild):
        guildModel(self, guild).create()
        logging.info("{} Server as joined the conquest!".format(guild.name))

    async def on_command_error(self, ctx, error):
        if "The global check functions for command" in str(error):
            await ctx.send(
                "```Python\n Install {} package to use this command ! \n Request your server admin to install this module.```".format(
                    ctx.command.cog_name))
        else:
            await ctx.message.channel.send("```" + str(error) + "```")

    async def my_background_task(self):
        await self.wait_until_ready()

        # Continuous Folder Check Loading/Unloading..
        while self.foldercheck:
            await asyncio.sleep(5)  # task runs every 10 seconds
            after = dict([(f, None) for f in os.listdir(self.path_to_watch)])
            added = [f for f in after if f not in self.before]
            removed = [f for f in self.before if f not in after]
            """if added:
                logging.info("Added: ", ", ".join(added))"""
            [bot.unload_extension(
                self.path_to_watch + "." + f.replace(".py", "")) for f in removed if ".py" in f]
            if removed:
                logging.info("Forcefully Removed & Unloaded : " + str(removed))
            [load_mods(self.path_to_watch + "." + f.replace(".py", ""), self)
             for f in added if ".py" in f]
            self.before = after

    async def databaseStore(self):
        await self.wait_until_ready()
        if self.Settings["default_storage"]:
            while True:
                await asyncio.sleep(30)
                logging.debug("Routine : Saving Database..")
                js_w("data/database.json", bot.master)
        else:
            pass


def load_mods(extension: str, self):
    try:
        bot.load_extension(extension)
        logging.info("[{}] Loaded!.".format(extension))
        self.loaded = [f for f in self.cogs]
        return [True, None]
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        logging.error('Failed to load extension {}\n{}'.format(extension, exc))
        return [False, e]


# Declaring Client & command prefixes/descriptions..
bot = MyClient(command_prefix=commands.when_mentioned_or(
    "-"), description='Get Some when you need it!')


@bot.check
def modulesync(ctx):
    if ctx.command.cog_name is "Mods":
        return True
    try:
        boolvar = bot.master[str(ctx.guild.id)]["modules"][
            ctx.command.cog_name]
    except KeyError as e:
        boolvar = None
        # logging.error(e)
    if ctx.command.cog_name == None:
        return True
    else:
        return True if boolvar == True else False

bot.run(os.environ['DISCORDAPI'],
        bot=True, reconnect=True)
