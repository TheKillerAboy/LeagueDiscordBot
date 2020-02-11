from database import Database
import config.config as config
import utils.meyCryptography as crypt
import SECRETS.secrets as secrets

def num_of_stored_matches():
    DATABASE = Database('CONFIG.db')
    total = 0
    for accountId, time in DATABASE.execute("SELECT * FROM LEAGUE_USERS").fetchall():
        total += len(DATABASE.execute(f"SELECT * FROM LEAGUE_USER_{accountId}").fetchall())
    return total

def num_of_stored_accounts():
    DATABASE = Database('CONFIG.db')
    return len(DATABASE.execute("SELECT * FROM LEAGUE_USERS").fetchall())

def delete_duplicates(table_name):
    DATABASE = Database('CONFIG.db')
    all = set(DATABASE.execute(f"SELECT * FROM {table_name}").fetchall())
    DATABASE.execute(f"DELETE FROM {table_name}")
    def strk(val):
        if type(val) is str:
            return f'"{val}"'
        else:
            return val
    for data in all:
        DATABASE.execute(f"INSERT INTO {table_name} VALUES ({', '.join(map(strk,data))})")
    DATABASE.commit()
    DATABASE.close()

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