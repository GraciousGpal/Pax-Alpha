# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from discord.ext import commands
from prettytable import PrettyTable

from modules import is_admin


class Mods:

    def __init__(self, bot):
        self.bot = bot
        self.modname = __name__
        self.Description = "Contains the Basic Commands for Managing Modules."

    @commands.command(pass_context=True)
    async def catalog(self, ctx, modulename=None):
        """
        Shows the available modules for your server!
        """
        x = PrettyTable()

        temp = self.bot.loaded
        installed = [x for x in self.bot.master[str(ctx.guild.id)]["modules"] if
                     self.bot.master[str(ctx.guild.id)]["modules"][x] is True]
        if modulename is None:
            for modules in list(set(temp) - set(installed)):
                if len(list(set(temp) - set(installed))) == 1:
                    x.field_names = ["Description"]
                    x.add_row(["No Modules left to install !..pls help me make some.."])
                if modules == "Mods":
                    pass
                else:
                    try:
                        x.field_names = ["Names", "Description"]
                        var = self.bot.get_cog(modules)
                        x.add_row([str(modules), str(var.Description)])
                    except AttributeError:
                        pass
        elif modulename in [f for f in temp]:
            x.title = ("Commands in " + str(modulename))
            x.field_names = ["Commands", "Description"]
            for command in self.bot.commands:
                if command.cog_name == modulename:
                    x.add_row([str(command.name), str(command.help)])

        await ctx.message.channel.send(
            "\n" + "```" + str(x) + "\n For inDepth detail type +help <modulename> ```" + "")

    @commands.command(pass_context=True, description="Displays the Installed Mods!")
    async def installed(self, ctx):
        """
        Shows the currently Installed Modules on this Server.
        """
        temp = []
        installed = [x for x in self.bot.master[str(ctx.guild.id)]["modules"] if
                     self.bot.master[str(ctx.guild.id)]["modules"][x] is True]
        x = PrettyTable()
        for name in installed:
            x.field_names = ["Names", "Description"]
            if name == "Mods":
                pass
            else:
                x.add_row([str(name),
                           self.bot.get_cog(name).Description if self.bot.get_cog(name) is not None else None])
                temp.append(name)

        if len(temp) == 0:
            x.add_row(
                ["", " You Dont Have Anything Installed! check the catalog and install some Mods!"])

        await ctx.message.channel.send("\n" + "```" + str(x) + "```" + "")

    @commands.command(pass_context=True, description="Installs the Specified Mod")
    @is_admin()
    async def install(self, ctx, name):
        """
        Install Modules for the server from the catalog.
        """
        if name in self.bot.cogs:
            tempdict = self.bot.master[str(ctx.guild.id)]
            tempdict["modules"][name] = True
            if name == "logs":
                pass
            else:
                await ctx.message.channel.send("\n" + "```" + "{} Installed!".format(name) + "```" + "")
        else:
            await ctx.message.channel.send(
                "\n" + "```" + "{} Not Found in The Central Core..maybe write it urself ?!".format(name) + "```" + "")

    @commands.command(pass_context=True, description="Uninstalls the Specified Mod")
    @is_admin()
    async def uninstall(self, ctx, name):
        """
        Uninstall Modules from the server.
        """
        if name in self.bot.cogs:
            tempdict = self.bot.master[str(ctx.guild.id)]
            tempdict["modules"][name] = False
            await ctx.message.channel.send("\n" + "```" + "{} Uninstalled!".format(name) + "```" + "")
        else:
            await ctx.message.channel.send(
                "\n" + "```" + "{} Not Found , No Action Performed!.".format(name) + "```" + "")

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension_name: str):
        """
        Loads an extension.
        """
        try:
            self.bot.load_extension(extension_name)
            await ctx.message.channel.send("Module [{}] Loaded".format(extension_name))
        except (AttributeError, ImportError) as e:
            await ctx.message.channel.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension_name: str):
        """
        Unloads an extension.
        """
        self.bot.unload_extension(extension_name)
        await ctx.message.channel.send("Module [{}] Unloaded!.".format(extension_name))


def setup(bot):
    bot.add_cog(Mods(bot))
