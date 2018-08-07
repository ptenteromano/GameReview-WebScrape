#Phil Tenteromano
#Web Scraping personal project
#12/30/2017

#Using Python 3.6
#Program fetches data from the HTML on the most recent IGN Game reviews page
#Relevant data includes [title, platform, score, scorePhrase, price, ReviewDate] //6 total
#Stores this data in a fresh database (:memory:)
#Also writes to a locally created csv file 'games.csv'

import requests         #used to fetch url and HTTP request
from bs4 import BeautifulSoup   #parsing module
import sqlite3          #used to create the database
from reviewClass import gameReview      #self-made Class to store data into an object
import csv              #used to write to csv file

#link to the website, use browser headers to connect
url = "http://www.ign.com/reviews/games"            #target URL
headers = requests.utils.default_headers()          #get default request headers, update accordingly
headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
})

r = requests.get(url, headers=headers)          #Request and assign proper header to the request
print("Status Code: ",r.status_code)            #Make sure connection code is 200: good connection

if r.status_code != 200:            #proper connection is critical to functioning program
    exit(2)

#parse the website content
soup = BeautifulSoup(r.content, "lxml")         #Using 'lxml' parser instead of the default 'html parser'
#styled = soup.prettify()                       #Can be used to print HTML in styled format

#connect to the sqlite database
dataB = sqlite3.connect(':memory:')     #dynamically create a fresh database
c = dataB.cursor()       #creates a position in the database

#primary database table for the gameReviews
c.execute("""CREATE TABLE gameReviews   (
         title text,
         platform text,
         score real,
         price text,
         review_date text
         )""")      #docstring allows for styled table creation

dataB.commit()      #commit to database

#Database functions for insert, retrieve, and delete game reviews
def insert_game(game_obj):
    float(game_obj.score)       #convert the score into a float for easier retrieval
    with dataB:
        c.execute("INSERT INTO gameReviews VALUES \
                 (:title, :platform, :score, :price, :review_date)",
                  {'title':game_obj.title, 'platform':game_obj.platform,
                   'score':game_obj.score, 'price':game_obj.price,
                   'review_date':game_obj.revDate})

#returns the entire tuple set of game Reviews
def get_game_list():
    c.execute("SELECT * FROM gameReviews")
    return c.fetchall()

#returns the entire tuple when searching by title
def get_game_by_title(title):
    c.execute("SELECT * FROM gameReviews WHERE title=:title", \
              {'title': title})
    return c.fetchall()

#returns the title and platform of the games with that score
def get_game_by_score(scoreSearch):
    float(scoreSearch)              #make sure the score is a float
    c.execute("SELECT title, platform FROM gameReviews WHERE score=:score",
              {'score':scoreSearch})
    return c.fetchall()

#Delete a game by the title
def remove_game(title):
    with dataB:
        c.execute("DELETE FROM gameReviews WHERE title=:title", \
              {'title': title})

def getAvgByPlat(plat):
    c.execute("SELECT AVG(score) FROM gameReviews WHERE platform=:plat",{'plat':plat})
    return c.fetchall()

def getMinByPlat(plat):
    c.execute("SELECT MIN(score) FROM gameReviews WHERE platform=:plat",{'plat':plat})
    return c.fetchall()

def getMaxByPlat(plat):
    c.execute("SELECT MAX(score) FROM gameReviews WHERE platform=:plat",{'plat':plat})
    return c.fetchall()

def getNumGamesByPlat(plat):
    c.execute("SELECT COUNT(title) FROM gameReviews WHERE platform=:plat",{'plat':plat})
    return c.fetchall()

#Start the program after status code 200
print("Let's see the reviews for the latest games from IGN.com:\n")

#find the primary div tags separating each game review
gameData = soup.find_all("div", {'clear itemList-item'})

currentGame = gameReview()      #create gameReview object, used over iteration

filename = "games.csv"      #also store the data on a file
f = open(filename, "a", newline='')         #open file in write mode
# update -- now in append mode to keep adding data

#create top column names, use CSV module 
# Commented 2 lines out to avoid re-writing titles
# headColumns = ['Title', 'Platform', 'Genre', 'Price','Score']
# writer.writerow(headColumns)    #write the heading sections to the file

writer = csv.writer(f)          #instantiate 'writer' object

#primary iterating for loop, retrieves, prints, writes, and stores data
for game in gameData:       #go through each game review, find data accordingly
    #title, platform, and game are in their own tags, find and store
    currentGame.g_title(game.h3.a.text.strip())         #strip() gets rid of leading/trailing whitespace
    currentGame.g_platform(game.h3.span.text.strip())
    currentGame.g_genre(game.find('span',{'class':"item-genre"}).text.strip())

    #Not all games have a price, make sure sentinel value is absent
    priceCheck = (game.find('span', {'class': 'details'}).text)
    if "%displayPrice%" not in priceCheck:      #presence of sentinel value, continue on
        currentGame.g_price(priceCheck)         #else, store price
    # needed lambda to find correct HTML tag
    currentGame.g_revDate(game.find(lambda tag: tag.name == 'div'     #[1:-1] for date, HTML stored unused '\n'
                            and tag.get('class') == ['grid_3']).text[1:-1]) #on the lead and trail of the text
    numScore = game.find('span',{'class':'scoreBox-score'}).text        #store the score
    phraseScore = game.find('span',{'class':'scoreBox-scorePhrase'}).text   #score the scorePhrase directly below it
    currentGame.g_score(numScore, phraseScore)              #combine these values into the g_score attribute

    #begin insertion into the database, with complete currentGame object
    insert_game(currentGame)    #insert every iteration into the database

    print(currentGame)      #print complete currentGame as they come, used __str__() in class file
    #begin writing to the CSV file
    writer.writerow([currentGame.title, currentGame.platform, \
             currentGame.genre, currentGame.price, currentGame.revDate.replace(',', ' '), \
             currentGame.score + ' ' + currentGame.scorePhrase])

#show use of database functions
print("\nFinding all instances of 'Rocket League'!\n")
print(get_game_by_title('Rocket League'))   #get game by title
print("\nGetting game List!\n")
print(get_game_list())                      #get entire list
print("\nFinding Games with score of '7'!\n")
print(get_game_by_score(9.5),'\n')          #get games by score
remove_game('Rocket League')                #delete all instances of 'Rocket League'
print("\nDeleting all instances of Rocket League. Searching again...'!\n")
print(get_game_by_title('Rocket League'))   #shows up as empty list!

platforms = ("PlayStation 4", "PC", "Xbox One", "Nintendo Switch", "PlayStation Vita")

for plat in platforms:
    if getNumGamesByPlat(plat)[0][0] > 0: 
        print("AVG OF", plat, "Through", getNumGamesByPlat(plat)[0][0], "games:")
        x = getAvgByPlat(plat)
        y = ("%.2f" % x[0][0])                      # hundredths decimal precision
        print(y)



f.close()           #close the csv file
dataB.close()       #close the database

#done
print("\nEnd")
