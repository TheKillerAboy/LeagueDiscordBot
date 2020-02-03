import sqlite3

def update_api_key(api_key):
    DATABASE = sqlite3.connect('CONFIG.db')
    DATABASE.execute(f"UPDATE RIOT_API SET Value='{api_key}' WHERE Attr='API-KEY'")
    DATABASE.commit()
    DATABASE.close()

def num_of_stored_matches():
    DATABASE = sqlite3.connect('CONFIG.db')
    total = 0
    for accountId, time in DATABASE.execute("SELECT * FROM LEAGUE_USERS").fetchall():
        total += len(DATABASE.execute(f"SELECT * FROM LEAGUE_USER_{accountId}").fetchall())
    return total

def num_of_stored_accounts():
    DATABASE = sqlite3.connect('CONFIG.db')
    return len(DATABASE.execute("SELECT * FROM LEAGUE_USERS").fetchall())

def delete_duplicates(table_name):
    DATABASE = sqlite3.connect('CONFIG.db')
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