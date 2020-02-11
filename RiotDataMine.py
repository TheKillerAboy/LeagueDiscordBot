import GLOBALS
from riotwatcher import ApiError
import asyncio
import functools
import datetime
import requests
from bs4 import BeautifulSoup, NavigableString
import itertools
import general

def timestamp_to_time(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp).strftime('%H:%M:%S')

class RiotUser:
    STORED_MATCH_DATA = \
        ["matchId", "participantId", "win", "item0", "item1", "item2", "item3",
        "item4", "item5", "item6", "kills", "deaths", "assists", "largestKillingSpree",
        "largestMultiKill", "killingSprees", "longestTimeSpentLiving", "doubleKills", "tripleKills",
        "quadraKills", "pentaKills", "unrealKills", "totalDamageDealt", "magicDamageDealt",
        "physicalDamageDealt", "trueDamageDealt", "largestCriticalStrike", "totalDamageDealtToChampions",
        "magicDamageDealtToChampions", "physicalDamageDealtToChampions", "trueDamageDealtToChampions",
        "totalHeal", "totalUnitsHealed", "damageSelfMitigated", "damageDealtToObjectives",
        "damageDealtToTurrets", "visionScore", "timeCCingOthers", "totalDamageTaken",
        "magicalDamageTaken", "physicalDamageTaken", "trueDamageTaken", "goldEarned",
        "goldSpent", "turretKills", "inhibitorKills", "totalMinionsKilled", "neutralMinionsKilled",
        "neutralMinionsKilledTeamJungle", "neutralMinionsKilledEnemyJungle", "totalTimeCrowdControlDealt",
        "champLevel", "visionWardsBoughtInGame", "sightWardsBoughtInGame", "wardsPlaced", "wardsKilled",
        "firstBloodKill", "firstBloodAssist", "firstTowerKill", "firstTowerAssist", "firstInhibitorKill",
        "firstInhibitorAssist", "combatPlayerScore", "objectivePlayerScore", "totalPlayerScore", "totalScoreRank",
        "playerScore0", "playerScore1", "playerScore2", "playerScore3", "playerScore4", "playerScore5", "playerScore6",
        "playerScore7", "playerScore8", "playerScore9", "perk0", "perk0Var1", "perk0Var2", "perk0Var3", "perk1",
        "perk1Var1", "perk1Var2", "perk1Var3", "perk2", "perk2Var1", "perk2Var2", "perk2Var3", "perk3", "perk3Var1",
        "perk3Var2", "perk3Var3", "perk4", "perk4Var1", "perk4Var2", "perk4Var3", "perk5", "perk5Var1", "perk5Var2",
        "perk5Var3", "perkPrimaryStyle", "perkSubStyle", "statPerk0", "statPerk1", "statPerk2", "championId"]
    STORED_GATEWAYS = ["BR1","EUW1","JP1","KR","LA1","LA2","NA1","OC1","TR1","RU"]

    def gateway_parse(self,gateway):
        for gate in self.STORED_GATEWAYS:
            if gate[:len(gateway)].lower() == gateway.lower():
                return gate

    @staticmethod
    def teamId_to_team(teamId):
        return 'blue' if teamId == 100 else 'red'

    def __init__(self,DATABASE, username, gateway):
        self.userObj = GLOBALS.RIOTWATCHER.summoner.by_name(self.gateway_parse(gateway),username)
        self.userObj['accountIdA'] = self.userObj['accountId'].replace('-','_')
        self.DATABASE = DATABASE
        if len(DATABASE.execute(f"SELECT * FROM LEAGUE_USERS WHERE accountId = '{self.userObj['accountIdA']}'").fetchall()) == 0:
            DATABASE.execute(f"INSERT INTO LEAGUE_USERS VALUES ('{self.userObj['accountIdA']}',0)")
            DATABASE.execute(f"CREATE TABLE LEAGUE_USER_{self.userObj['accountIdA']} ({', '.join(self.STORED_MATCH_DATA)})")
            DATABASE.commit()

        self.userObj['gateway'] = self.gateway_parse(gateway)

    async def _livegame_get_livegame_info(self,loop = None):
        try:
            data = await self.run_command_riotwatcher(GLOBALS.RIOTWATCHER.spectator.by_summoner,self.userObj['gateway'],self.userObj['id'], loop=loop)
            outdata = data['participants']
            for i,parti in enumerate(outdata):
                parti['team'] = self.teamId_to_team(parti['teamId'])
                parti['id'] = i
            return outdata
        except Exception as e:
            print(e)
            return None

    async def livegame_info_all(self):
        return await self.run_command_riotwatcher(GLOBALS.RIOTWATCHER.spectator.by_summoner,self.userObj['gateway'],self.userObj['id'])

    async def get_champion_info(self, championId):
        return await self.run_command_riotwatcher(GLOBALS.RIOTWATCHER.champion_mastery.by_summoner_by_champion,self.userObj['gateway'],self.userObj['id'],championId)

    @staticmethod
    async def run_command_riotwatcher(func,*args,loop=None,**kwargs):
        while True:
            try:
                if loop is None:
                    loop = GLOBALS.client.loop
                return await loop.run_in_executor(None,functools.partial(func,**kwargs),*args)
            except ApiError as err:
                if err.response.status_code == 429:
                    print('Rate Limit Exceeded')
                    await asyncio.sleep(5)
                else:
                    raise err

    async def get_all_champions(self):
        return await self.run_command_riotwatcher(GLOBALS.RIOTWATCHER.champion_mastery.by_summoner,self.userObj['gateway'],self.userObj['id'])

    async def get_matches_info_v2(self,champion=None, queue = 20):
        begin_index = 0
        kwargs = {}
        if champion is not None:
            kwargs = {'champion': champion}
        data = await self.run_command_riotwatcher(GLOBALS.RIOTWATCHER.match.matchlist_by_account, self.userObj['gateway'],
                                                  self.userObj['accountId'], begin_index=50000,
                                                  end_index=50000, **kwargs)
        total_games = data['totalGames']
        queue = min(queue, total_games)
        while begin_index < queue:
            end_index = min(begin_index + 100, queue)
            data = await self.run_command_riotwatcher(GLOBALS.RIOTWATCHER.match.matchlist_by_account, self.userObj['gateway'],
                                                      self.userObj['accountId'], begin_index=begin_index,
                                                      end_index=end_index, **kwargs)
            yield set(map(lambda match: match['gameId'], data['matches'])), total_games
            begin_index = end_index

    def tuple_to_dict_match_data(self, tuple):
        return {self.STORED_MATCH_DATA[i]:tuple[i] for i in range(len(self.STORED_MATCH_DATA))}

    async def get_match_details_v2_api_call(self, matchId):
        data = await self.run_command_riotwatcher(GLOBALS.RIOTWATCHER.match.by_id, self.userObj['gateway'], matchId)
        partiId = 0
        for parti in data['participantIdentities']:
            if parti['player']['accountId'] == self.userObj['accountId']:
                partiId = parti['participantId']
                break
        for parti in data['participants']:
            if parti['participantId'] == partiId:
                stats = {**parti['stats'], 'championId': parti['championId'], 'matchId': matchId}
                store = []
                for key in self.STORED_MATCH_DATA:
                    try:
                        store.append(stats[key])
                    except:
                        store.append('')
                storeStr = ', '.join([f'"{store[i]}"' for i in range(len(self.STORED_MATCH_DATA))])
                self.DATABASE.execute(f"INSERT INTO LEAGUE_USER_{self.userObj['accountIdA']} VALUES ({storeStr})")
                self.DATABASE.commit()
                return stats

    async def get_matches_details_v2(self, matchId_set, stored_stack = 100):
        matchId_set = matchId_set.copy()
        def str_qu(val):
            return f'"{val}"'
        data = self.DATABASE.execute(
            f"SELECT * FROM LEAGUE_USER_{self.userObj['accountIdA']} WHERE matchId IN ({', '.join(map(str_qu,matchId_set))})").fetchall()
        for match in map(self.tuple_to_dict_match_data,data):
            try:
                matchId_set.remove(int(match['matchId']))
                yield match, "Stored Match"
            except:
                self.DATABASE.execute(f"DELETE FROM LEAGUE_USER_{self.userObj['accountIdA']} WHERE matchId = {str_qu(match['matchId'])}")
        for matchId in matchId_set:
            yield await self.get_match_details_v2_api_call(matchId), "API Call"

    async def lolwasted(self):
        req = await self.run_command_riotwatcher(requests.get,f"https://wol.gg/stats/{self.userObj['gateway'].lower()}/{self.userObj['name'].lower().replace(' ','')}/")
        soup = BeautifulSoup(req.content,"html.parser")
        p = soup.find('div',id='time-hours').find('p')
        return int([x for x in p if isinstance(x,NavigableString)][0].replace(',',''))

    @staticmethod
    async def mine_champion_relation(DATABASE,championId):
        def special_lower(str):
            return str.lower().replace(' & ','-').replace(' ','-').replace("'",'').replace('.','')
        GLOBALS.chromeDriver.get(f"https://www.counterstats.net/league-of-legends/{special_lower(GLOBALS.STATICDATA['CHAMPIONS'][championId]['name'])}")
        if GLOBALS.chromeDriver.execute_script("return $('.load-more.ALL').length") == 0:
            print(f"{GLOBALS.STATICDATA['CHAMPIONS'][championId]['name']} - data collection problem")
        for i in range(40):
            GLOBALS.chromeDriver.execute_script('$(".load-more.ALL").click()')
        await asyncio.sleep(.5)
        soup = BeautifulSoup(GLOBALS.chromeDriver.page_source,"html.parser")
        def image_link_to_champId(src):
            champ = GLOBALS.lowerplus(src[src.rindex('/')+1:src.rindex('.')])
            return int(GLOBALS.STATICDATA['CHAMPIONS'][champ]['key'])
        all = {}
        def create_and_or_create_table(DATABASE, table):
            if (len(DATABASE.execute(
                    f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';").fetchall()) == 0):
                DATABASE.execute(
                    f"CREATE TABLE {table} (champId,percentage);")
            else:
                DATABASE.execute(
                    f"DELETE FROM {table}")
            DATABASE.commit()
        for datablock in soup.find_all('div',class_='champ-box__wrap'):
            src = datablock.find('img')['src']
            lane = src[src.rindex('-') + 1:src.rindex('.')].upper()
            create_and_or_create_table(DATABASE,f"CHAMPION_RELATION_{championId}_{lane}")
            for champblock in datablock.find('div',class_='champ-box ALL').find_all('a'):
                if champblock.has_attr('class'):
                    if 'radial-progress' in champblock['class']:
                        champId, perc = image_link_to_champId(champblock.find('img')['src']), float(champblock.find('span',class_='percentage').string.replace('%',''))
                    elif 'champ-box__row' in champblock['class']:
                        champId, perc = image_link_to_champId(champblock.find('img')['src']), float(champblock.find('span').string.replace('%',''))
                    DATABASE.execute(f"INSERT INTO CHAMPION_RELATION_{championId}_{lane} VALUES ({champId},{perc})")
                    if champId not in all:
                        all[champId] = []
                    all[champId].append(perc)
            DATABASE.commit()
            await asyncio.sleep(.5)
        for key in all:
            all[key] = sum(all[key])/len(all[key])
        create_and_or_create_table(DATABASE,f"CHAMPION_RELATION_{championId}_ALL")
        for champId, perc in all.items():
            DATABASE.execute(f"INSERT INTO CHAMPION_RELATION_{championId}_ALL VALUES ({champId},{perc})")
        DATABASE.commit()
    @staticmethod
    async def get_champion_strong(DATABASE,championId, pos = 'all'):
        for champId, perc in DATABASE.execute(f"SELECT * FROM CHAMPION_RELATION_{championId}_{pos.upper()} WHERE percentage < 50 ORDER BY percentage").fetchall():
            yield champId, perc
    @staticmethod
    async def get_champion_weak(DATABASE,championId, pos = 'all'):
            for champId, perc in DATABASE.execute(f"SELECT * FROM CHAMPION_RELATION_{championId}_{pos.upper()} WHERE percentage > 50 ORDER BY percentage DESC").fetchall():
                yield champId, perc
    @staticmethod
    async def get_champion_relation_compare(DATABASE,championId, championId2, pos = 'all'):
        out = [50,50]
        try:
            out[0] = DATABASE.execute(f"SELECT * FROM CHAMPION_RELATION_{championId}_{pos.upper()} WHERE champId={championId2}").fetchone()[1]
        except:
            pass
        try:
            out[1] = DATABASE.execute(f"SELECT * FROM CHAMPION_RELATION_{championId2}_{pos.upper()} WHERE champId={championId}").fetchone()[1]
        except:
            pass
        return (out[0]+100-out[1])/2
    @staticmethod
    async def get_champion_relation_compare_group(DATABASE,championId, championIds, pos = 'all'):
        return map(lambda k:k[0],DATABASE.execute(f"SELECT * FROM CHAMPION_RELATION_{championId}_{pos.upper()} WHERE percentage > 50 AND champId IN ({', '.join(map(str,championIds))})").fetchall())