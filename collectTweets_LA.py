import parameters
import sys
import tweepy
import config
import jsonpickle
import time

# This script collects tweets from the LA region
bounding_box = parameters.boundingBox['mapTemplate']
outfile = 'twitter_data/la_stream.json'

# set up streaming API
auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_secret)
api = tweepy.API(auth)
t0 = time.time()


class CustomStreamListener(tweepy.StreamListener):
    total_tweets = 0
    tweets_with_geolocation = 0

    def on_status(self, status):
        # possible status keys:
        # 'is_quote_status', 'in_reply_to_user_id_str', 'in_reply_to_status_id',
        # 'user', 'in_reply_to_status_id_str', 'source', 'place', 'text', 'entities',
        # 'retweet_count', 'source_url', 'geo', 'lang', 'id', 'created_at', 'favorite_count',
        # 'favorited', 'coordinates', '_api', 'in_reply_to_user_id', 'possibly_sensitive',
        # 'retweeted', 'truncated', 'timestamp_ms', 'author', '_json', 'in_reply_to_screen_name',
        # 'contributors', 'id_str', 'filter_level'])
        self.total_tweets = self.total_tweets + 1
        if status.coordinates is None:
            print(str(self.tweets_with_geolocation) + ' tweets with geolocation (' + str(self.total_tweets) +' total) over ' + str(time.time()-t0) + ' seconds')
            return True
        self.tweets_with_geolocation = self.tweets_with_geolocation + 1
        with open(outfile, 'a') as f:
            print(str(self.tweets_with_geolocation) + ' tweets with geolocation (' + str(self.total_tweets) +' total) over ' + str(time.time()-t0) + ' seconds')
            f.write(jsonpickle.encode(status._json, unpicklable=False) + '\n')
        #print(status)
        #print(status.user.name) # actual name
        #print(status.user.screen_name) # @...
        #print(status.text)
        #print(status.id_str)
        #print(status.coordinates)
        #print(status.place)
        #print(status.timestamp_ms)
        #print(status.__dict__.keys())
        return True
    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        if status_code == 420:
            return False # kill stream if exceed attempt limit to connect to stream
        return True # Don't kill the stream
    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
sapi.filter(locations=bounding_box)
