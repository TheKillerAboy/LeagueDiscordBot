import GLOBALS
from flask import render_template

@GLOBALS.app.route('/leaguebot')
def leaguebot():
    return render_template('discord_league_bot.html')

@GLOBALS.app.route('/leaguebot/updateapi')
def leaguebot_updateapi():
    return render_template('discord_league_bot_updateapi.html')