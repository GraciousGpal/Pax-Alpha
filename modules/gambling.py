import asyncio
import random
from operator import ge, le, ne
from random import randint
import traceback
from discord.ext import commands

from modules import search, transaction ,usernotFound

secure_random = random.SystemRandom()


class gambling:

    def __init__(self, bot):
        self.bot = bot
        self.modname = __name__
        self.Description = "Bet away your Moolah and ruin your life or Hit the high life"
        self.betlist = []

    @commands.command()
    async def slots(self, ctx, bid):
        """
        The Slot machine, a sure way of getting nothing from something.
        Costs Moolah to Play
        :param ctx:
        :param bid:
        :return:
        """
        bid = abs(int(bid))
        blue = transaction(self.bot, ctx.author)

        if blue.hasenough(abs(int(bid))):
            blue.remove(bid)
            pool = 0
            ls = []
            ITEMS = {"CHERRY": (3, 10, "🍒"), "APPLE": (2, 4, "🍏"), "PLUM": (1.5, 2, "🍑"), "BELL":
                     (1, 1.25, "🚨"), "BOMB": (-0.5, -1, "💣")}
            item = [f for f in ITEMS]
            for x in range(0, 3):
                ls.append(item[randint(0, 4)])
            tosend = "```\n/------------------------------9\n| +--------------------------+ |\n| |       SLOT MACHINE       | |   🔴\n| +--------------------------+ |   |\n| |  ______________________  | |===+\n|   |                      |   |\n          |       |            \n|   |______________________|   |\n| |                          | |\n| +--------------------------+ |\n9------------------------------/\n```".replace(
                "9", "\\")
            sentmsg = await ctx.send(tosend)
            msg = list(tosend)
            for item, i, z in zip(ls, [220, 227, 234], [105, 179, 246]):
                msg[i] = ITEMS[item][2]
                msg = "".join(msg)
                await sentmsg.edit(content=msg)
                msg = list(msg)
                if i != 234:
                    await asyncio.sleep(0.6)
            gotStuff = False
            for item in list(set(ls)):
                no2 = (len(list(l for l in ls if item in l)) is 2)
                no3 = (len(list(l for l in ls if item in l)) is 3)
                if no2 and not no3:
                    pool += bid* ITEMS[item][0]
                    await ctx.send("You get " + str(pool))
                    blue.add(pool)
                    gotStuff = True
                elif no3:
                    pool += bid*ITEMS[item][1]
                    await ctx.send("You get " + str(pool))
                    blue.add(pool)
                    gotStuff = True
            if not gotStuff:
                await ctx.send("Alas Luck wasn't on your side")
        else:
            await ctx.send("```Insufficient Funds to use the slot machine :(```")

    @commands.command()
    async def cointoss(self, ctx, user, amount):
        '''
        Wager Your Moolah in this deadly game and rise to the top!
        '''
        amount = abs(int(amount))
        bank = ["heads", "tails"]
        option = ['heads', 'tails', 'cancel']
        author = ctx.message.author
        challenged = await search(ctx, user)
        blue = transaction(self.bot, ctx.author)
        red = transaction(self.bot, challenged)

        def check_opponent(m):
            if m.author.id == challenged.id:
                return True

        def check_author(m):
            if m.author.id == author.id:
                return True

        async def toss_coin(challenged_choice, prize_money):
            result = secure_random.choice(bank)
            await ctx.send(":drum:")
            await asyncio.sleep(3)
            await ctx.send("The Coin has Landed !.........and its " + "**" + str(result) + " ! **")
            if result == "heads" and challenged_choice == "heads":
                red.add(prize_money)
            elif result == "tails" and challenged_choice == "tails":
                red.add(prize_money)
            else:
                blue.add(prize_money)

        if not blue.hasenough(amount):
            await ctx.send("You Dont Have Enough Moolah for this wager!")

        if not red.hasenough(amount):
            await ctx.send("{} does not have enough Moolah for this wager!".format(challenged.name))

        elif (str(challenged.id) or str(author.id)) in self.betlist:
            await ctx.send("There is already a pending bet for {}".format(
                challenged.display_name if str(challenged.id) in self.betlist else str(author.id)))

        elif blue.hasenough(amount) and red.hasenough(amount):
            self.betlist.append(str(ctx.message.author.id))
            self.betlist.append(str(challenged.id))

            await ctx.send("Showdown between {} and {} for ".format(ctx.message.author.mention,
                                                                    challenged.mention) + "\n" + "Challenger Has Waged " + "**" + str(
                amount) + "**" + " Moolah")
            blue.remove(amount)
            await ctx.send("The Opponent get to pick the sides!")
            try:
                msg = await self.bot.wait_for("message", timeout=120, check=check_opponent)

            except TimeoutError:
                await ctx.send("Too much time has passed!,canceling the bet!")
                blue.add(amount)
                self.betlist.remove(str(author.id))
                self.betlist.remove(str(challenged.id))

            if msg is None:
                await ctx.send("Too much time has passed!,canceling the bet!")
                blue.add(amount)
                self.betlist.remove(str(author.id))
                self.betlist.remove(str(challenged.id))
            elif "heads" in msg.content:
                await ctx.send("{} has picked heads and {} takes tails ".format(challenged.name,
                                                                                ctx.message.author.name) + "{} has waged {}. \n **Total Pot:{}**".format(
                    challenged.name, amount, str(int(amount) + int(amount))))
                red.remove(amount)
                await toss_coin("heads", amount * 2)
                self.betlist.remove(str(author.id))
                self.betlist.remove(str(challenged.id))
            elif "tails" in msg.content:
                await ctx.send("{} has picked tails and {} takes heads ".format(challenged.name,
                                                                                ctx.message.author.name) + "{} has waged {}. \n **Total Pot:{}**".format(
                    challenged.name, amount, str(int(amount) + int(amount))))
                red.remove(amount)
                await toss_coin("tails", amount * 2)
                self.betlist.remove(str(author.id))
                self.betlist.remove(str(challenged.id))
            elif "cancel" in msg.content:
                blue.add(amount)
                await ctx.send("{} has canceled the wager!".format(challenged.name))
                self.betlist.remove(str(author.id))
                self.betlist.remove(str(challenged.id))
            elif not any(x in msg.content for x in option):
                blue.add(amount)
                self.betlist.remove(str(author.id))
                self.betlist.remove(str(challenged.id))
                await ctx.send("{}'s Bet Has Been canceled due to INVALID input!'".format(challenged.name))
        else:
            await ctx.send("Error Bet Couldn't be Placed!")
            self.betlist.remove(str(author.id))
            self.betlist.remove(str(challenged.id))

    @commands.command(pass_context=True, description="Play Highlow when your broke !")
    async def highlow(self, ctx, rounds=8):
        '''
        Lets you play High and Low - Entry Costs Only 2 Moolah
        '''
        baseamount = 2
        red = transaction(self.bot, ctx.author)
        if red.hasenough(baseamount):
            red.remove(baseamount)
            cards = range(1, 14)
            faces = {11: 'Jack', 12: 'Queen', 13: 'King', 1: 'Ace'}
            suits = ["Spades", "Hearts", "Clubs", "Diamonds"]

            comparisons = {'h': le, 'l': ge, 's': ne}
            pass_template = "```Good job! The card is the {0} of {1}.```"
            fail_template = "```Sorry, you fail. The card is the {0} of {1}.```"
            running = True
            card = random.choice(cards)
            suit = random.choice(suits)

            def check(m):
                if m.author.id == ctx.author.id:
                    return True

            while running:

                await ctx.send("```The first card is the {0} of {1}.```".format(faces.get(card, card), suit))
                next_card = random.choice(cards)
                next_suit = random.choice(suits)
                await ctx.send(
                    "Higher (H), Lower (L) or the Same (S)? " + "Current Pot: [**" + str(baseamount) + "**]")
                ui = await self.bot.wait_for('message', timeout=120, check=check)
                choices = set("hls")
                if ui.content.lower() in choices:
                    ui = ui.content.lower()
                if comparisons[ui](next_card, card):
                    await ctx.send(fail_template.format(faces.get(next_card, next_card), next_suit))
                    break
                else:
                    await ctx.send(pass_template.format(faces.get(next_card, next_card), next_suit))
                    if baseamount < 1000:
                        baseamount = baseamount + (baseamount)
                        multiplyer = 2
                    elif baseamount >= 1000 and baseamount < 2999:
                        baseamount = baseamount + (baseamount / 2)
                        multiplyer = 1.5
                    elif baseamount > 2999:
                        baseamount = baseamount + (baseamount / 4)
                        multiplyer = 1.25
                    await ctx.send(
                        "```Do you want to continue playing ? type [Y/n]. \n Current Multiplier [x{}] Current Pot [{}]```".format(
                            str(multiplyer), str(baseamount)))
                    repeat = await self.bot.wait_for('message', timeout=120, check=check)
                    repeat = repeat.content.lower()
                    if repeat != "yes" and repeat != "y":
                        running = False
                        red.add(baseamount)
                        await ctx.send("Have Fun with your Moolah! Alas for me 'tis a goodbye amigo.")
                    card = next_card
                    suit = next_suit
        else:
            await ctx.send("You dont have enough Moolah")

    @commands.command(aliases=['tictac'], pass_context=True, description="The classic game of tictactoe")
    async def tictactoe(self, ctx, user, amount=0):
        """
        Play a Fun game of Tic Tac Toe!.
        """
        # amount = abs(int(amount))
        board = "```| {0} | {1} | {2} |\n------------\n| {3} | {4} | {5} |\n------------\n| {6} | {7} | {8} |```"
        opponent = [await search(ctx, user), 'X']
        challenger = [ctx.message.author, 'O']
        red = transaction(self.bot, opponent[0])
        blue = transaction(self.bot, challenger[0])
        spaces = ['_', '_', '_', '_', '_', '_', '_', '_', '_']
        if red.hasenough(amount) and blue.hasenough(amount):
            red.remove(amount)
            blue.remove(amount)
            Board = await ctx.send(board.format(*range(0, 10)))
            #  await self.bot.say(board.format(*spaces))
            await ctx.send(("```{0} is X\n{1} is O\nX goes first```".format(opponent[0].name, challenger[0].name, )))
            current_player = opponent

            def check(m):
                if m.author.id == current_player[0].id:
                    return True

            while tictac_checkboard(spaces) == '_':
                msg = await self.bot.wait_for('message', timeout=120, check=check)
                if msg.content.isdigit():
                    move = abs(int(msg.content))
                    if move > 8:
                        await ctx.send("Move must be less than 9, there's only 9 spaces!")
                        continue
                    if spaces[move] != "_":
                        await ctx.send("Space is already taken by %s" % spaces[move])
                        continue
                    spaces[move] = current_player[1]
                    await Board.edit(content=board.format(*spaces))
                    await msg.delete()

                    if current_player == opponent:
                        current_player = challenger
                    else:
                        current_player = opponent
                elif msg.content is None:
                    await ctx.send("Too much time as passed !.The Match is canceled.")
                elif msg.content == "quit":
                    await ctx.send(
                        "Match Cancelled by {} : Invaild input! please use a number ".format(current_player[0]))
                    red.add(amount)
                    blue.add(amount)
                else:
                    await ctx.send("Invaild input! please use a number ")
            result = tictac_checkboard(spaces)
            if opponent[1] == result:
                await ctx.send("%s [%s] is the winner!" % (opponent[0].name, result))
                red.add(amount + amount)

            elif challenger[1] == result:
                await ctx.send("%s [%s] is the winner!" % (challenger[0].name, result))
                blue.add(amount + amount)
            elif "STALE" == result:
                await ctx.send("The match ended in a draw between {} & {}".format(challenger[0], opponent[0]))
                red.add(amount + int(amount / 10))
                blue.add(amount + int(amount / 10))
        else:
            if not red.hasenough(amount):
                await ctx.send("{} does not have enough Moolah!".format(ctx.message.author.name))
            else:
                await ctx.send("{} does not have enough Moolah!".format(opponent[0]))


def tictac_checkboard(spaces):
    # horizontal, diagonal and vertical
    directions = [spaces[0:3], spaces[3:6], spaces[6:9], [spaces[0], spaces[3],
                                                          spaces[6]], [spaces[1], spaces[4], spaces[7]],
                  [spaces[2], spaces[5],
                   spaces[8]], [spaces[0], spaces[4], spaces[8]], [spaces[2], spaces[4],
                                                                   spaces[6]]]
    final = 9
    for number in spaces:
        if number != "_":
            final = final - 1
    if ['X', 'X', 'X'] in directions:
        return 'X'
    elif ['O', 'O', 'O'] in directions:
        return 'O'
    elif final == 0 and ['X', 'X', 'X'] not in directions and ['O', 'O', 'O'] not in directions:
        return "STALE"
    return '_'


def setup(bot):
    bot.add_cog(gambling(bot))
