from discord.ext import commands, tasks
from flask import Flask
from flask_socketio import SocketIO
import riotwatcher
from database import Database

RIOTWATCHER = None
STATICDATA = None
app = None
socketio = None
client = None
DATABASE = None
chromeDriver = None


def init_riotwatcher(riot_api_key):
    global RIOTWATCHER, STATICDATA
    RIOTWATCHER = riotwatcher.RiotWatcher(riot_api_key)
    STATICDATA = {'VERSION':RIOTWATCHER.data_dragon.versions_for_region('euw1')['dd']}
    STATICDATA['CHAMPIONS'] = RIOTWATCHER.data_dragon.champions(STATICDATA['VERSION'])['data']
    dummy = {}
    for champId, champ in STATICDATA['CHAMPIONS'].items():
        champ['lower-name'] = lowerplus(champ['name'])
        dummy[int(champ['key'])] = champ
        dummy[champ['lower-name']] = champ
    STATICDATA['CHAMPIONS'].update(dummy)
    STATICDATA['SUMMONER_SPELLS'] = RIOTWATCHER.data_dragon.summoner_spells(STATICDATA['VERSION'])['data']
    dummy = {}
    for spellId, spell in STATICDATA['SUMMONER_SPELLS'].items():
        spell['lower-name'] = lowerplus(spell['name'])
        dummy[int(spell['key'])] = spell
        dummy[spell['lower-name']] = spell
    STATICDATA['SUMMONER_SPELLS'].update(dummy)

def lowerplus(str):
    return str.lower().replace(' ','').replace("'",'').replace('&','').replace('.','').replace('-','')

def main(riot_api_key):
    global RIOTWATCHER,STATICDATA,app,socketio,client,DATABASE,chromeDriver
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    socketio = SocketIO(app)
    client = commands.Bot(command_prefix='.')
    DATABASE = Database('CONFIG.db')
    init_riotwatcher(riot_api_key)