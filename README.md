

# Pax - Alpha

Pax Bot is something that was born from the needs of a small discord community.  
Initially All it did was display welcoming text, It has since evolved to something much greater.  
Pax is built around the Idea of Modularity :  
 * The Host server has all the plugins avaliable and it can freely let its users add to its repositoire .  
 * The clients can then choose what functionality they require.   



# Creating your Own Modules!

You can easily add your creation to the bot with a simple few steps.

 * Main part of the code needs to be contained in a class.
 * Must contain the modulename and Description in the class initialization.
 * The end of the file must contain a setup function.

**Example:**
```python
class members():
    def __init__(self, bot):
        self.bot = bot
        self.Description = "Contains commands for Users"

    @commands.command()
    async def joined(self, member : discord.Member):
        """Displays the date when the user joined the server."""
        await self.bot.say('{0.name} joined at {0.joined_at}'.format(member))

def setup(bot):
    bot.add_cog(members(bot))
```
Note that Listeners/Events need:
```python
    Documentation coming soon
```
It stops them from executing without installation.
