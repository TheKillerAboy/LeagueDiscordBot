import discord
import functools
import shlex
import json
from bs4 import BeautifulSoup
import requests
import urllib
import RiotDataMine
import GLOBALS
from general import *
import datetime
import time
from selenium import webdriver

@ctx_parse()
async def lolwasted(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,parse_commands(message.content))
    riotuser = RiotDataMine.RiotUser(DATABASE,lolname,gateway)
    hours = await riotuser.lolwasted()
    await channel.send(f"{lolname}#{gateway} has wasted {hours} hours on league")

@ctx_parse()
async def lolsetinfo(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    person = message.author
    if len(message.mentions) > 0:
        args = args[1:]
        person = client.get_user(message.mentions[0].id)
        adminrole = discord.utils.get(ctx.guild.roles, name="Admin")
        if adminrole not in ctx.author.roles:
            await message.send("Need to be admin to use that command")
            return
    lolname, gateway = parse_league_user_discord(args[0])
    if len(DATABASE.execute(f'SELECT * FROM USERS WHERE Author = "{person}"').fetchall()) > 1:
        DATABASE.execute(f'DELETE FROM USERS WHERE Author = "{person}"')
    DATABASE.execute(f'INSERT INTO USERS VALUES ("{person}", "{lolname}", "{gateway.upper()}")')
    DATABASE.commit()

    await channel.send(f'User <@{person.id}> \'s in-game name set to {lolname}, gateway {gateway}')

@ctx_parse()
async def lolhelp(DATABASE,client, ctx):
    channel, message = parse_ctx_plus(ctx)
    with open('help.json','r') as f:
        HELP = json.load(f)
    embed = discord.Embed(title="Commands",colour=discord.Color.blue())
    embed.set_thumbnail(url='https://i.imgur.com/4e2Rnwq.png')
    for command in HELP:
        embed.add_field(name=command['cmd'], value=f"Format: {command['format']}\nPurpose: {command['purpose']}", inline=False)

    await channel.send(embed=embed)

@ctx_parse()
async def lolprofile(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,parse_commands(message.content))
    await league_player_embed_data_get(DATABASE,lolname,gateway,channel)

@ctx_parse()
async def lolprofilefull(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,parse_commands(message.content))
    await league_player_embed_data_get(DATABASE,lolname,gateway,channel,queue=50000)

@ctx_parse()
async def lolprofileplus(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    queue = int(args[0])
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,args[1:])
    await league_player_embed_data_get(DATABASE,lolname,gateway,channel,queue=queue)


@ctx_parse()
async def lollivematchplus(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    queue = int(args[0])
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,args[1:])
    await league_livegame_embed_data_get(client,DATABASE,lolname,gateway,channel,queue=queue,api_stack=2)

@ctx_parse()
async def lollivematch(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,parse_commands(message.content))
    await league_livegame_embed_data_get(client,DATABASE,lolname,gateway,channel,queue=20,api_stack=2)

@ctx_parse()
async def lolchampion(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    champion = args[0].lower()
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,args[1:])
    await league_champion_embed_data_get(DATABASE,lolname,gateway,channel, int(GLOBALS.STATICDATA['CHAMPIONS'][champion]['key']),queue=20)

@ctx_parse()
async def lolchampionplus(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    queue = int(args[0])
    champion = args[1].lower()
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,args[2:])
    await league_champion_embed_data_get(DATABASE,lolname,gateway,channel, int(GLOBALS.STATICDATA['CHAMPIONS'][champion]['key']),queue=queue)

@ctx_parse()
async def lolchampionfull(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    champion = args[0].lower()
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,args[1:])
    await league_champion_embed_data_get(DATABASE,lolname,gateway,channel, int(GLOBALS.STATICDATA['CHAMPIONS'][champion]['key']),queue=50000)

@ctx_parse()
async def deletemessages(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    adminrole = discord.utils.get(ctx.guild.roles, name="Admin")
    if adminrole not in ctx.author.roles:
        await message.send("Your not a admin so you can't use this method")
    args = parse_commands(message.content)
    if len(args) < 2:
        await channel.send("incorrect command formating")
    user = client.get_user(message.mentions[0].id)
    limit = int(args[1])

    for message in await channel.history(limit=limit).flatten():
        if message.author == user:
            await message.delete()

@ctx_parse()
async def lolmonitor(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,args)
    riotuser = RiotDataMine.RiotUser(DATABASE, lolname, gateway)
    try:
        data = await riotuser.livegame_info_all()
    except:
        await channel.send("User isn't currenly in a live match")
        return
    embed = basic_league_user_embed(riotuser)
    starttime = data['gameStartTime']
    embed.add_field(name='Expired Time:',value=datetime.datetime.utcfromtimestamp((int(time.time()*1000)-starttime)/1000).strftime('%H:%M:%S'))
    mess = await channel.send(embed = embed)
    while True:
        embed.set_field_at(0,name='Expired Time:',value=datetime.datetime.utcfromtimestamp((int(time.time()*1000)-starttime)/1000).strftime('%H:%M:%S'))
        await mess.edit(embed = embed)

@ctx_parse()
async def lolchampions(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,args)
    await league_user_champions('http://annekinutils.xyz',DATABASE,channel,lolname,gateway,queue=10)
@ctx_parse()
async def lolchampionsplus(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    amount = int(args[0])
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,args[1:])
    await league_user_champions('http://annekinutils.xyz',DATABASE,channel,lolname,gateway,queue=amount)
@ctx_parse()
async def lolchampionsfull(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    lolname, gateway = await get_userinfo(DATABASE,client,channel,message,args)

async def lolchampionrelation(DATABASE,func, args, lane = 'all'):
    championId = GLOBALS.STATICDATA["CHAMPIONS"][GLOBALS.lowerplus(args[0])]['key']
    championId2 = None
    if len(args) > 1:
        championId2 = GLOBALS.STATICDATA["CHAMPIONS"][GLOBALS.lowerplus(args[0])]['key']
    try:
        if championId2 is None:
            msg = ''
            async for champId, risk in func(DATABASE, championId,pos=lane):
                msg += f'{GLOBALS.STATICDATA["CHAMPIONS"][champId]["name"]} - {float(risk):.2f}%\n'
            return msg
        else:
            async for champId, risk in func(DATABASE, championId,pos=lane):
                if champId == championId2:
                    return f'{risk}%'
            return "No Data"
    except:
        return "No Data"

@ctx_parse()
async def lolchampionweak(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    msg = await lolchampionrelation(DATABASE,RiotDataMine.RiotUser.get_champion_weak,args)
    await send_long_message(msg,channel)

@ctx_parse()
async def lolchampionweakpos(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    lane = args[0]
    args = args[1:]
    msg = await lolchampionrelation(DATABASE,RiotDataMine.RiotUser.get_champion_weak,args,lane=lane)
    await send_long_message(msg,channel)

@ctx_parse()
async def lolchampionstrong(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    msg = await lolchampionrelation(DATABASE,RiotDataMine.RiotUser.get_champion_strong,args)
    await send_long_message(msg,channel)

@ctx_parse()
async def lolchampionstrongpos(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    lane = args[0]
    args = args[1:]
    msg = await lolchampionrelation(DATABASE,RiotDataMine.RiotUser.get_champion_strong,args,lane=lane)
    await send_long_message(msg,channel)

@ctx_parse()
async def lolminerelationdata(DATABASE, client, ctx):
    channel, message = parse_ctx_plus(ctx)
    args = parse_commands(message.content)
    GLOBALS.chromeDriver = webdriver.Chrome('chromedriver.exe')
    msg = await channel.send(f'0/{len(GLOBALS.STATICDATA["CHAMPIONS"])//2}')
    for i, champId in enumerate(filter(lambda k:type(k) is int, GLOBALS.STATICDATA['CHAMPIONS'])):
        await RiotDataMine.RiotUser.mine_champion_relation(DATABASE,champId)
        await msg.edit(content=f'{i+1}/{len(GLOBALS.STATICDATA["CHAMPIONS"])/2}')
    await msg.edit(content=f'DONE')
