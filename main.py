import os
from importlib import reload
import importlib
import liveCommands
import functools
from threading import Thread
from GLOBALS import *
from socketio_stuff import *

def reload_method():
    def wrapper(func):
        @functools.wraps(func)
        async def method(*args,**kwargs):
            reload(liveCommands)
            await getattr(liveCommands, func.__name__)(DATABASE,client,*args,**kwargs)
        wrapper.__name__ = func.__name__
        return method
    return wrapper

@client.command(pass_context=True)
@reload_method()
async def lolsetinfo(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def lolhelp(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def lolprofile(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def lolprofilefull(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def lolprofileplus(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def lollivematch(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def lollivematchplus(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def lolchampion(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def lolchampionfull(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def lolchampionplus(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def deletemessages(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def lolmonitor(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def lolwasted(ctx):
    pass

@client.command(pass_context=True)
@reload_method()
async def lolchampions(ctx):
    pass
@client.command(pass_context=True)
@reload_method()
async def lolchampionsplus(ctx):
    pass
@client.command(pass_context=True)
@reload_method()
async def lolchampionsfull(ctx):
    pass
@client.command(pass_context=True)
@reload_method()
async def lolchampionweak(ctx):
    pass
@client.command(pass_context=True)
@reload_method()
async def lolchampionstrong(ctx):
    pass
@client.command(pass_context=True)
@reload_method()
async def lolchampionweakpos(ctx):
    pass
@client.command(pass_context=True)
@reload_method()
async def lolchampionstrongpos(ctx):
    pass
@client.command(pass_context=True)
@reload_method()
async def lolminerelationdata(ctx):
    pass


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

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

import_all_routes()

appthread = Thread(target=socketio.run,args=(app,),kwargs={"host":"192.168.2.12","port":8445})
appthread.start()
client.run(TOKEN)
