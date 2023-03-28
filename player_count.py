import requests
import time as t
import sqlite3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor




# Functions

# This function pulls data from Steam's API on an hourly basis and inserts the number of active players for every game into the SQL database
def run_automatic_update(ids, threads):

    now = datetime.now()
    monthddyy = now.strftime('%B_%d_%Y') # March_02_2023
    time_w_colon = now.strftime('%H:%M') # 23:57

    now = datetime.now()
    monthddyy = now.strftime('%B_%d_%Y') # March_02_2023
    time_w_colon = now.strftime('%H:%M') # 23:57
    
    monthtime = str(monthddyy) + '_' + ''.join(str(time_w_colon).split(':')) # March_02_2023_2357, This will be the name of the column

    # Updates the values in the dictionary of id - player_count pairs
    with ThreadPoolExecutor(threads) as executor:
        _ = [executor.submit(retrieve_n_update, id) for id in ids]

    # SQL -> Updates the player_count in the SQL table
    update_sql(ids, id_playercount, monthtime)

# This function pulls the player count from Steam's API and inserts it into a dictionary {'id': 'player_count'}
def retrieve_n_update(id):
    # Creates a URL to connect to
    param = {'appid': id}
    url = 'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?'
    response = requests.get(url, params=param)

    player_count = retrieve_playercount(response.json(), response.url)
    update_dct(id, player_count)

# This function simply pulls the player count from Steam's API
def retrieve_playercount(response, response_url):
    try:
        player_count = response['response']['player_count']
    except:
        player_count = f'PLAYER COUNT ERROR - {response_url}'
    return player_count

# This function updates the dictionary with the player count
def update_dct(id, player_count):
    print(id, player_count)
    id_playercount[id] = player_count

def make_empty_dct(ids):
    id_playercount = {}
    # Creates a 'NULL' playercount value for each id in the dct
    for id in ids:
        id_playercount[id] = None

    return id_playercount

# This function inserts the player count into the SQL table with their respective game ids
def update_sql(ids, id_playercount, monthtime):
    cur.execute(f'ALTER TABLE Player_Count ADD COLUMN {monthtime}')
    for id in ids:
        player_count = id_playercount[id] # This dictionary search ensures that each id in the database receives the correct player count
        cur.execute(f'UPDATE Player_Count SET {monthtime} = ? WHERE id = ?', (player_count, id))
        conn.commit()

def time_to_int(time):
    hh, mm = map(int, time.split(':'))
    return hh * 60 + mm





# SQL -> SQL Connection
sql_file_name = input('What was the name of the SQL file that you created from before? (followed by .sqlite) Enter here: ') # .sqlite'
while True:
    if sql_file_name.endswith('.sqlite'):
        break
    else:
        sql_file_name = input('The file name did not end with .sqlite, try again. Enter here: ')

sql_table_name = input('What was the name of the main table you created from before? Enter here: ') # no numbers, must have underscore for multiple words
while True:
    if any(char.isdigit() for char in sql_table_name):
        sql_table_name = input('Your table name has a number in it. This is unfortunately not allowed, try again. Enter here: ')
    elif sql_table_name.find(' ') != -1:
        sql_table_name = input('Your table name has a space. Use an underscore instead, try again. Also, try not to use any special characters. Enter here: ')
    else:
        break

threads = int(input('How many threads do you want to use? Threads will determine how quickly you want to pull data. CAUTION: The higher the threads, the more CPU required. Enter here: '))

conn = sqlite3.connect(sql_file_name)
cur = conn.cursor()

# Creates a new table to track active player count
try:
    cur.executescript(f'''
    CREATE TABLE Player_Count AS
        SELECT
            id,
            name
        FROM
            {sql_table_name}
    ''')
except:
    pass

# Creating an dictionary of ids and empty player coutns
cur.execute('SELECT * FROM Player_Count ORDER BY id ASC')
rows = cur.fetchall()
id_index = 0
ids = [row[id_index] for row in rows]
id_playercount = make_empty_dct(ids) # The ids and player counts will be inserted into this dictionary

i = 1
hour_runs = input('How many times do you want to pull active player counts for each game? Each run will take at least an hour depending on the current time. Enter here: ')
while i <= int(hour_runs):
    start_time = t.time()
    run_automatic_update(ids, threads)
    print('Session', i, '-> Transferred data in', t.time()-start_time, 'seconds')
    t.sleep(60)
    i += 1
