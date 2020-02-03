import GLOBALS
import riotwatcher
import admincommands

@GLOBALS.socketio.on('update-api-key')
def update_api_key(data):
    admincommands.update_api_key(data)
    GLOBALS.RIOTWATCHER = riotwatcher.RiotWatcher(data)