import json
import time
import pickle

# Bounding box for map display.
# A helpful tool for obtaining bounding box coordinates: http://boundingbox.klokantech.com/
# westlimit, eastlimit are longitudinal boundaries
# northlimit, southlimit are latitudinal boundaries
# copy paste to bounding box: westlimit= -118.475189, southlimit= 33.594603, eastlimit= -117.745972, northlimit= 34.162386
westlimit   =  -118.55134
southlimit  = 33.535371
eastlimit   = -117.524278
northlimit  = 34.267232

boundingBox={}
boundingBox['mapTemplate'] = [westlimit,southlimit,eastlimit,northlimit]
boundingBox['sanGabriel'] = [-118.120808, 34.071114, -118.077206, 34.115318]
boundingBox['rowlandHeights'] = [-117.930396, 33.959029, -117.850188, 34.000562]
boundingBox['irvine'] = [-117.870041, 33.599523, -117.678463, 33.774477]
boundingBox['westminster'] = [-118.043095, 33.720017, -117.944667, 33.773616]
boundingBox['compton'] = [-118.263659, 33.863086, -118.179962, 33.923418]
boundingBox['santaMonica'] = [-118.55134, 33.966674, -118.443426, 34.05056]
boundingBox['beverlyHills'] = [-118.427041, 34.052666, -118.372027, 34.112432]
boundingBox['glendale'] = [-118.307849, 34.118761, -118.182005, 34.267232]
boundingBox['pasadena'] = [-118.198139, 34.117037, -118.065479, 34.251905]
boundingBox['arcadia'] = [-118.069388, 34.087007, -117.99145, 34.179453]
boundingBox['azusa'] = [-117.943592, 34.106734, -117.881345, 34.168206]
boundingBox['claremont'] = [-117.750793, 34.07941, -117.677745, 34.165319]
boundingBox['pomona'] = [-117.828817, 34.018512, -117.711067, 34.112936]
boundingBox['chino'] = [-117.735889, 33.925014, -117.599585, 34.047811]
boundingBox['newportBeach'] = [-117.988741, 33.535371, -117.78349, 33.67192]
boundingBox['ontario'] = [-117.683588, 33.975213, -117.524278, 34.09281]
boundingBox['glendora'] = [-117.890037, 34.105475, -117.793532, 34.178607]
boundingBox['longBeach'] = [-118.248966, 33.690593, -118.063253, 33.885459]
boundingBox['ranchoPalosVerde'] = [-118.418691, 33.721862, -118.301, 33.79547]


def importTweets():
    tweets = []
    with open('twitter_data/la_stream.json', 'r') as f:
        for line in f:
            tweet = json.loads(line)
            tweets.append(tweet)
    return tweets


def checkLastName(name,surnames):
    name_withCase = name
    name = name.lower()
    # space
    lastName = name.split()[-1]
    if lastName in surnames:
        return True
    # underscore
    lastName = name.split('_')[-1]
    if lastName in surnames:
        return True
    # dash
    lastName = name.split('-')[-1]
    if lastName in surnames:
        return True
    # capital
    lastName = ''.join( ' '+x if x.isupper() else x for x in name_withCase ).split()[-1].lower()
    if lastName in surnames:
        return True
    # else
    return False

def filterTweetsByBoundingBox(tweets,boundingBox):
    tweets_filtered = [tweet for tweet in tweets if tweet['geo']['coordinates'][1] > boundingBox[0] and \
                                                    tweet['geo']['coordinates'][1] < boundingBox[2] and \
                                                    tweet['geo']['coordinates'][0] > boundingBox[1] and \
                                                    tweet['geo']['coordinates'][0] < boundingBox[3] \
                                                    ]
    return tweets_filtered

# race should be: white, black, asian, native, or hispanic
def filterTweetsByRace(tweets,race):
    # load mapping of last name to ethnicity
    t0=time.time()
    pkl_file = open('pickle_files/ethnicity_by_lastName.pkl', 'rb')
    surnames_byRace = pickle.load(pkl_file)
    pkl_file.close()
    t1=time.time()
    print('Time to load ethnicity_by_lastName.pkl: ' + str(t1-t0) + ' seconds')


    # get tweets by race
    t0=time.time()
    tweets_filtered = [ tweet for tweet in tweets if checkLastName(tweet['user']['name'],surnames_byRace[race]) ]
    t1=time.time()
    print('Time to get ' + race + ' tweets: ' + str(t1-t0) + ' seconds')

    # return
    return tweets_filtered

def removeTrailingS(word):
    if word.endswith('s') or word.endswith('S'):
        return word[:-1]
    else:
        return word

def tweetsToCorpus(tweets,depluralize=True):
    # initialize wordCloud object
    from MCWordCloud import STOPWORDS
    import sys
    import re

    # list of words
    #for tweet in tweets:
    #    print("***")
    #    print(tweet)
    #    print(tweet['text'])

    words = " ".join([tweet['text'] for tweet in tweets])
    words2 = words.split()
    # sanitize
    words3 = " ".join([word.lower() for word in words2
                                if 'http' not in word
                                    and not word.startswith('@')
                                    and word != 'RT'
                                    and word != '-&gt;' # greater than sign
                                    and word.lower() not in STOPWORDS
                                ])
    # sanitize more
    flags = (re.UNICODE if sys.version < '3' and type(text) is unicode
             else 0)
    words4=[word for word in re.findall(r"\w[\w']+", words3, flags=flags) if not word.isdigit() and word not in STOPWORDS]
    # remove trailing s to account for plural # TODO: use more sophisticated method
    if depluralize:
        words4 = " ".join([removeTrailingS(word) for word in words4])
    return words4

def corpusToWordcount(corpus):
    from MCWordCloud import WordCloud
    wC = WordCloud(
                          font_path='/Users/mcah5a/Library/Fonts/CabinSketch-Bold.ttf',
                          background_color='black',
                          width=1800,
                          height=1400
                         )
    word_frequencies = dict(wC.MCprocess_text(corpus)) # process_text will remove stopwords
    return word_frequencies

# generate a wordcloud from a single text corpus (no comparison)
def wordcountToWordcloud(count,save_name):
    from MCWordCloud import WordCloud, STOPWORDS
    import matplotlib.pyplot as plt
    # initialize wordCloud object
    wC = WordCloud(
                          font_path='/Users/mcah5a/Library/Fonts/CabinSketch-Bold.ttf',
                          background_color='black',
                          width=1800,
                          height=1400
                         )
    wC.generate_from_frequencies(count.items())
    plt.imshow(wC)
    plt.axis('off')
    plt.savefig(save_name, dpi=300)

def compareWordcount(wordcount1,wordcount2):
    import scipy.stats as stats
    wordlist1 = [word for word,freq in wordcount1.items()]
    wordlist2 = [word for word,freq in wordcount2.items()]
    combined_wordlist =  list(set(wordlist1).union(wordlist2))
    total_words1 = sum([freq for word,freq in wordcount1.items()])
    total_words2 = sum([freq for word,freq in wordcount2.items()])
    word_comparison_info = dict()

    for word in combined_wordlist:
        try:
            m11 = wordcount1[word]
        except:
            m11 = 0
        try:
            m21 = wordcount2[word]
        except:
            m21 = 0
        m12 = total_words1 - m11
        m22 = total_words2 - m21
        contingency_matrix = [[m11, m12], [m21, m22]]
        # TODO: throw out m11 and m22 < 5
        # fisher_exact is slow
        #oddsratio, pvalue = stats.fisher_exact(contingency_matrix)
        chi2, pvalue, dof, ex = stats.chi2_contingency(contingency_matrix, correction=False)
        word_comparison_info[word] = {'pvalue':pvalue,'rate1':m11/(m11+m12),'rate2':m21/(m21+m22),'contingency_matrix':contingency_matrix}
    return word_comparison_info

def plotMap(tweets,save_name):
    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap

    # load map template
    try:
        t0=time.time()
        pkl_file = open('pickle_files/map_template.pkl', 'rb')
        fig = pickle.load(pkl_file)
        pkl_file.close()
        t1=time.time()
        print('Time to load map_template.pkl: ' + str(t1-t0) + ' seconds')
    except:
        print('map_template.pkl not found, try runnning createMapTemplate.py?')
        return

    # create basemap object to plot points
    t0=time.time()
    themap = Basemap(projection='merc',
                  llcrnrlon = westlimit,              # lower-left corner longitude, westlimit
                  llcrnrlat = southlimit,               # lower-left corner latitude, southlimit
                  urcrnrlon = eastlimit,               # upper-right corner longitude, eastlimit
                  urcrnrlat = northlimit,               # upper-right corner latitude, northlimit
                  resolution = 'c',         # Can be c (crude), l (low), i (intermediate), h (high), f (full) or None
                  #area_thresh = 100000.0,
                  )
    t1=time.time()
    print('Time to create basemap ' + str(t1-t0) + ' seconds')

    # get tweets to plot
    lon=[]
    lat=[]
    if tweets is not None:
        for tweet in tweets:
            latitude = tweet['geo']['coordinates'][0]
            longitude = tweet['geo']['coordinates'][1]
            lat.append(latitude)
            lon.append(longitude)

    # plot
    t0=time.time()
    x, y = themap(lon, lat)
    themap.plot(x, y,
                'o',                    # marker shape
                color='red',         # marker colour
                markersize=2            # marker size
                )
    t1=time.time()
    print('Time to plot lon, lat: ' + str(t1-t0) + ' seconds')
    #plt.show()

    # save
    plt.savefig(save_name, dpi=300)

    # return
    return
