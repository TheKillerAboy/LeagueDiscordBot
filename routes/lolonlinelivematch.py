import GLOBALS
from flask import render_template
import RiotDataMine
import sqlite3
import asyncio

@GLOBALS.app.route('/lolonlinelivematch/<league_name>/<gateway>')
def lolonlinelivematch(league_name, gateway):
    DATABASE = sqlite3.connect('CONFIG.db')
    print(league_name,gateway)
    riotuser = RiotDataMine.RiotUser(DATABASE,league_name,gateway)
    loop = asyncio.new_event_loop()
    partiData = loop.run_until_complete(riotuser._livegame_get_livegame_info(loop))
    for parti in partiData:
        parti['spell_name_1'] = GLOBALS.STATICDATA['SUMMONER_SPELLS'][parti['spell1Id']]['id']
        parti['spell_name_2'] = GLOBALS.STATICDATA['SUMMONER_SPELLS'][parti['spell2Id']]['id']
        parti['champion_name'] = GLOBALS.STATICDATA['CHAMPIONS'][parti['championId']]['id']
    return render_template('league_live_match_online.html', partiData = partiData)