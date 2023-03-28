import requests
import sqlite3

def create_base_table():
    # SQL -> Cursor
    sql_file_name = input('What do you want to name the SQL file? Please format the file as a .sqlite file (follow the name with .sqlite). Enter here: ')
    sql_table_name = input('What do you want to name the main table as in the SQL file? Enter here: ')
    conn = sqlite3.connect(sql_file_name)
    cur = conn.cursor()

    cur.executescript(f'''
    DROP TABLE IF EXISTS {sql_table_name};

    CREATE TABLE IF NOT EXISTS {sql_table_name} (
        id INTEGER NOT NULL PRIMARY KEY,
        name TEXT UNIQUE
    ) 
    ''')

    ids = []
    names = []
    while True: # Terminates when script stores all the 'ids' and 'names' of all 70,000+ Steam games
        print('Adding games to SQL table...')
        
        # Indicates the last Steam game the storing process was left off on
        if len(ids) == 0:
            last_id = 0
        else:
            last_id = ids[len(ids)-1]

        # Connects to the URL that contains the JSON text
        param = {'key': '1674C7309B00CA08D73A8CC100CA24C7', 'max_results': '50000', 'last_appid': last_id}
        url = 'https://api.steampowered.com/IStoreService/GetAppList/v1/'
        response = requests.get(url, params=param)
        print(response.url)
        print('Status Code:', response.status_code)
        response = response.json()

        # Parses the JSON text for the 'id' and 'name' of the Steam game
        try: 
            ids_names = response['response']['apps'] # [{'appid': ___, 'names': ___}, ...]
        except:
            print('Final Number of IDs:', len(ids), '\n')      
            break # Termination of while loop

        """
        Appends the 'ids' and 'names' of every Steam game to separate lists to
        later insert simultaneously into an SQLite database in its entirety
        """
        for dct in ids_names: # [{'appid': ___, 'names': ___}, ...]
            ids.append(dct['appid'])
            names.append(dct['name'])

        print('Number of IDs:', len(ids), '\n')

    id_name_tple = zip(ids, names)
    cur.executemany(f'INSERT OR IGNORE INTO {sql_table_name} VALUES (?,?)', id_name_tple)
    conn.commit()

create_base_table()