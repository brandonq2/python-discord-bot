from asyncore import write
import csv
from tracemalloc import start
from warnings import catch_warnings
import discord
from discord.ext import commands
from discord.ext import tasks
import random
import config

description = 'Betting bot'

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
dict = {}
betStarter = ''
betActive = False
betClosed = False
activeBetters = {}
betYes = []
betNo = []
yesPoints = 1
noPoints = 1
yesWeight = 0
noWeight = 0

@bot.event
async def on_ready():
    global dict
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    dict = createDictionary()
    freepoints.start()

@tasks.loop(hours=1.0)
async def freepoints():
    global dict
    guild = bot.get_guild(551586327758372884)
    for memberID in dict:
        member = guild.get_member(int(memberID))
        if member.voice == None:
            continue
        else:
            if str(member.id) in dict:
                dict[str(member.id)] = str(int(dict[str(member.id)]) + 100)
                writeToCSV()
    
@bot.command()
async def flip(ctx, side, amount):
    guild = bot.get_guild(551586327758372884)
    embed=discord.Embed(title=":coin: Coin Flip | " + guild.get_member(ctx.message.author.id).name, description="This is the results of flipping a coin. It really ain't that complicated.", color=0xffb700)

    if int(dict.get(str(ctx.message.author.id))) < int(amount):
        embed.add_field(name="Broke Bitch: ", value="Get your money up not your funny up, you broke bitch", inline=True)
        await ctx.send(embed = embed)
    else:
        if str(side).lower() == 'heads' or str(side).lower() == 'tails':
            choice = random.choice(['heads', 'tails'])
            if str(side).lower() == choice:
                embed=discord.Embed(title=":green_circle: WIN | " + guild.get_member(ctx.message.author.id).name, description="This is the results of flipping a coin. It really ain't that complicated.", color=0x00ff1e)
                dict[str(ctx.message.author.id)] = str(int(dict[str(ctx.message.author.id)]) + int(amount))
                embed.add_field(name="Choice: ", value=str(side), inline=True)
                embed.add_field(name="Result: ", value=str(choice), inline=True)
                embed.add_field(name="Gained: ", value=str(amount), inline=True)
                await ctx.send(embed = embed)
            else:
                dict[str(ctx.message.author.id)] = str(int(dict[str(ctx.message.author.id)]) - int(amount))
                embed=discord.Embed(title=":red_circle: LOSS | " + guild.get_member(ctx.message.author.id).name, description="This is the results of flipping a coin. It really ain't that complicated.", color=0xff0000)
                embed.add_field(name="Choice: ", value=str(side), inline=True)
                embed.add_field(name="Result: ", value=str(choice), inline=True)
                embed.add_field(name="Lost: ", value=str(amount), inline=True)
                await ctx.send(embed = embed)
        else:
            embed.add_field(name="Invalid Option: ", value='Invalid side selection. Please choose either heads or tails.', inline=False)
            await ctx.send(embed = embed)
    writeToCSV()

@bot.command()
async def points(ctx): 
    guild = bot.get_guild(551586327758372884)
    embed=discord.Embed(title=":moneybag: Points | " + guild.get_member(ctx.message.author.id).name , color=0x00ff1e)
    embed.add_field(name="Current Points", value=str(dict[str(ctx.message.author.id)]), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def rob(ctx, member:discord.Member):
    if int(dict.get(str(ctx.message.author.id))) < int(100):
            embed=discord.Embed(title=":spy: Rob | You attempt to rob " + member.name, description="I didnt know it was possible to be too broke to rob someone :skull: :regional_indicator_x: :seven:.", color=0x00ff00)
            await ctx.send(embed=embed)
    elif int(dict.get(str(member.id))) < 100:
            embed=discord.Embed(title=":spy: Rob | You attempt to rob " + member.name, description="They were too broke to get robbed :skull: :regional_indicator_x: :seven:.", color=0x00ff00)
            await ctx.send(embed=embed)
    else:
        if random.randint(1, 10) == 1:
            dict[str(ctx.message.author.id)] = str(int(dict[str(ctx.message.author.id)]) + 100)
            dict[str(member.id)] = str(int(dict[str(member.id)]) - 100)
            embed=discord.Embed(title=":spy: Rob | You attempt to rob " + member.name, description="You ran their pockets. Fr ong, just like that :neutral_face:.", color=0x00ff00)
            embed.add_field(name="Gained", value="100", inline=True)
            await ctx.send(embed=embed)
        else:
            dict[str(ctx.message.author.id)] = str(int(dict[str(ctx.message.author.id)]) - 100)
            dict[str(member.id)] = str(int(dict[str(member.id)]) + 100)
            embed=discord.Embed(title=":spy: Rob | You attempt to rob " + member.name, description="You got caught lackin and got your cheeks clapped :skull: :regional_indicator_x: :seven:.", color=0xff0000)
            embed.add_field(name="Lost", value="100", inline=True)
            await ctx.send(embed=embed)
    writeToCSV()

@bot.command()
async def startbet(ctx, *arg):
    global betClosed
    global betActive
    global dict
    global betStarter
    global activeBetters
    global betYes
    global betNo
    global yesPoints
    global noPoints

    if(not betActive):
        embed=discord.Embed(title=":game_die: Bet Started", description="Use !bet to place bets, !checkbet to check your bet, !closebet to stop taking bets, and !endbet to cash out.", color=0x00ffb3)
        embed.add_field(name="Bet", value=' '.join(map(str, arg)), inline=False)
        await ctx.send(embed = embed)
        betActive = True
        activeBetters.clear()
        betClosed = False
        yesPoints = 1
        noPoints = 1
        dict = createDictionary()
        betStarter = ctx.message.author
        betYes.clear()
        betNo.clear()
    else:
        await ctx.send('A bet is already in progress, please ask the last bet starter to end the bet.')
        
@bot.command()
async def bet(ctx, yesOrNo, points):
    global activeBetters
    global yesPoints
    global noPoints
    embed=discord.Embed(title=":coin: Placing Bet", description="Placing your bet...", color=0xffffff)
    
    if ctx.message.author != betStarter:
        if not betActive or betClosed:
            embed.add_field(name="Error", value="There are currently no open bets.", inline=True)
        elif int(points) < 1:
            embed.add_field(name="Error", value="Aint no way you this broke :skull: x 7", inline=True)
        elif int(dict.get(str(ctx.message.author.id))) < int(points):
            embed.add_field(name="Error", value="You don't have enough points. You currently have " + str(dict[str(ctx.message.author.id)]) + " points." , inline=True)
        elif str(yesOrNo).lower() != 'yes' and str(yesOrNo).lower() != 'no':
            embed.add_field(name="Error", value="Not a valid choice, please select either yes or no.", inline=True)
        elif ctx.message.author.id not in activeBetters:
            activeBetters[ctx.message.author.id] = [yesOrNo, points]
            embed.add_field(name="Bet Choice", value=str(yesOrNo), inline=True)
            embed.add_field(name="Points Bet", value=str(points), inline=True)
            if str(yesOrNo) == 'yes':
                betYes.append(ctx.message.author.id)
                yesPoints += int(points)
            else:
                betNo.append(ctx.message.author.id)
                noPoints += int(points)
        else:
            embed.add_field(name="Error", value="You've already placed a bet.", inline=True)
    else:
        embed.add_field(name="Error", value="As the starter and moderator of the bet, you may not place a bet.", inline=True)
    await ctx.send(embed = embed)


@bot.command()
async def checkbet(ctx):
    embed=discord.Embed(title=":coin: Bet Info | " + ctx.message.author.name, color=0x00ffb3)

    if ctx.message.author.id not in activeBetters:
        embed.add_field(name="Error", value="You're not in the betting pool.", inline=False)
    else:
        embed.add_field(name="Prediction", value=str(activeBetters.get(ctx.message.author.id)[0]), inline=False)
        embed.add_field(name="Points Bet", value=str(activeBetters.get(ctx.message.author.id)[1]), inline=False)
    await ctx.send(embed = embed)

@bot.command()
async def prizepool(ctx):
    embed=discord.Embed(title=":coin: Prize Pool", color=0x00ffb3)
    embed.add_field(name="Points for Yes", value=str(yesPoints), inline=False)
    embed.add_field(name="Points for No", value=str(noPoints), inline=False)
    embed.add_field(name="Total Points", value=str(yesPoints + noPoints), inline=False)
    await ctx.send(embed=embed)

def createDictionary():
    with open('points.csv', mode = 'r') as inFile:
        reader = csv.reader(inFile)
        with open('points_new.csv', mode = 'w') as outFile:
            writer = csv.writer(outFile)
            temp = {rows[0]:rows[1] for rows in reader}
    return temp


def writeToCSV():
    with open('points.csv', 'w', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        for row in dict.items():
            writer.writerow(row)

@bot.command()
async def closebet(ctx):
    global betStarter
    global betActive
    global betClosed
    if betActive and not betClosed:
        if ctx.message.author == betStarter:
            betClosed = True
            embed=discord.Embed(title=":lock: Closing Bets", description="New bets cannot be placed anymore.", color=0xff0000)
            await ctx.send(embed = embed)
        else:
            await ctx.send('You are not the bet starter.')
            embed=discord.Embed(title=":lock: Closing Bets", description="You are not the bet starter.", color=0xff0000)
            await ctx.send(embed = embed)
    else:
        embed=discord.Embed(title=":lock: Closing Bets", description="There are no open bets.", color=0xff0000)
        await ctx.send(embed = embed)

@bot.command()
async def endbet(ctx, result):
    global betStarter
    global betActive
    global betClosed
    if betActive:
        if ctx.message.author == betStarter:
            calculateWeights()
            await calculateDistributions(ctx, result)
            betStarter = ''
            betActive = False
            betClosed = False
        else:
            embed=discord.Embed(title=":no_entry: End Bet Error", description="You are not the bet starter.", color=0xff0000)
            await ctx.send(embed = embed)
    else:
        embed=discord.Embed(title=":no_entry: End Bet Error", description="There are not open bets.", color=0xff0000)
        await ctx.send(embed = embed)
        

def calculateWeights():
    global yesWeight
    global noWeight
    yesWeight = (yesPoints + noPoints) / yesPoints
    noWeight = (yesPoints + noPoints) / noPoints

async def calculateDistributions(ctx, result):
    global yesWeight
    global noWeight
    embed1=discord.Embed(title=":green_circle: Winners", description="Total points being distributed: " + str(yesPoints + noPoints), color=0x00ff00)
    embed2=discord.Embed(title=":red_circle: Losers", description="Get clapped lmao.", color=0xff0000)

    if str(result).lower() == 'yes':
        for user1 in betYes:
            dict[str(user1)] =  str(int(dict[str(user1)]) + int(float(int(activeBetters.get(user1)[1]) * yesWeight)) - int(activeBetters.get(user1)[1]))
            embed1.add_field(name=bot.get_guild(551586327758372884).get_member(int(user1)).name, value=str(float(int(activeBetters.get(user1)[1]) * yesWeight)), inline=False)
        for user2 in betNo:
            dict[str(user2)] = str(int(dict[str(user2)]) - int(activeBetters.get(user2)[1]))
            embed2.add_field(name=bot.get_guild(551586327758372884).get_member(int(user2)).name, value=str(int(float(int(activeBetters.get(user2)[1])))), inline=False)
    elif str(result).lower() == 'no':
        for user1 in betNo:
            dict[str(user1)] =  str(int(dict[str(user1)]) + int(float(int(activeBetters.get(user1)[1]) * noWeight)) - int(activeBetters.get(user1)[1]))
            embed1.add_field(name=bot.get_guild(551586327758372884).get_member(int(user1)).name, value=str(int(float(int(activeBetters.get(user1)[1]) * noWeight))), inline=False)
        for user2 in betYes:
            dict[str(user2)] = str(int(dict[str(user2)]) - int(activeBetters.get(user2)[1]))
            embed2.add_field(name=bot.get_guild(551586327758372884).get_member(int(user2)).name, value=str(int(float(int(activeBetters.get(user2)[1])))), inline=False)

    await ctx.send(embed = embed1)
    await ctx.send(embed = embed2)
    writeToCSV()

@bot.command()
async def leaderboard(ctx):
    global dict
    temp = {}
    places = ''
    names = ''
    points =''

    for vals in dict.keys():
        temp[vals] = int(dict.get(vals))
    sorted_values = sorted(temp.values(), reverse = True) # Sort the values
    sorted_dict = {}
    counter = 1
    guild = bot.get_guild(551586327758372884)

    for i in sorted_values:
        for k in temp.keys():
            if int(temp[k]) == int(i):
                sorted_dict[k] = int(temp[k])
    for x in sorted_dict:
        places += str(counter) + '\n'
        names += guild.get_member(int(x)).name + '\n'
        points += str(sorted_dict[x]) + '\n'
        counter += 1
    
    embed=discord.Embed(title=":trophy: Points Leaderboard", description="This is the current standings.", color=0xffbb00)
    embed.add_field(name="Place", value=places, inline=True)
    embed.add_field(name="Name", value=names, inline=True)
    embed.add_field(name="Points", value=points, inline=True)
    await ctx.send(embed = embed)
        
@bot.command()
async def commands(ctx):
    embed=discord.Embed(title=":book: Commands List", color=0x0084ff)
    embed.add_field(name="!commands", value="Prints out a list of all commands available.", inline=False)
    embed.add_field(name="!startbet", value="Start a bet for others to participate in. The starter cannot participate. Example: '!startbet Will we win this game?'.", inline=False)
    embed.add_field(name="!closebet", value="Closes the bet, and stops anyone else from placing a bet. Example: '!closebet'.", inline=False)
    embed.add_field(name="!endbet", value="Ends the bet, and cashes everyone out. Example: '!endbet yes'.", inline=False)
    embed.add_field(name="!bet", value="Place a bet. Example: '!bet yes 1000'.", inline=False)
    embed.add_field(name="!checkbet", value="Checks your bet. Example: '!checkbet'.", inline=False)
    embed.add_field(name="!prizepool", value="Checks the prize pool of the active bet. Example: '!prizepool'.", inline=False)
    embed.add_field(name="!points", value="Returns how many points you have. Example: '!points'.", inline=False)
    embed.add_field(name="!flip", value="Allows you to flip a coin and bet points. Example: '!flip 1000'.", inline=False)
    embed.add_field(name="!rob", value="Attempts to rob someone. If you fail, you get robbed instead. Example: '!rob @Maple'.", inline=False)
    embed.add_field(name="!leaderboard", value="Prints out the current points standing. Example '!leaderboard'.", inline=False)
    await ctx.send(embed = embed)

bot.run(config.token)