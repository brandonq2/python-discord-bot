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
    print('RUN')
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
async def points(ctx): 
    await ctx.send('You currently have: ' + str(dict[str(ctx.message.author.id)]) + ' points.')

@bot.command()
async def rob(ctx, member:discord.Member):
    if int(dict.get(str(ctx.message.author.id))) < int(100):
        await ctx.send('I didnt know it was possible to be too broke to rob someone :skull: x 7.')
    elif int(dict.get(str(member.id))) < 100:
        await ctx.send('Theyre too poor to rob :skull: x 7.')
    else:
        if random.randint(1, 10) == 1:
            dict[str(ctx.message.author.id)] = str(int(dict[str(ctx.message.author.id)]) + 100)
            dict[str(member.id)] = str(int(dict[str(member.id)]) - 100)
            await ctx.send('Congrats, you robbed a man for 100 points :neutral_face:.')
        else:
            dict[str(ctx.message.author.id)] = str(int(dict[str(ctx.message.author.id)]) - 100)
            dict[str(member.id)] = str(int(dict[str(member.id)]) + 100)
            await ctx.send('Bruh, you got your ass kicked, and lost 100 bones :skull: x 7.')
    writeToCSV()

    
    

@bot.command()
async def startbet(ctx, *arg):
    global betActive
    global dict
    global betStarter
    global activeBetters
    global betYes
    global betNo
    global yesPoints
    global noPoints
    if(not betActive):
        await ctx.send("Bet: " + ' '.join(map(str, arg)))
        betActive = True
        activeBetters.clear()
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
    #if ctx.message.author != betStarter:
    if int(points) < 1:
        await ctx.send('Aint no way you this broke :skull: x 7')
    elif int(dict.get(str(ctx.message.author.id))) < int(points):
        await ctx.send('You do not have enough points. You currently have: ' + str(dict[str(ctx.message.author.id)]) + ' points.')
    elif str(yesOrNo).lower() != 'yes' and str(yesOrNo).lower() != 'no':
        await ctx.send('Not a valid choice. Please select either yes or no.')
    elif ctx.message.author.id not in activeBetters:
        activeBetters[ctx.message.author.id] = [yesOrNo, points]
        await ctx.send('Adding you to the betting pool...')
        if str(yesOrNo) == 'yes':
            betYes.append(ctx.message.author.id)
            yesPoints += int(points)
        else:
            betNo.append(ctx.message.author.id)
            noPoints += int(points)
    else:
        await ctx.send('You\'ve already placed a bet.')
    #else:
        #await ctx.send("As the starter and moderator of the bet, you may not place a bet.")


    
@bot.command()
async def checkbet(ctx):
    if ctx.message.author.id not in activeBetters:
        await ctx.send('You are not in the betting pool.')
    else:
        await ctx.send('Prediction: ' + str(activeBetters.get(ctx.message.author.id)[0] + " | Points Bet: " + str(activeBetters.get(ctx.message.author.id)[1])))

@bot.command()
async def prizepool(ctx):
    await ctx.send("The total prize pool is: " + str(yesPoints + noPoints) + " points.")

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
async def endbet(ctx, result):
    global betStarter
    global betActive
    if betActive:
        if ctx.message.author == betStarter:
            calculateWeights()
            await calculateDistributions(ctx, result)
            betStarter = ''
            betActive = False
        else:
            await ctx.send('You are not the bet starter.')
    else:
        await ctx.send('There is no bet currently active.')
        

def calculateWeights():
    global yesWeight
    global noWeight
    yesWeight = (yesPoints + noPoints) / yesPoints
    noWeight = (yesPoints + noPoints) / noPoints

async def calculateDistributions(ctx, result):
    global yesWeight
    global noWeight
    if str(result).lower() == 'yes':
        for user1 in betYes:
            dict[str(user1)] =  str(int(dict[str(user1)]) + int(float(int(activeBetters.get(user1)[1]) * yesWeight)) - int(activeBetters.get(user1)[1]))
            await ctx.send('User: ' + bot.get_guild(551586327758372884).get_member(int(user1)).name + ' earned ' + str(int(float(int(activeBetters.get(user1)[1]) * yesWeight))) + ' points.')
        for user2 in betNo:
            dict[str(user2)] = str(int(dict[str(user2)]) - int(activeBetters.get(user2)[1]))
            await ctx.send('User: ' + bot.get_guild(551586327758372884).get_member(int(user2)).name + ' lost ' + str(int(float(int(activeBetters.get(user2)[1])))) + ' points.')
    elif str(result).lower() == 'no':
        for user1 in betNo:
            dict[str(user1)] =  str(int(dict[str(user1)]) + int(float(int(activeBetters.get(user1)[1]) * noWeight)) - int(activeBetters.get(user1)[1]))
            await ctx.send('User: ' + bot.get_guild(551586327758372884).get_member(int(user1)).name + ' earned ' + str(int(float(int(activeBetters.get(user1)[1]) * noWeight))) + ' points.')
        for user2 in betYes:
            dict[str(user2)] = str(int(dict[str(user2)]) - int(activeBetters.get(user2)[1]))
            await ctx.send('User: ' + bot.get_guild(551586327758372884).get_member(int(user2)).name + ' lost ' + str(int(float(int(activeBetters.get(user2)[1])))) + ' points.')
    writeToCSV()

bot.run(config.token)