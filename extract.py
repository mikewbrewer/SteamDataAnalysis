import mysql.connector
import requests
import re

from time import sleep
from random import randint
from bs4 import BeautifulSoup
from password import PASSWORD



# Pull the html from steam and extract relevant data
# continuously writes that data using mySQL to pythondatabase
# because of how the website's html is written, only 50 titles from each
# genre can be extracted without manually triggering some javascript on
# each page.

def extract(_cursor, _db):
    GENRE_KEYS = {
        'Action': '19',
        'Adventure': '21',
        'Casual': '597',
        'Indie': '492',
        'MMO': '128',
        'Racing': '699',
        'RPG': '122',
        'Simulation': '599',
        'Sports': '701',
        'Strategy': '9'
    }


    # Creates new game_titles table if it doesn't already exist
    try:
        _cursor.execute("""
            CREATE TABLE game_titles (
                game_id INT AUTO_INCREMENT,
                title VARCHAR(100),
                price DECIMAL(5, 2),
                genre VARCHAR(15),
                discount VARCHAR(1),
                release_year INT DEFAULT NULL,
                PRIMARY KEY (game_id)
            )
            """
        )
    except:
        print ('Table already created')


    # each loop is for a different page request from Steam.com
    for genre in GENRE_KEYS:
        # generate desired url for the request
        my_url = 'https://store.steampowered.com/search/?filter=topsellers&tags=' + GENRE_KEYS[genre]

        # set up html link with BeautifulSoup
        page = requests.get(my_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        # container for all games on given page
        games_list = soup.find(id='search_resultsRows')
        game_container = games_list.findAll("div", {"class":"responsive_search_name_combined"})

        # iterate over each game in the game_container
        for game in game_container[0:200]:
            # extract title from html
            title = game.find(class_='title').get_text()

            # extract price from html
            price_container = game.find("div", {"class": "col search_price_discount_combined responsive_secondrow"})
            if (price_container.find("div", {"class": "col search_price discounted responsive_secondrow"})):
                temp = price_container.find("div", {"class": "col search_price discounted responsive_secondrow"}).text.strip()
                temp2 = temp.rsplit('$', 1)
                price = temp2[0][1:]
                price2 = temp2[1]
                discount = 'Y'
            else:
                price = price_container.text.strip()[1:]
                price2 = ''
                discount = 'N'

            # make sure price is a number, matter if listed as 'Free to Play'
            if not(re.search('[0-9]$', price)):
                price = 0

            # extract year released from html
            year = game.find(class_='col search_released responsive_secondrow').get_text()
            if not(year == '') and not('/' in year):
                year = year[-4:]
                # write to database
                _cursor.execute("""
                    INSERT INTO game_titles
                    (title, price, genre, discount, release_year)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (title, price, genre, discount, year)
                )
            else:
                # write to database
                _cursor.execute("""
                    INSERT INTO game_titles
                    (title, price, genre, discount)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (title, price, genre, discount)
                )

            # commit the changes to the database
            _db.commit()



if __name__ == '__main__':
    # if run on it's own, this connects the script to the database
    mydb = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        passwd = PASSWORD,
        database = 'pythondatabase',
        auth_plugin = 'mysql_native_password'
    )
    my_cursor = mydb.cursor()

    extract(my_cursor, mydb)
