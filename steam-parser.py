import requests
import time
import json
import sqlite3

# CLEANING
# 1. Basic Cleaning (logical variable names, add/remove comments)
# 2. Add dynamic functionality so that the entire table can be made
# 3. Table Cleaning (logical table names)

# CREATING WHOLE SCRIPT
# 1. Insert column of game ids and game names
# 2. Insert column for cost and release date of each game

# Functions
def sql_update(counter, sql_table_name, column, id, value):
    print(counter, id, value)
    data = (value, id)
    sql_update_query = f'UPDATE {sql_table_name} SET {column} = ? WHERE id = ?' # STATIC SQL
    cur.execute(sql_update_query, data)

def request_pause(status_code):
    if status_code == 429:
        wait_time = 300
    else:
        wait_time = 10
    print('Status Code', status_code, '-> Pausing for', wait_time, 'seconds')
    time.sleep(wait_time)

def json_parse(response, response_url, column, id):

    if column == 'is_free':
        try:
            value = response[str(id)]['data']['is_free']
        except: 
            value = f'FREE CHECK ERROR - {response_url}'
    elif column == 'cost':
        try:
            value = response[str(id)]['data']['price_overview']['final_formatted']
        except:
            value = f'COST CHECK ERROR - {response_url}'
    elif column == 'release_date':
        try:
            value = response[str(id)]['data']['release_date']['date'][-4:]
        except:
            value = f'DATE CHECK ERROR - {response_url}'
    
    return value

def parse_n_store(sql_table_name, column, insert_number):

    try:
        cur.execute(f'ALTER TABLE {sql_table_name} ADD COLUMN {column}')
    except:
        print(f'\n----Adding values to the ({column}) column----')
        pass

    # SQL -> Pulling all data from Apps table
    table = cur.execute(f'SELECT * FROM {sql_table_name} ORDER BY id ASC')
    rows = cur.fetchall()

    col_names = [description[0] for description in table.description]
    
    row_count = 1
    for row in rows: # rows consist a list of tuples [(id, name, cost, release_date)]

        id = row[col_names.index('id')]
        value = row[col_names.index(column)] # returns either the cost or release_date value

        # Python -> Pick up where the iterator left off
        if value is None:
            pass
        else:
            continue

        # Python -> Iterator Limit
        if row_count > insert_number:
            insert_number = input("Would you like to insert more data? If yes, insert a number. If not, type 'No'. Enter here: ")
            try:
                insert_number = int(insert_number)
                row_count = 1
                continue
            except:
                while True:
                    if insert_number != 'No':
                        insert_number = input("You must insert a number or the word 'No', try again. Enter here: ")
                    else:
                        break
                break

        # Python -> URL Connection
        param = {'appids': id}
        url = 'https://store.steampowered.com/api/appdetails/'
        response = requests.get(url, params=param)

        # Python -> Check if the steam API restricted my access
        while response.status_code != 200:
            request_pause(response.status_code)
            response = requests.get(url, params=param)
        response_url = response.url
        response = response.json()

        # Python + SQL -> Parses for the value and updates the SQL table
        if column == 'cost':
            value = json_parse(response, response_url, 'is_free', id) # checks if an app is free to avoid checking for price
            if value is True:
                value = '$0.00'
            else:
                value = json_parse(response, response_url, column, id)
        else:
            value = json_parse(response, response_url, column, id)

        sql_update(row_count, sql_table_name, column, id, value)

        row_count += 1

    conn.commit()





# Handling User Input Errors
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

column = input('What data are you trying to retrieve (cost, release_date)? Enter here: ') # cost or release_date
while True:
    if column not in ['cost', 'release_date']:
        column = input('You have not selected one of the two available options (cost / release_date), try again. Enter here: ')
    else:
        break

insert_number = int(input('How many data points do you want to retrieve and insert in this session? The Steam API limits requests to 200 requests every 5 minutes. Enter here: ')) # only numbers
while True:
    try:
        insert_number % 1
        break
    except:
        insert_number = int(input('Please insert a number, try again. Enter here: '))
        
conn = sqlite3.connect(sql_file_name)
cur = conn.cursor()

parse_n_store(sql_table_name, column, insert_number) 