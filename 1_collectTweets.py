# This script collects tweets from the LA region

# Parameters

# Bounding box of tweet search in [SWlongitude, SWLatitude, NElongitude, NELatitude]
# on google maps, syntax is: latitude-y, longitude-x
box=[-118.323898,33.090246,-118.156357,34.043628]
# number of grid boxes in bounding box
sz_x = 10
sz_y = 15
# when to stop search
max_tweets = 10

# Script
import sys
import tweepy
import config

auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_secret)
api = tweepy.API(auth)



class CustomStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print(status.text)

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream


for x in range(sz_x):
    for y in range(sz_y):
        sw_longitude = box[0] + (box[2]-box[0])*x/(sz_x-1)
        sw_latitude  = box[1] + (box[3]-box[1])*y/(sz_y-1)
        print(str(sw_longitude) + ', ' + str(sw_latitude))

sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
sapi.filter(locations=box)
