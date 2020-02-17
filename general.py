import discord
from discord.ext import tasks
import functools
import shlex
import json
from bs4 import BeautifulSoup
import requests
import urllib
import RiotDataMine
import heapq
import asyncio
import pprint
import datetime
import GLOBALS

def timestamp_to_time(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp).strftime('%H:%M:%S')

def parse_commands(commands):
    return list(shlex.split(str(commands).replace('"','\'').replace('“','"').replace("”",'"')))

def remove_prefix(pre,msg):
    if pre == msg[:len(pre)]:
        msg = msg[len(pre):]
    while len(msg) > 0 and msg[0] == ' ':
        msg = msg[1:]
    return msg

def ctx_parse():
    def wrapper(func):
        @functools.wraps(func)
        async def method(*args,**kwargs):
            for arg in args:
                try:
                    arg_name = arg.__module__
                except:
                    continue
                if arg_name == 'discord.ext.commands.context':
                    arg.message.content = remove_prefix(f'.{func.__name__}',arg.message.content)
            await func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return method
    return wrapper

def parse_ctx_plus(ctx):
    return ctx.message.channel, ctx.message

def parse_user_id_from_mention(msg):
    return int(msg[3:-1])

def parse_league_user_discord(lolname):
    if '#' in lolname:
        return tuple(lolname.split('#'))
    return lolname, "EUW1"

async def get_userinfo(client,channel, message, args):
    args = list(args)
    if len(args) == 0:
        user_author = message.author
        fetch = GLOBALS.DATABASE.execute(f'SELECT * FROM USERS WHERE Author = "{user_author}"').fetchone()
        try:
            lolname = fetch[1]
            gateway = fetch[2]
        except:
            await channel.send(f"You have not yet set your league information, use .lolsetinfo")
            raise Exception("ERROR WITH INFO GET")
    else:
        if len(message.mentions) != 0:
            user_author = client.get_user(message.mentions[0].id)
            fetch = GLOBALS.DATABASE.execute(f'SELECT * FROM USERS WHERE Author = "{user_author}"').fetchone()
            try:
                lolname = fetch[1]
                gateway = fetch[2]
            except:
                await channel.send(f"User {args[0]} has not yet set there league information")
                raise Exception("ERROR WITH INFO GET")
        else:
            lolname, gateway = parse_league_user_discord(args[0])
    return lolname, gateway

async def basic_league_user_embed(riotuser, colour = discord.Colour.light_grey()):
    embed = discord.Embed(title=riotuser.userObj['name'],
                          description=f"{riotuser.userObj['gateway'].upper()}\nLvl. {riotuser.userObj['summonerLevel']}\n{await riotuser.lolwasted()} Hours Wasted",
                          colour=colour)
    embed.set_thumbnail(
        url=f"http://ddragon.leagueoflegends.com/cdn/10.2.1/img/profileicon/{riotuser.userObj['profileIconId']}.png")
    return embed

async def league_player_embed_data_get(username, gateway, channel, queue = 20, colour = discord.Colour.light_grey()):
    riotuser = RiotDataMine.RiotUser(username, gateway)
    embed = await basic_league_user_embed(riotuser,colour=colour)
    message = await channel.send(embed=embed)
    embed.add_field(name='Collecting Data:',value=f'{0}/{queue}')
    embed.add_field(name='Recent Matches:',value='Waiting...')
    embed.add_field(name='Winrate:',value='Waiting...')
    embed.add_field(name='KDA:',value='Waiting...')
    embed.add_field(name='KDA Distribution:',value='Waiting...')
    embed.add_field(name='Vision Score:',value='Waiting...')
    embed.add_field(name='CS Distribution:',value='Waiting...')
    embed.add_field(name='MultiKills:',value='Waiting...')
    embed.add_field(name='Favorite Champion:',value='Waiting...')
    async for special_stats, type_req in calculate_stats_from_matches_special_v2(riotuser,queue=queue):
        special_stats = await motify_special_match_stats(special_stats)
        embed.set_field_at(0,name='Collecting Data:',value=f'{special_stats["gamescount"]}/{min(queue,special_stats["totalgames"])} - {type_req}')
        embed.set_field_at(1,name='Recent Matches:',value=special_stats['special_stats']['recent_matches'])
        embed.set_field_at(2,name='Winrate:',value=special_stats['special_stats']['winrate'])
        embed.set_field_at(3,name='KDA:',value=special_stats['special_stats']['kda'])
        embed.set_field_at(4,name='KDA Distribution:',value=special_stats['special_stats']['kda_distribution'])
        embed.set_field_at(5,name='Vision Score:',value=special_stats['special_stats']['vision_score'])
        embed.set_field_at(6,name='CS Distribution:',value=special_stats['special_stats']['cs'])
        embed.set_field_at(7,name='MultiKills:',value=special_stats['special_stats']['multi_kills'])
        embed.set_field_at(8,name='Favorite Champion:',value=special_stats['special_stats']['favorite_champion'])
        await message.edit(embed=embed)
    embed.remove_field(0)
    await message.edit(embed=embed)

async def league_champion_embed_data_get(data,fullparti,username, gateway, channel,championId, colour = discord.Colour.light_grey(), queue = 20, api_stack = 5):
    parti = {'summonerName':username}
    parti['riotuser'] = RiotDataMine.RiotUser( parti['summonerName'], gateway)
    parti['championId'] = championId
    parti['description'] = f"{gateway.upper()}\nLvl. {parti['riotuser'].userObj['summonerLevel']}\n{await parti['riotuser'].lolwasted()} Hours Wasted\n\n{GLOBALS.STATICDATA['CHAMPIONS'][parti['championId']]['name']}"
    parti['embed'] = discord.Embed(title=parti['summonerName'],
                                   description=parti['description'],
                                   colour=colour)
    parti['embed'].set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/10.2.1/img/champion/{GLOBALS.STATICDATA['CHAMPIONS'][parti['championId']]['id']}.png")
    parti['message'] = await channel.send(embed=parti['embed'])
    await league_livegame_embed_data_get__update_parti(data,fullparti,parti, queue=queue,api_stack=api_stack)

async def league_livegame_embed_data_get(client,username, gateway, channel,queue = 20, api_stack = 5):
    riotuser = RiotDataMine.RiotUser( username, gateway)
    data = await riotuser._livegame_get_livegame_info()
    if data == None:
        await channel.send(f'{username} | {gateway} isn\'t currently in a match')
        return
    for parti in data:
        client.loop.create_task(league_champion_embed_data_get(data,parti,parti['summonerName'], gateway, channel,parti['championId'],colour=discord.Colour.red() if parti['team'] == 'red' else discord.Colour.blue(),queue=queue,api_stack=api_stack))

async def send_long_message(message, channel):
    buffer = ''
    for line in message.split('\n'):
        if len(buffer) + 1 + len(line) <= 1500:
            buffer+=f'\n{line}'
        else:
            await channel.send(buffer)
            buffer = line
    if buffer != '':
        await channel.send(buffer)

async def league_user_champions(baseurl,channel,username,gateway,queue = 10):
    riotuser = RiotDataMine.RiotUser(username,gateway)
    data = await riotuser.get_all_champions()
    data = sorted(data,key=lambda champ:(champ['championLevel'],champ['championPoints']),reverse=True)
    def format_champ(champ):
        link = f"{baseurl}/lolchampion/{urllib.parse.quote_plus(username)}/{gateway}/{20}/{champ['championId']}/{channel.id}"
        return f"{GLOBALS.STATICDATA['CHAMPIONS'][champ['championId']]['name']}\tLvl. {champ['championLevel']}\t{champ['championPoints']}\t{link}"
    msg = '\n'.join(map(format_champ,data[:(min(len(data),queue))]))
    await send_long_message(msg,channel)

async def relation_livegame(data, parti):
    good, bad = [],[]
    for partiD in data:
        if partiD['teamId'] != parti['teamId']:
            if (info := await RiotDataMine.RiotUser.get_champion_relation_compare(parti['championId'],partiD['championId'])) is not None:
                if info < 50:
                    good.append((partiD['championId'],info))
                elif info > 50:
                    bad.append((partiD['championId'],info))
    return good, bad


async def league_livegame_embed_data_get__update_parti(data,fullparti,parti,queue=5, api_stack = 5):
    neverplayed = False
    try:
        parti['champ_info'] = await parti['riotuser'].get_champion_info(parti['championId'])
    except:
        neverplayed = True
        parti['champ_info'] = {'championLevel' : 0,'championPoints' : 0}
    parti['description'] += f"\nLvl. {parti['champ_info']['championLevel']}\n{parti['champ_info']['championPoints']} pts."
    parti['embed'].description = parti['description']
    await parti['message'].edit(embed=parti['embed'])
    if neverplayed:
        parti['description'] += '\n\nNever played this champion before'
        parti['embed'].description = parti['description']
        await parti['message'].edit(embed=parti['embed'])
        return
    parti['embed'].add_field(name='Collecting Data:',value=f'{0}/{queue}')
    parti['embed'].add_field(name='Recent Matches:',value='Waiting...')
    parti['embed'].add_field(name='Winrate:',value='Waiting...')
    parti['embed'].add_field(name='KDA:',value='Waiting...')
    parti['embed'].add_field(name='KDA Distribution:',value='Waiting...')
    parti['embed'].add_field(name='Vision Score:',value='Waiting...')
    parti['embed'].add_field(name='CS Distribution:',value='Waiting...')
    parti['embed'].add_field(name='MultiKills:',value='Waiting...')
    if data is not None and fullparti is not None:
        goodagainst, badagaints = await relation_livegame(data,fullparti)
        bad = '\n'.join(map(lambda code:f"{GLOBALS.STATICDATA['CHAMPIONS'][code[0]]['name']} - {code[1]:.2f}%",badagaints))
        good = '\n'.join(map(lambda code:f"{GLOBALS.STATICDATA['CHAMPIONS'][code[0]]['name']} - {code[1]:.2f}%",goodagainst))
        if len(bad) > 0:
            parti['embed'].add_field(name='Vulnerable against:',value=bad)
        if len(good) > 0:
            parti['embed'].add_field(name='A threat to:',value=good)
    async for special_stats, type_req in calculate_stats_from_matches_special_v2(parti['riotuser'],queue=queue,champion=parti['championId'],api_stack=api_stack):
        special_stats = await motify_special_match_stats(special_stats)
        parti['embed'].set_field_at(0,name='Collecting Data:',value=f'{special_stats["gamescount"]}/{min(queue,special_stats["totalgames"])} - {type_req}')
        parti['embed'].set_field_at(1,name='Recent Matches:',value=special_stats['special_stats']['recent_matches'])
        parti['embed'].set_field_at(2,name='Winrate:',value=special_stats['special_stats']['winrate'])
        parti['embed'].set_field_at(3,name='KDA:',value=special_stats['special_stats']['kda'])
        parti['embed'].set_field_at(4,name='KDA Distribution:',value=special_stats['special_stats']['kda_distribution'])
        parti['embed'].set_field_at(5,name='Vision Score:',value=special_stats['special_stats']['vision_score'])
        parti['embed'].set_field_at(6,name='CS Distribution:',value=special_stats['special_stats']['cs'])
        parti['embed'].set_field_at(7,name='MultiKills:',value=special_stats['special_stats']['multi_kills'])
        await parti['message'].edit(embed=parti['embed'])
    parti['embed'].remove_field(0)
    await parti['message'].edit(embed=parti['embed'])

async def calculate_stats_from_matches_special(riotuser,champion=None,queue = 20):
    storeStats = {'gamescount':0,'wins':0,'lose':0,'kills':0,'assists':0,'deaths':0,'visionscore':0,'doublekills':0,'triplekills':0,'quadrakills':0,'pentakills':0,'champions':{},'totalMinionsKilled':0,'neutralMinionsKilledTeamJungle':0,'neutralMinionsKilledEnemyJungle':0}
    async for matchId in riotuser.get_matches_info(queue=queue,champion=champion):
        stats, type_req = await riotuser.get_match_details(matchId)
        add_match_stats_to_overall_stats(storeStats,stats)
        yield storeStats, type_req

def add_match_stats_to_overall_stats(overall_stats, stats):
    overall_stats['gamescount'] += 1
    if (stats['win'] == 'True' and type(stats['win']) == str) or (stats['win'] and type(stats['win']) == bool):
        overall_stats['wins'] += 1
    else:
        overall_stats['lose'] += 1
    overall_stats['kills'] += int(stats['kills'])
    overall_stats['assists'] += int(stats['assists'])
    overall_stats['deaths'] += int(stats['deaths'])
    try:
        overall_stats['totalMinionsKilled'] += int(stats['totalMinionsKilled'])
    except:
        pass
    try:
        overall_stats['neutralMinionsKilledTeamJungle'] += int(stats['neutralMinionsKilledTeamJungle'])
    except:
        pass
    try:
        overall_stats['neutralMinionsKilledEnemyJungle'] += int(stats['neutralMinionsKilledEnemyJungle'])
    except:
        pass
    overall_stats['visionscore'] += int(stats['visionScore'])
    overall_stats['doublekills'] += int(stats['doubleKills'])
    overall_stats['triplekills'] += int(stats['tripleKills'])
    overall_stats['quadrakills'] += int(stats['quadraKills'])
    overall_stats['pentakills'] += int(stats['pentaKills'])
    if stats['championId'] not in overall_stats['champions']:
        overall_stats['champions'][stats['championId']] = 1
    else:
        overall_stats['champions'][stats['championId']] += 1

async def calculate_stats_from_matches_special_v2(riotuser,champion=None,queue = 20,stored_stack=100, api_stack=5):
    storeStats = {'gamescount':0,'wins':0,'lose':0,'kills':0,'assists':0,'deaths':0,'visionscore':0,'doublekills':0,'triplekills':0,'quadrakills':0,'pentakills':0,'champions':{},'totalMinionsKilled':0,'neutralMinionsKilledTeamJungle':0,'neutralMinionsKilledEnemyJungle':0}
    last_req = "Stored Match"
    async for matchId_set, totalgames in riotuser.get_matches_info_v2(queue=queue,champion=champion):
        storeStats['totalgames'] = totalgames
        stack = 0
        last_req = "Stored Match"
        stack_rate = {"Stored Match":stored_stack, "API Call":api_stack}
        async for stats, type_req in riotuser.get_matches_details_v2(matchId_set):
            if last_req == type_req:
                stack+=1
            else:
                stack = 0
                yield storeStats, last_req
                last_req = type_req
            add_match_stats_to_overall_stats(storeStats,stats)
            if stack >= stack_rate[type_req]:
                stack = 0
                yield storeStats, last_req
    yield storeStats, last_req

async def motify_special_match_stats(special_stats):
    try:
        special_stats['special_stats'] = {
            'winrate': f"{round(special_stats['wins'] / special_stats['gamescount'] * 100)}%",
            'kill_average' : special_stats['kills']/special_stats['gamescount'],
            'death_average' : special_stats['deaths']/special_stats['gamescount'],
            'assist_average' : special_stats['assists']/special_stats['gamescount'],
            'lane_minion_killed' : special_stats['totalMinionsKilled']/special_stats['gamescount'],
            'jungle_team_killed' : special_stats['neutralMinionsKilledTeamJungle']/special_stats['gamescount'],
            'jungle_enemy_killed' : special_stats['neutralMinionsKilledEnemyJungle']/special_stats['gamescount'],
            'vision_score':f"{special_stats['visionscore']/special_stats['gamescount']:.2f}"
        }
    except ZeroDivisionError:
        special_stats['special_stats'] = {
            'winrate': f"0%",
            'kill_average' : 0,
            'death_average' : 0,
            'assist_average' : 0,
            'lane_minion_killed' : 0,
            'jungle_team_killed' : 0,
            'jungle_enemy_killed' : 0,
            'vision_score':f"0"
        }
    if special_stats['special_stats']['death_average'] != 0:
        kda = f"{(special_stats['special_stats']['kill_average'] + special_stats['special_stats']['assist_average']) / special_stats['special_stats']['death_average']:.2f}"
    else:
        kda = 'Perfect'
    special_stats['special_stats'].update({
        'recent_matches':f"{special_stats['gamescount']}G {special_stats['wins']}W {special_stats['lose']}L",
        'kda': f"{kda} KDA",
        'kda_distribution':f"**{special_stats['special_stats']['kill_average']:.2f}** {special_stats['special_stats']['death_average']:.2f} *{special_stats['special_stats']['assist_average']:.2f}*",
        'multi_kills':f"{special_stats['doublekills']} D, {special_stats['triplekills']} T, {special_stats['quadrakills']} Q, {special_stats['pentakills']} P",
        'cs':f"**{special_stats['special_stats']['lane_minion_killed']:.2f}** {special_stats['special_stats']['jungle_team_killed']:.2f} *{special_stats['special_stats']['jungle_enemy_killed']:.2f}*"
    })
    try:
        special_stats['special_stats'].update({
            'favorite_champion':GLOBALS.STATICDATA['CHAMPIONS'][int(sorted(list(special_stats['champions'].items()), key=lambda champ:champ[1], reverse=True)[0][0])]['name']
        })
    except:
        special_stats['special_stats'].update({
            'favorite_champion':'None'
        })
    return special_stats