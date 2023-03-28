import requests
import json
import sqlite3




sql_file_name = input('\nWhat was the name of the SQL file that you created from before? (followed by .sqlite) Enter here: ') # .sqlite'
while True:
    if sql_file_name.endswith('.sqlite'):
        break
    else:
        sql_file_name = input('The file name did not end with .sqlite, try again. Enter here: ')

conn = sqlite3.connect(sql_file_name)
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS game_tags;

CREATE TABLE game_tags (
    game_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY(game_id, tag_id),
    FOREIGN KEY(game_id) REFERENCES Games2(id),
    FOREIGN KEY(tag_id) REFERENCES tags(id)
);

''')

# Getting the column name of the player count as it varies depending on the day and time of day
table = cur.execute('SELECT * FROM Player_Count')
col_names = [description[0] for description in table.description]
player_count_col_name = col_names[2]
print(player_count_col_name)

table = cur.execute(f'SELECT * FROM Player_Count WHERE TYPEOF({player_count_col_name}) = "integer" AND {player_count_col_name} > 20 ')
rows = cur.fetchall()

for row in rows:
    game_id = row[0]

    # URL Connection
    url = 'https://steamspy.com/api.php'
    param = {'request': 'appdetails', 'appid': game_id}
    response = requests.get(url, params=param)
    print('Status Code:', response.status_code, response.url)

    print('Game ID:', game_id)

    tags = response.json()['tags']
    for tag_name in tags:
        cur.execute('SELECT id FROM tags WHERE tag_name = (?)', (tag_name,))
        tag_id = cur.fetchone()

        if tag_id is None:
            continue
        tag_id = tag_id[0]
        
        cur.execute('INSERT INTO game_tags (game_id, tag_id) VALUES (?, ?)', (game_id, tag_id))
        print('INSERTED', game_id, tag_id)
    
conn.commit()