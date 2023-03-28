# Steam-API-Storefront-Web-Sraping with SQLite

This project scrapes video game data (app id, cost, release dates, active player count, etc.) from Steam's API and Steam Spy's API through HTTP requests and stores that data in a SQLite database. The purpose of this project is to reveal which video game genre is the most popular through Tableau visualizations. The generic 'genre' and 'category' descriptions that Steam provided did not suffice because they lacked information on the actual styling of the game or were so broad that nearly all games were suitable for that category. As a result, popular player tags (2D, 3D, indie, action, etc) which were created by the players themselves, were analyzed in place of Steam's categories.

Software Requirements
1. SQLite

APIs
1. Steam
2. Steam Spy

URLs
1. Game List (Steam) - https://api.steampowered.com/IStoreService/GetAppList/v1/
2. Game Details (Steam) - https://store.steampowered.com/api/appdetails/
3. List of Popular Tags (Steam) - https://store.steampowered.com/tagdata/populartags/english
4. Popular Tags of a Game - https://steamspy.com/api.php

Instructions
1. Download the most recent version of SQLite https://www.sqlite.org/download.html
2. Register for a Steam API key as it is necessary to access some APIs such as the Game List from URLs (1). This Steam API key will be one of the parameters for the URL.
3. Enter the Steam API key directly into the source code 
4. IMPORTANT! It it crucial to run the scripts in this order:
   1. base_table.py -- Creates a simple table of the appids (unique key associated with every Steam game) and the name of the game. The cost and release date of every      game will also be added to this table**
   2. Steam-parser.py -- Scrapes Steam's API for the cost and release date of every game and stores it in a SQLite database table (named by the user through input)**
   3. player_count.py -- Scrapes Steam's API for the player count of every game on an hourly basis and stores that data into a SQlite table called 'Player_Count'
   4. tags.py -- Scrapes Steam's API for a list of popular player tags and stores the data into a SQLite table called 'tags'
   5. game_tags.py -- Scrapes Steam Spy's API for the popular tags associated with a specific game
** When these scripts are ran, they will prompt for a file name for the SQLite database and a SQLite table name which should never change and be remembered

