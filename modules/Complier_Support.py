import json
import os

import discord
import requests
from discord.ext import commands


class Compiler:
    def __init__(self, bot):
        self.bot = bot
        self.modname = __name__
        self.Description = "Compiles almost all languages.."
        self.payload = {}

    @commands.command()
    async def compile(self, ctx, language, *, arg):
        """
        Compiles lines of Code e.g. .compile python3 "print('Neil is a bitch')"
        :param ctx:
        :param language:
        :param script:
        :return:
        """
        self.payload["clientId"] = os.environ['compiler_clientId']
        self.payload["clientSecret"] = os.environ['compiler_clientSecret']
        self.payload["language"] = language
        self.payload["versionIndex"] = "0"
        self.payload["script"] = "".join(arg).replace("```", "")

        r = requests.post("https://api.jdoodle.com/v1/execute", data=json.dumps(self.payload),
                          headers={"Content-Type": "application/json; charset=UTF-8"})
        response = r.json()
        try:
            await ctx.send("```Compiler Output :\n" + str(response["output"]) + "```")
        except Exception as e:
            print(e)

        if language == "help":
            await ctx.send(
                '```Usage Example: .compile python3 print(#Hello#)\n Using BackTicks in "print(#Hello#)" will make ur code much more readable in discord```'.replace(
                    "#", "'"), file=discord.File("data/compilers/Supported_Languages_List.html"))


def setup(bot):
    bot.add_cog(Compiler(bot))
