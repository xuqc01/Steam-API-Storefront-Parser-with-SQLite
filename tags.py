import requests
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
DROP TABLE IF EXISTS tags;

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    tag_name TEXT
);

''')

url = 'https://store.steampowered.com/tagdata/populartags/english'
response = requests.get(url)

print(response.url)
print('Status Code', response.status_code)

for i in response.json():
    tagid = i['tagid']
    name = i['name']
    cur.execute('INSERT INTO tags (id, tag_name) VALUES (?, ?)', (tagid, name))

conn.commit()

