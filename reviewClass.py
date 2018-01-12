#Phil Tenteromano
#Web Scraping personal project
#12/30/2017

#Game Class - game objects store data from website

class gameReview:

    def __init__(self):        #initalize object
        self.price = 'No Data'  #Price will not always have data in it, store empty unless otherwise

    def g_title(self, title):       #used to initalize data in object
        self.title = title

    def g_platform(self, platform):
        self.platform = platform

    def g_score(self, score, scorePhrase):
        self.score = score
        self.scorePhrase = scorePhrase

    def g_genre(self, genre):
        self.genre = genre

    def g_price(self, price):
        self.price = price

    def g_revDate(self, revDate):
        self.revDate = revDate

    def __str__(self):          #overloaded output operator for print
        test = ['Title: ' + self.title, 'Platform: ' + self.platform, 'Score: ' + self.score + ' ' + \
                 self.scorePhrase, 'Price: ' + self.price, 'Review Date: ' + self.revDate]

        return ' | '.join(test)

