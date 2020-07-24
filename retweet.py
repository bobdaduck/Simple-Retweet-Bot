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
minimum_account_follower = 40 #in followers

#metrics
authorsToday= []

uniqueAuthors = 0
uniqueTweets = 0

def incremintMetrics(tweet):
    global uniqueAuthors
    global uniqueTweets
    if(tweet.user.screen_name not in authorsToday):
        authorsToday.append(tweet.user.screen_name)
        uniqueAuthors += 1
    uniqueTweets += 1

def isGreenFlaggedAccount(tweet): 
    #accounts we follow get retweeted even if they're low clout
    if(tweet.user.id in following_list):
        return True
    else:
        return False

def containsRedFlagWords(tweet):
    fullText = str(api.get_status(tweet.id, tweet_mode="extended").full_text).lower()
    if('#exmormon' in fullText or 'mormons' in fullText or 'the mormons' in fullText or 'deznats' in fullText):
        return True
    elif('#nacdes' in fullText): #fine but spammy
        return True
    else:
        return False

def meetsRetweetConditions(tweet): #filter out trolls
    if tweet.user.id in blocked_users:
        return False

    if tweet.user.id in muted_users:
        return False

    if(containsRedFlagWords(tweet)):
        print("~~~~~~~@" + tweet.user.screen_name + " using no-no language. Tweet ID (to paste): " + str(tweet.id) + "~~~~~")
        return False

    if(not isGreenFlaggedAccount(tweet)):
        account_age = datetime.datetime.now() - tweet.user.created_at
        if account_age.days < minimum_account_age: #less than a week old
            print("~~~~~~~@" + tweet.user.screen_name + " new or low-clout.  Evaluate and RT manually.  Tweet ID (to paste): " + str(tweet.id))
            print(tweet.text+ "\n") #/n just means newline
            return False

        if tweet.user.followers_count < minimum_account_follower: #fewer than 15 followers
            print("~~~~~~~@" + tweet.user.screen_name + " new or low-clout.  Evaluate and RT manually.  Tweet ID (to paste): " + str(tweet.id))
            print(tweet.text + "\n")
            return False
    
        replyTo = tweet.in_reply_to_status_id
        replyText = ""
        if(replyTo is not None):#don't retweet every hashtag in a 50 tweet thread where all have the hashtag
            
            replyText = str(api.get_status(replyTo, tweet_mode="extended").full_text).lower() #"extended" gets full text rather than 40 chars of each tweet
            if('#deznat' in replyText):
                print("above tweet already tagged #DezNat, skipping @" + tweet.user.screen_name + "'s tweet: " + str(tweet.id))
                print(replyText + "\n")
                return False
        return True

following_list = []
searched_store = [] #cut down on log printing after first iteration by memorizing what we've retweeted
while True: #run infinitely until aborted
    blocked_users = api.blocks_ids()
    muted_users = api.mutes_ids()
    following_list = api.friends_ids()
    for tweet in tweepy.Cursor(api.search, q='#DezNat OR #deznat OR #Deznat', count=100).items(100): #q= search query, items = max items to try
        try:
            if(tweet.id not in searched_store): #save CPU time if we already saw this since last time we started the bot
                searched_store.append(tweet.id)
                if(tweet.in_reply_to_user_id not in blocked_users and tweet.in_reply_to_user_id not in muted_users): #don't drag us into your nonsense
                    if(hasattr(tweet, "retweeted_status") == False): #tweet is an original tweet
                        #print("new tweet found by " + tweet.user.screen_name + ", tweet ID: " + str(tweet.id))
                        #print("has attribute retweeted status: " + str(hasattr(tweet, "retweeted_status")))
                        if(meetsRetweetConditions(tweet)): #Not blocked, new, or low-clout
                            tweet.retweet() #if its already retweeted, this gives 327 error and moves on
                            print('retweeted tweet by @' + tweet.user.screen_name + '. Tweet ID: ' + str(tweet.id))
                            print(tweet.text  + "\n")
                            incremintMetrics(tweet)
                            sleep(seconds_between_retweets) #halt bot process for 10 seconds
                        elif(isGreenFlaggedAccount(tweet)):
                            tweet.retweet() #if its already retweeted, this gives 327 error and moves on
                            print("\n- - - - @" + tweet.user.screen_name + " is a low follower account we've greenflagged- - - -")
                            print('retweeted tweet by @' + tweet.user.screen_name + '. Tweet ID: ' + str(tweet.id))
                            print(tweet.text  + "\n")
                            incremintMetrics(tweet)
                            sleep(seconds_between_retweets) #halt bot process for 10 seconds
                        else:
                            pass
                    else:
                        pass #print("Not an original tweet")
                elif(tweet.user.id not in blocked_users and tweet.user.id not in muted_users):
                    print(tweet.user.screen_name + " is replying to a troll, skipping.  tweet ID: " + str(tweet.id) + "\n") #/n just means newline
                    pass #print(str(tweet.user.screen_name) + " FOUND ON BLOCK LIST, IGNORE HIM")
                else:
                    pass
        except tweepy.TweepError as error:
            if("327" not in error.reason): #327 = already retweeted.  
                print('\n~~~~Error. Retweet for @' + tweet.user.screen_name + ' failed: ' + error.reason)
                print('tweet ID: ' + str(tweet.id))
            else:
                pass #already retweeted error
        except StopIteration:
            break
    print("loop finished, waiting to retry. Since startup, " + str(uniqueAuthors) + " unique authors and " + str(uniqueTweets) + " retweets")
    sleep(120) #halt bot process for X seconds



