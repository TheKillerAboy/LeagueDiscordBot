import os
from importlib import reload
import importlib
import liveCommands
import functools
from threading import Thread
import GLOBALS
from utils import meyCryptography
import SECRETS.secrets as secrets

def reload_method():
    def wrapper(func):
        @functools.wraps(func)
        async def method(*args,**kwargs):
            reload(liveCommands)
            await getattr(liveCommands, func.__name__)(GLOBALS.client,*args,**kwargs)
        wrapper.__name__ = func.__name__
        return method
    return wrapper

async def data_mine_all_relation_regualar():
    while True:
        liveCommands.lol

def import_module_all(module):
    mdl = importlib.import_module(module)
    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        names = [x for x in mdl.__dict__ if not x.startswith("_")]
    globals().update({k: getattr(mdl, k) for k in names})

def import_all_routes():
    for file in os.listdir('routes'):
        try:
            file, ext = file[:file.rindex('.')],file[file.rindex('.'):]
        except:
            continue
        if ext == '.py':
            import_module_all(f'routes.{file}')

def flask_server_setup():
    # GLOBALS.socketio.run(GLOBALS.app,**{"host":"192.168.2.12","port":8445})
    GLOBALS.app.run()

password = input("Password: ")

if not meyCryptography.is_correct_password(password, secrets.get_secret('password')):
    print("incorrect Password")
    exit()

discord_token = meyCryptography.decrypt(password,secrets.get_secret('discord_token'))
riot_api_key = meyCryptography.decrypt(password,secrets.get_secret('riot_api_key'))


GLOBALS.main(riot_api_key)
import_all_routes()
appthread = Thread(target=flask_server_setup)
appthread.start()

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolsetinfo(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolhelp(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolprofile(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolprofilefull(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolprofileplus(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lollivematch(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lollivematchplus(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolchampion(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolchampionfull(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolchampionplus(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def deletemessages(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolmonitor(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolwasted(ctx):
    pass

@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolchampions(ctx):
    pass
@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolchampionsplus(ctx):
    pass
@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolchampionsfull(ctx):
    pass
@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolchampionweak(ctx):
    pass
@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolchampionstrong(ctx):
    pass
@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolchampionweakpos(ctx):
    pass
@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolchampionstrongpos(ctx):
    pass
@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolminerelationdata(ctx):
    pass
@GLOBALS.client.command(pass_context=True)
@reload_method()
async def lolminerelationdatasingle(ctx):
    pass

@GLOBALS.client.event
async def on_ready():
    print('Logged in as')
    print(GLOBALS.client.user.name)
    print(GLOBALS.client.user.id)
    print('------')

GLOBALS.client.run(discord_token)