# http://sebastianraschka.com/Articles/2014_twitter_wordcloud.html
from wordcloud import WordCloud, STOPWORDS
import json
import time
import parameters
import matplotlib.pyplot as plt

boundingBox = parameters.boundingBox['pasadena']

# read all tweets into list
t0=time.time()
#lon=[]
#lat=[]
#words = ''
tweets = []
with open('twitter_data/la_stream.json', 'r') as f:
    for line in f:
        tweet = json.loads(line)
        tweets.append(tweet)
        #print(tweet['place']) # this is the location of the TWEET
        #print(tweet['user']['location']) # this is self reported user location
        #print(tweet['id_str']) # unique ID for tweet
        #print(tweet['user']['name']) # self reported name of user
        #print(tweet['user']['screen_name']) # twitter handle (ex: @realDonaldTrump )
        #print(tweet['user']['geo_enabled']) # whether or not user has enabled geolocation
        #words += tweet['text'].replace('\n', '')
        #words += ' '

# filter tweets
tweets_filtered = [tweet for tweet in tweets if tweet['geo']['coordinates'][1] > boundingBox[0] and \
                                                tweet['geo']['coordinates'][1] < boundingBox[2] and \
                                                tweet['geo']['coordinates'][0] > boundingBox[1] and \
                                                tweet['geo']['coordinates'][0] < boundingBox[3] \
                   ]

# list to string
words = " ".join([tweet['text'] for tweet in tweets_filtered])

# sanitize
words = " ".join([word for word in words.split()
                            if 'http' not in word
                                and not word.startswith('@')
                                and word != 'RT'
                                and word != '-&gt;' # greater than sign
                            ])
t1=time.time()
print('Time to assemble word list: ' + str(t1-t0) + ' seconds')


t0=time.time()
wordcloud = WordCloud(
                      font_path='/Users/mcah5a/Library/Fonts/CabinSketch-Bold.ttf',
                      stopwords=STOPWORDS,
                      background_color='black',
                      width=1800,
                      height=1400
                     ).generate(words)
t1=time.time()
print('Time to assemble word cloud: ' + str(t1-t0) + ' seconds')

plt.imshow(wordcloud)
plt.axis('off')
plt.savefig('./my_twitter_wordcloud_1.png', dpi=300)
plt.show()
