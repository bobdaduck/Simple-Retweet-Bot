# Retweet bot for Twitter, using Python and Tweepy.
# Search query via hashtag or keyword.
# Author: Tyler L. Jones || CyberVox
# Date: Saturday, May 20th - 2017.
# License: MIT License.

import tweepy
import datetime
from time import sleep
# Import in your Twitter application keys, tokens, and secrets.
# Make sure your keys.py file lives in the same directory as this .py file.
from keys import *

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

hashtag = '#DezNat'
# amount of tweets fetched per call and seconds between retweets
maximum_tweets_per_call = 12
seconds_between_retweets = 5
# debug mode no retweets send to account
testing = True
# account threshold
minimum_account_age = 7
minimum_account_follower = 15
date_since = "2020-06-21"

blocked_users = api.blocks_ids() 

def meetsRetweetConditions(tweet): #Not blocked, new, or low-clout
    if tweet.user.id in blocked_users:
        return False

    account_age = datetime.datetime.now() - tweet.user.created_at
    if account_age.days < minimum_account_age:
        return False

    if tweet.user.followers_count < minimum_account_follower:
        return False

    return True

last_id = "1273780338662178816" #some tweet on July 19th just to keep things recent
last_date = ""
searched_store = []
while True:

    for tweet in tweepy.Cursor(api.search, q='#DezNat OR #deznat OR #Deznat', count=100).items(100): #q= search query, items = max items to try
       
        #print("now more recent than " + str(last_date))
        try:
            if(tweet.id not in searched_store): #save CPU time if we already saw this since last time we started the bot
                searched_store.append(tweet.id)
                if(tweet.user.id not in blocked_users): 
                    if(hasattr(tweet, "retweeted_status") == False): #tweet is an original tweet
                        #print("has attribute retweeted status: " + str(hasattr(tweet, "retweeted_status")))
                        if(meetsRetweetConditions(tweet)): #Not blocked, new, or low-clout
                            tweet.retweet()
                            print('\nretweeted tweet by @' + tweet.user.screen_name + '. Tweet ID: ' + str(tweet.id))
                            sleep(seconds_between_retweets) #halt bot process for 10 seconds
                        else:
                            print(tweet.user.screen_name + "blocked, new, or low-clout.  Evaluate and RT manually.  Tweet ID (to paste): " + str(tweet.id))
                    else:
                        pass #print("Not an original tweet")
                else:
                    pass #print(str(tweet.user.screen_name) + " FOUND ON BLOCK LIST, IGNORE HIM")
        
        except tweepy.TweepError as error:
            if("327" not in error.reason):
                print('\nError. Retweet not successful: ' + error.reason)
            else:
                pass #already retweeted error
        except StopIteration:
            break
    print("loop finished, waiting to retry")
    sleep(120) #halt bot process for 60 seconds



