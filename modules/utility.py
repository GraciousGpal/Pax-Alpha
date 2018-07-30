from discord.ext import commands

from modules import search, is_admin

ids = None


class Utility:

    def __init__(self, bot):
        self.bot = bot
        self.modname = __name__
        self.Description = "Contains a set of useful Server utilities."

    @commands.command(pass_context=True)
    async def clear(self, ctx, messages=0, member=None):
        '''
        Clears a number of messages or a specific persons message
        '''
        if messages == 0 and member is None:
            await ctx.send("```No Input ! Example usage: .clear <e.g 10> <member or leave as blank> ```")
        if member is None and messages != 0 and ctx.author.guild_permissions.manage_messages:
            number = int(messages)  # Converting the amount of messages to delete to an integer
            await ctx.channel.purge(limit=number)
        if member is not None and messages is not None and ctx.author.guild_permissions.manage_messages:
            number = int(messages)
            mem = await search(ctx, member)
            if mem is not None:
                self.ids = mem.id
                await ctx.channel.purge(limit=number, check=self.m_check)
            else:
                await ctx.send("{} not Found!".format(member))

    def m_check(self, m):
        if m.author.id == self.ids:
            return True
        else:
            return False

    @commands.command(pass_context=True, description="The Bot Repeats what you say like your own pet parrot!")
    @is_admin()
    async def echo(self, ctx, *, echo: str):
        """
        The Bot follows your lead!
        """
        if ctx.message.author.guild_permissions.administrator:
            await ctx.message.delete()
            await ctx.send(echo)
        else:
            await ctx.send("Sorry Bro , you dont have permissions for this !")


def setup(bot):
    bot.add_cog(Utility(bot))
