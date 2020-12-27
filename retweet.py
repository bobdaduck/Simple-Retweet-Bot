# DezNat Retweet bot for Twitter, using Python and Tweepy.
# by bobdaduck, modifying "simple retweet bot"'s source on github.Author: Tyler L. Jones || CyberVox
# Resources: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object
# http://docs.tweepy.org/en/latest/api.html?highlight=search

import tweepy #let python handle the twitter api stuff
import datetime
import fileinput
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
timesLooped = 0
blockedAttempts = 0
mutedReplies = 0
repliesToTrolls = 0
sessionDate = str(datetime.datetime.now())

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
    if('#exmormon' in fullText or '#exmo' in fullText or ' mormons' in fullText or 'deznats' in fullText or 'nuts' in fullText or 'deez' in fullText or 'a mormon' in fullText or 'blocked me' in fullText):
        global blockedAttempts
        blockedAttempts = blockedAttempts + 1
        return True
    else:
        return False

def containsYellowFlagWords(tweet):   #fine but spammy
    fullText = str(api.get_status(tweet.id, tweet_mode="extended").full_text).lower()
    if("#iglesiadejesucristo" in fullText):
        return True
    elif('#nacdes' in fullText):
        return True
    elif('#escúchalo' in fullText):
        return True
    elif(fullText.count('#') > 6):
        return True
    else:
        return False
def containsRedFlagBio(tweet):
    bio = tweet.user.description.lower()
    if("utes" in bio or "jazz" in bio or "exmo" in bio or "he/him" in bio or "she/her" in bio or "they/them" in bio or "feminist" in bio or "queer" in bio or " ally" in bio or "onlyfans" in bio):
        return True
def isNotAThread(tweet):
    replyTo = tweet.in_reply_to_status_id
    replyText = ""
    if(replyTo is not None):#don't retweet every hashtag in a 50 tweet thread where all have the hashtag
        
        replyText = str(api.get_status(replyTo, tweet_mode="extended").full_text).lower() #"extended" gets full text rather than 40 chars of each tweet
        if('#deznat' in replyText):
            #print("above tweet already tagged #DezNat, skipping @" + tweet.user.screen_name + "'s tweet: " + str(tweet.id))
            #print(replyText + "\n")
            return False
    return True

def meetsRetweetConditions(tweet): #filter out trolls
    if tweet.user.id in blocked_users:
        return False
    if tweet.user.id in muted_users:
        return False
    
    if(not isGreenFlaggedAccount(tweet)):
        account_age = datetime.datetime.now() - tweet.user.created_at
        if account_age.days < minimum_account_age: #less than a week old
            print("~~~~~~~@" + tweet.user.screen_name + "\a new or low-clout.  Evaluate and RT manually.  Tweet ID (to paste): " + str(tweet.id))
            print(tweet.text+ "\n") #/n just means newline
            return False
        if tweet.user.followers_count < minimum_account_follower: #fewer than 40 followers
            print("~~~~~~~@" + tweet.user.screen_name + "\a new or low-clout.  Evaluate and RT manually.  Tweet ID (to paste): " + str(tweet.id))
            print(tweet.text + "\n")
            return False
        if(containsRedFlagWords(tweet)):
            print("~~~~~~~ @" + tweet.user.screen_name + "\a using red flag language. Tweet ID (to paste): " + str(tweet.id) + " ~~~~~")
            return False
        if(containsYellowFlagWords(tweet)):
            print("~~~~~~~ @" + tweet.user.screen_name + "\a using yellow flag language. Tweet ID (to paste): " + str(tweet.id) + " ~~~~~")
            return False
        if(containsRedFlagBio(tweet)):
            print("~~~~~~~ @" + tweet.user.screen_name + "\a otherwise fine but has red flags in Bio: Tweet ID (to paste): " + str(tweet.id) + " ~~~~~")
            global mutedReplies
            mutedReplies += 1
            return False
    
    return True

def EvaluateAndRetweet(tweet):
    if(tweet.id not in searched_store): #save CPU time if we already saw this since last time we started the bot
        searched_store.append(tweet.id)
        if(tweet.in_reply_to_user_id not in blocked_users and tweet.in_reply_to_user_id not in muted_users): #don't drag us into your nonsense
            if(hasattr(tweet, "retweeted_status") == False): #tweet is an original tweet
                #print("new tweet found by " + tweet.user.screen_name + ", tweet ID: " + str(tweet.id))
                #print("has attribute retweeted status: " + str(hasattr(tweet, "retweeted_status")))
                if(meetsRetweetConditions(tweet) and isNotAThread(tweet)): #Not blocked, new, or low-clout
                    tweet.retweet() #if its already retweeted, this gives 327 error and moves on
                    print('retweeted tweet by @' + tweet.user.screen_name + '. Tweet ID: ' + str(tweet.id))
                    print(tweet.text  + "\n")
                    incremintMetrics(tweet)
                    sleep(seconds_between_retweets) #halt bot process for 10 seconds
                elif(isGreenFlaggedAccount(tweet) and isNotAThread(tweet)):
                    tweet.retweet() #if its already retweeted, this gives 327 error and moves on
                    print("\n- - - - @" + tweet.user.screen_name + " is a low follower account we've greenflagged- - - -")
                    print('retweeted tweet by @' + tweet.user.screen_name + '. Tweet ID: ' + str(tweet.id))
                    print(tweet.text  + "\n")
                    incremintMetrics(tweet)
                    sleep(seconds_between_retweets) #halt bot process for 10 seconds
                elif(tweet.user.id in muted_users):
                    global mutedReplies
                    mutedReplies = mutedReplies + 1
                    print("!!!!!!!!!!!!! " + tweet.user.screen_name + "\a is muted.  Consider blocking or unmuting. tweet ID: " + str(tweet.id) + " !!!!!!!!\n")
                elif(tweet.user.id in blocked_users):
                    global blockedAttempts
                    blockedAttempts = blockedAttempts + 1
                    #print(tweet.user.screen_name + " is blocked")
        
        elif(tweet.user.id not in blocked_users and tweet.user.id not in muted_users):
            global repliesToTrolls
            repliesToTrolls = repliesToTrolls + 1
            #print(tweet.user.screen_name + " is replying to a troll, skipping.  tweet ID: " + str(tweet.id) + "\n") #/n just means newline
            pass #print(str(tweet.user.screen_name) + " FOUND ON BLOCK LIST, IGNORE HIM")
following_list = []
searched_store = [] #cut down on log printing after first iteration by memorizing what we've retweeted

f = open("trends.csv", "a") #set newline on file up before the loop runs
f.write("\n" + sessionDate + " || authors: " + str(uniqueAuthors) + ", total retweets: " + str(uniqueTweets))
f.close()

while True: #run infinitely until aborted
    blocked_users = api.blocks_ids()
    muted_users = api.mutes_ids()
    following_list = api.friends_ids()
    for tweet in tweepy.Cursor(api.search, q='#DezNat OR #deznat OR #Deznat', count=100).items(100): #q= search query, items = max items to try
        try:
            EvaluateAndRetweet(tweet)
        except tweepy.TweepError as error:
            errCode = error.api_code
            if(errCode == 327): #327 = already retweeted. #503 = server down
                pass
            elif(errCode == 136):
                print(tweet.user.screen_name + " has blocked us, consider blocking back to cut down on these messages (ID:) " + str(tweet.id))
                #this part also is triggered if the reply tweet is blocked, idk
            else:
                print(error.api_code)  
                print('\n%%%%%%%Error. Retweet for @' + tweet.user.screen_name + ' failed: ' + error.reason)
                print('tweet ID: ' + str(tweet.id))
        except StopIteration:
            break
    print("loop finished, waiting to retry. Since startup, " + str(uniqueAuthors) + " unique authors and " + str(uniqueTweets) + " retweets")

    lines = open('trends.csv').read().splitlines()
    lines[-1] =  sessionDate + ", " + str(uniqueAuthors) + ", " + str(uniqueTweets)+ ", " + str(timesLooped) + ", " + str(blockedAttempts) + ", " + str(repliesToTrolls) + ", " + str(mutedReplies)
    open('trends.csv','w').write('\n'.join(lines))
    
    timesLooped = timesLooped + 1
    sleep(120) #halt bot process for X seconds