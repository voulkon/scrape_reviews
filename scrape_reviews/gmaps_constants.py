# -*- coding: utf-8 -*-

from scrape_reviews.categories_of_interest import GoogleMapsCategories
import os.path as path

FOUND_IN_ATTRIBUTES = {

    'reviewer':'aria-label',
    'data-review-id': 'data-review-id'

}

FOUND_IN_CLASSES = {

    'text_of_review' :'wiI7pd',
    'date_created' : 'xRkPPb',
    'reviewer': 'd4r55',
    'reviewers_no_of_reviews':'RfnDt',
    'rating':'fzvQIb'

}

INFO_DICTIONARY = {

        'Name' : 'qBF1Pd',
        'Overall_Rating':'MW4etd',
        'Number_of_Ratings':'UY7F9'

    }


#Depends on the download speed of the server
GENERAL_WAIT_TIME = 1.5
CLASS_OF_REVIEW_CONTAINER = "jftiEf"
CLASS_OF_REVIEWS_BUTTON = "DkEaL" #"hh2c6.G7m0Af" #""
REVIEWS_WINDOWS_CLASS = "#QA0Szd > div > div > div.w6VYqd > div.bJzME.Hu9e2e.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf"
CLASS_OF_CATEGORIES_OF_INTEREST_BUTTONS = "KNfEk.Rqu0ae"

ENTITIES_BASE_XPATH_INIT = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[{to_be_confirmed}]/div[1]'

CLASS_OF_STARS = 'kvMYJc'

#The Button to Click in order to Avoid Cookies Screen and procceed with the actul website
COOKIES_XPATH = '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[1]/div/div/button'

PARENT_XPATH_OF_CATEGORIES = '//*[@id="assistive-chips"]/div/div/div/div[1]/div/div/div/div/div[5]/div[2]'

XPATH_OF_EACH_CATEGORY = {
    '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[{to_be_confirmed}]/div[1]' : GoogleMapsCategories.HOTELS,
    '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[{to_be_confirmed}]' : GoogleMapsCategories.RESTAURANTS
    }


# #For future reference - not used for now
# with open(f"{path.dirname(path.abspath(__file__)) }/greek_stopwords.txt","r", encoding = "utf-8") as f:
#     greek_stopwords = f.readlines()