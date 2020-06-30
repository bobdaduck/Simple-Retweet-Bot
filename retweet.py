# DezNat Retweet bot for Twitter, using Python and Tweepy.
# by bobdaduck, modifying "simple retweet bot"'s source on github.Author: Tyler L. Jones || CyberVox
# Resources: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object
# http://docs.tweepy.org/en/latest/api.html?highlight=search

import tweepy #let python handle the twitter api stuff
import datetime
from time import sleep
from keys import *

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True) # "api" variable now calls whatever twitter api you give it, like on line 17

seconds_between_retweets = 5
minimum_account_age = 7 #in days
minimum_account_follower = 15 #in followers

def meetsRetweetConditions(tweet): #filter out trolls
    if tweet.user.id in blocked_users:
        return False

    account_age = datetime.datetime.now() - tweet.user.created_at
    if account_age.days < minimum_account_age: #less than a week old
        print(tweet.user.screen_name + "new, or low-clout.  Evaluate and RT manually.  Tweet ID (to paste): " + str(tweet.id))
        return False

    if tweet.user.followers_count < minimum_account_follower: #fewer than 15 followers
        print(tweet.user.screen_name + "new, or low-clout.  Evaluate and RT manually.  Tweet ID (to paste): " + str(tweet.id))
        return False
 
    return True

searched_store = [] #cut down on log printing after first iteration by memorizing what we've retweeted
while True: #run infinitely until aborted
    blocked_users = api.blocks_ids()
    for tweet in tweepy.Cursor(api.search, q='#DezNat OR #deznat OR #Deznat', count=100).items(100): #q= search query, items = max items to try
        try:
            if(tweet.id not in searched_store): #save CPU time if we already saw this since last time we started the bot
                searched_store.append(tweet.id)
                if(tweet.in_reply_to_user_id not in blocked_users): #don't drag us into your nonsense
                    if(hasattr(tweet, "retweeted_status") == False): #tweet is an original tweet
                        print("new tweet found by " + tweet.user.screen_name + ", tweet ID: " + str(tweet.id))
                        #print("has attribute retweeted status: " + str(hasattr(tweet, "retweeted_status")))
                        if(meetsRetweetConditions(tweet)): #Not blocked, new, or low-clout
                            tweet.retweet() #if its already retweeted, this gives 327 error and moves on
                            print('\nretweeted tweet by @' + tweet.user.screen_name + '. Tweet ID: ' + str(tweet.id))
                            sleep(seconds_between_retweets) #halt bot process for 10 seconds
                    else:
                        pass #print("Not an original tweet")
                elif(tweet.user.id not in blocked_users):
                    print(tweet.user.screen_name + "is replying to a troll, skipping.  tweet ID: " + str(tweet.id))
                    pass #print(str(tweet.user.screen_name) + " FOUND ON BLOCK LIST, IGNORE HIM")
        
        except tweepy.TweepError as error:
            if("327" not in error.reason): #327 = already retweeted.  
                print('\nError. Retweet not successful: ' + error.reason)
            else:
                pass #already retweeted error
        except StopIteration:
            break
    print("loop finished, waiting to retry")
    sleep(120) #halt bot process for X seconds



