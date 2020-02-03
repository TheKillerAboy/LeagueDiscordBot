from discord.ext import commands, tasks
import sqlite3
from flask import Flask
from flask_socketio import SocketIO
import riotwatcher

RIOTWATCHER = None
STATICDATA = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

TOKEN = 'NjcwMDEyMTMyNDk0MTQ3NjA2.XiodYQ.dc_F7q8Kq69cCsvD9kgZFhJRXAs'

client = commands.Bot(command_prefix='.')

DATABASE = sqlite3.connect('CONFIG.db')

def init_riotwatcher(DATABASE):
    global RIOTWATCHER, STATICDATA
    RIOTWATCHER = riotwatcher.RiotWatcher(DATABASE.execute("SELECT * FROM RIOT_API WHERE Attr = \"API-KEY\"").fetchone()[1])
    STATICDATA = {'VERSION':RIOTWATCHER.data_dragon.versions_for_region('euw1')['dd']}
    STATICDATA['CHAMPIONS'] = RIOTWATCHER.data_dragon.champions(STATICDATA['VERSION'])['data']
    dummy = {}
    for champId, champ in STATICDATA['CHAMPIONS'].items():
        champ['lower-name'] = lowerplus(champ['name'])
        dummy[int(champ['key'])] = champ
        dummy[champ['lower-name']] = champ
    STATICDATA['CHAMPIONS'].update(dummy)

def lowerplus(str):
    return str.lower().replace(' ','').replace("'",'').replace('&','').replace('.','').replace('-','')

init_riotwatcher(DATABASE)
chromeDriver = None