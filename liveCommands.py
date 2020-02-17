import discord
import functools
import shlex
import json
from bs4 import BeautifulSoup
import requests
import urllib
import RiotDataMine
import GLOBALS
import general
import datetime
import time
from selenium import webdriver
import os

@general.ctx_parse()
async def lolwasted(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    lolname, gateway = await general.get_userinfo(client,channel,message,general.parse_commands(message.content))
    riotuser = RiotDataMine.RiotUser(lolname,gateway)
    hours = await riotuser.lolwasted()
    await channel.send(f"{lolname}#{gateway} has wasted {hours} hours on league")

@general.ctx_parse()
async def lolsetinfo(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    person = message.author
    if len(message.mentions) > 0:
        args = args[1:]
        person = client.get_user(message.mentions[0].id)
        adminrole = discord.utils.get(ctx.guild.roles, name="Admin")
        if adminrole not in ctx.author.roles:
            await message.send("Need to be admin to use that command")
            return
    lolname, gateway = general.parse_league_user_discord(args[0])
    if len(GLOBALS.DATABASE.execute(f'SELECT * FROM USERS WHERE Author = "{person}"').fetchall()) > 1:
        GLOBALS.DATABASE.execute(f'DELETE FROM USERS WHERE Author = "{person}"')
    GLOBALS.DATABASE.execute(f'INSERT INTO USERS VALUES ("{person}", "{lolname}", "{gateway.upper()}")')
    GLOBALS.DATABASE.commit()

    await channel.send(f'User <@{person.id}> \'s in-game name set to {lolname}, gateway {gateway}')

@general.ctx_parse()
async def lolhelp(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    with open('help.json','r') as f:
        HELP = json.load(f)
    embed = discord.Embed(title="Commands",colour=discord.Color.blue())
    embed.set_thumbnail(url='https://i.imgur.com/4e2Rnwq.png')
    for command in HELP:
        embed.add_field(name=command['cmd'], value=f"Format: {command['format']}\nPurpose: {command['purpose']}", inline=False)

    await channel.send(embed=embed)

@general.ctx_parse()
async def lolprofile(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    lolname, gateway = await general.get_userinfo(client,channel,message,general.parse_commands(message.content))
    await general.league_player_embed_data_get(lolname,gateway,channel)

@general.ctx_parse()
async def lolprofilefull(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    lolname, gateway = await general.get_userinfo(client,channel,message,general.parse_commands(message.content))
    await general.league_player_embed_data_get(lolname,gateway,channel,queue=50000)

@general.ctx_parse()
async def lolprofileplus(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    queue = int(args[0])
    lolname, gateway = await general.get_userinfo(client,channel,message,args[1:])
    await general.league_player_embed_data_get(lolname,gateway,channel,queue=queue)


@general.ctx_parse()
async def lollivematchplus(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    queue = int(args[0])
    lolname, gateway = await general.get_userinfo(client,channel,message,args[1:])
    await general.league_livegame_embed_data_get(client,lolname,gateway,channel,queue=queue,api_stack=2)

@general.ctx_parse()
async def lollivematch(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    lolname, gateway = await general.get_userinfo(client,channel,message,general.parse_commands(message.content))
    await general.league_livegame_embed_data_get(client,lolname,gateway,channel,queue=20,api_stack=2)

@general.ctx_parse()
async def lolchampion( client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    champion = args[0].lower()
    lolname, gateway = await general.get_userinfo(client,channel,message,args[1:])
    await general.league_champion_embed_data_get(None,None,lolname,gateway,channel, int(GLOBALS.STATICDATA['CHAMPIONS'][champion]['key']),queue=20)

@general.ctx_parse()
async def lolchampionplus(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    queue = int(args[0])
    champion = args[1].lower()
    lolname, gateway = await general.get_userinfo(client,channel,message,args[2:])
    await general.league_champion_embed_data_get(None,None,lolname,gateway,channel, int(GLOBALS.STATICDATA['CHAMPIONS'][champion]['key']),queue=queue)

@general.ctx_parse()
async def lolchampionfull(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    champion = args[0].lower()
    lolname, gateway = await general.get_userinfo(client,channel,message,args[1:])
    await general.league_champion_embed_data_get(None,None,lolname,gateway,channel, int(GLOBALS.STATICDATA['CHAMPIONS'][champion]['key']),queue=50000)

@general.ctx_parse()
async def deletemessages( client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    adminrole = discord.utils.get(ctx.guild.roles, name="Admin")
    if adminrole not in ctx.author.roles:
        await message.send("Your not a admin so you can't use this method")
    args = general.parse_commands(message.content)
    if len(args) < 2:
        await channel.send("incorrect command formating")
    user = client.get_user(message.mentions[0].id)
    limit = int(args[1])

    for message in await channel.history(limit=limit).flatten():
        if message.author == user:
            await message.delete()

@general.ctx_parse()
async def lolmonitor(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    lolname, gateway = await general.get_userinfo(client,channel,message,args)
    riotuser = RiotDataMine.RiotUser( lolname, gateway)
    try:
        data = await riotuser.livegame_info_all()
    except:
        await channel.send("User isn't currenly in a live match")
        return
    embed = general.basic_league_user_embed(riotuser)
    starttime = data['gameStartTime']
    embed.add_field(name='Expired Time:',value=datetime.datetime.utcfromtimestamp((int(time.time()*1000)-starttime)/1000).strftime('%H:%M:%S'))
    mess = await channel.send(embed = embed)
    while True:
        embed.set_field_at(0,name='Expired Time:',value=datetime.datetime.utcfromtimestamp((int(time.time()*1000)-starttime)/1000).strftime('%H:%M:%S'))
        await mess.edit(embed = embed)

@general.ctx_parse()
async def lolchampions(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    lolname, gateway = await general.get_userinfo(client,channel,message,args)
    await general.league_user_champions('http://annekinutils.xyz',channel,lolname,gateway,queue=10)
@general.ctx_parse()
async def lolchampionsplus(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    amount = int(args[0])
    lolname, gateway = await general.get_userinfo(client,channel,message,args[1:])
    await general.league_user_champions('http://annekinutils.xyz',channel,lolname,gateway,queue=amount)
@general.ctx_parse()
async def lolchampionsfull(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    lolname, gateway = await general.get_userinfo(client,channel,message,args)
    await general.league_user_champions('http://annekinutils.xyz',channel,lolname,gateway,queue=300)

async def lolchampionrelation(func, args, lane = 'all'):
    championId = int(GLOBALS.STATICDATA["CHAMPIONS"][GLOBALS.lowerplus(args[0])]['key'])
    championId2 = None
    if len(args) > 1:
        championId2 = int(GLOBALS.STATICDATA["CHAMPIONS"][GLOBALS.lowerplus(args[1])]['key'])
    try:
        if championId2 is None:
            msg = ''
            async for champId, risk in func( championId,pos=lane):
                msg += f'{GLOBALS.STATICDATA["CHAMPIONS"][champId]["name"]} - {float(risk):.2f}%\n'
            return msg
        else:
            find = False
            async for champId, risk in func(championId,pos=lane):
                if champId == championId2:
                    find = True
                    return f'{risk:.2f}%'
            if not find:
                return "No Data"
    except Exception as e:
        return "No Data"

@general.ctx_parse()
async def lolchampionweak(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    msg = await lolchampionrelation(RiotDataMine.RiotUser.get_champion_weak,args)
    await general.send_long_message(msg,channel)

@general.ctx_parse()
async def lolchampionweakpos(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    lane = args[0]
    args = args[1:]
    msg = await lolchampionrelation(RiotDataMine.RiotUser.get_champion_weak,args,lane=lane)
    await general.send_long_message(msg,channel)

@general.ctx_parse()
async def lolchampionstrong(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    msg = await lolchampionrelation(RiotDataMine.RiotUser.get_champion_strong,args)
    await general.send_long_message(msg,channel)

@general.ctx_parse()
async def lolchampionstrongpos(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    lane = args[0]
    args = args[1:]
    msg = await lolchampionrelation(RiotDataMine.RiotUser.get_champion_strong,args,lane=lane)
    await general.send_long_message(msg,channel)

@general.ctx_parse()
async def lolminerelationdata(client, ctx):
    adminrole = discord.utils.get(ctx.guild.roles, name="Admin")
    if adminrole not in ctx.author.roles:
        await client.send("Your not a admin so you can't use this method")
        return
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    GLOBALS.chromeDriver = webdriver.Chrome(os.path.join(os.getcwd(),'chromedriver'))
    total = len(list(filter(lambda k:type(k) is int,GLOBALS.STATICDATA["CHAMPIONS"].keys())))
    msg = await channel.send(f'0/{total}')
    for i, champId in enumerate(filter(lambda k:type(k) is int, GLOBALS.STATICDATA['CHAMPIONS'])):
        await msg.edit(content=f'{i}/{total} - {GLOBALS.STATICDATA["CHAMPIONS"][champId]["name"]}')
        await RiotDataMine.RiotUser.mine_champion_relation(champId)
    await msg.edit(content=f'DONE')

@general.ctx_parse()
async def lolminerelationdatasingle(client, ctx):
    channel, message = general.parse_ctx_plus(ctx)
    args = general.parse_commands(message.content)
    GLOBALS.chromeDriver = webdriver.Chrome(os.path.join(os.getcwd(),'chromedriver'))
    await RiotDataMine.RiotUser.mine_champion_relation(int(GLOBALS.STATICDATA['CHAMPIONS'][GLOBALS.lowerplus(args[0])]['key']))

async def on_command_error(ctx, err):
    channel, message = general.parse_ctx_plus(ctx)
    await channel.send("Unknown command, type .lolhelp for all commands")
