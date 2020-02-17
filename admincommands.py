from database import Database
import config.config as config
import utils.meyCryptography as crypt
import SECRETS.secrets as secrets

def num_of_stored_matches():
    DATABASE = Database('CONFIG.db')
    return DATABASE.execute('SELECT count(*) FROM LEAGUE_MATCHES_TEMP').fetchone()[0]

def num_of_stored_accounts():
    DATABASE = Database('CONFIG.db')
    return DATABASE.execute('SELECT count(distinct(accountId)) FROM LEAGUE_MATCHES_TEMP').fetchone()[0]

def update_riot_api_key(password,api_key):
    secrets.set_secret('riot_api_key',crypt.encrypt(password,api_key))

def update_discord_token(password,token):
    secrets.set_secret('discord_token',crypt.encrypt(password,token))

def update_password(password):
    secrets.set_secret('password',crypt.get_hash(password))
    discord = input('Discord Token:')
    update_discord_token(password,discord)
    riot = input('Riot API key:')
    update_riot_api_key(password,riot)

def change_password(oldpassword,password):
    secrets.set_secret('password',crypt.get_hash(password))
    discord = crypt.decrypt(oldpassword,secrets.get_secret('discord_token'))
    update_discord_token(password,discord)
    riot = crypt.decrypt(oldpassword,secrets.get_secret('riot_api_key'))
    update_riot_api_key(password,riot)