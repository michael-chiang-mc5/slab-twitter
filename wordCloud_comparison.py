# http://sebastianraschka.com/Articles/2014_twitter_wordcloud.html
#from wordcloud import WordCloud, STOPWORDS
from MCWordCloud import WordCloud, STOPWORDS
import json
import time
import parameters
import matplotlib.pyplot as plt
import scipy.stats as stats
import copy
import pickle
import re
import sys

# Only do pairwise comparisons on these cities
#cityNames = [cityName for cityName in parameters.boundingBox.keys() if cityName != 'mapTemplate']
cityNames = [cityName for cityName in parameters.boundingBox.keys()]
#cityNames = cityNames[0:2]
#cityNames = ['compton','mapTemplate']

# extra stopwords
stopwords_extra = ['']
STOPWORDS = STOPWORDS.union(stopwords_extra)

# read all tweets into list
# TODO: filter careerArc, job, etc.
t0=time.time()
tweets = []
with open('twitter_data/la_stream.json', 'r') as f:
    for line in f:
        tweet = json.loads(line)
        tweets.append(tweet)

# initialize wordCloud object
wC = WordCloud(
                      font_path='/Users/mcah5a/Library/Fonts/CabinSketch-Bold.ttf',
                      stopwords=STOPWORDS,
                      background_color='black',
                      width=1800,
                      height=1400
                     )

def removeTrailingS(word):
    if word.endswith('s') or word.endswith('S'):
        return word[:-1]
    else:
        return word


# assemble word list for all cities
words_byCity = dict()
for cityName in cityNames:
    boundingBox = parameters.boundingBox[cityName]
    # filter tweets based on bounding box
    tweets_filtered = [tweet for tweet in tweets if tweet['geo']['coordinates'][1] > boundingBox[0] and \
                                                    tweet['geo']['coordinates'][1] < boundingBox[2] and \
                                                    tweet['geo']['coordinates'][0] > boundingBox[1] and \
                                                    tweet['geo']['coordinates'][0] < boundingBox[3] \
                                                    ]
    # list of words
    words = " ".join([tweet['text'] for tweet in tweets_filtered])
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
    words4=[word for word in re.findall(r"\w[\w']+", words3, flags=flags) if not word.isdigit() ]
    # remove trailing s to account for plural
    words5 = " ".join([removeTrailingS(word) for word in words4])
    # count word frequencies
    word_frequencies = dict(wC.MCprocess_text(words5)) # process_text will remove stopwords
    # store
    words_byCity[cityName] = word_frequencies


t1=time.time()
print('Time to assemble word list for all cities: ' + str(t1-t0) + ' seconds')

# do pairwise comparison between cities
# chi2 matrix should look like this:
#           pizza   not_pizza
# city1     m11     m12
# city2     m21     m22
# Output:
# pairwise_chi2_matrix[cityName1][cityName2][word] = dictionary with pvalue, rate1, rate2
pairwise_chi2_matrix = dict()
bonferonni_correction = (len(words_byCity.keys())+1)*len(words_byCity.keys())/2 - len(words_byCity.keys())
for cityName1, words1 in words_byCity.items():
    pairwise_chi2_matrix[cityName1] = dict()
    t0=time.time()
    for cityName2, words2 in words_byCity.items():
        if cityName1 == cityName2:
            continue
        try:
            pairwise_chi2_matrix[cityName1][cityName2] = pairwise_chi2_matrix[cityName2][cityName1]
            # flip rates
            for word_comparison_info in pairwise_chi2_matrix[cityName1][cityName2]:
                temp = word_comparison_info['rate1']
                word_comparison_info['rate1'] = word_comparison_info['rate2']
                word_comparison_info['rate2'] = temp
            continue
        except:
            wordlist1 = [word for word,freq in words_byCity[cityName1].items()]
            wordlist2 = [word for word,freq in words_byCity[cityName2].items()]
            combined_wordlist =  list(set(wordlist1).union(wordlist2))
            total_words1 = sum([freq for word,freq in words_byCity[cityName1].items()])
            total_words2 = sum([freq for word,freq in words_byCity[cityName2].items()])
            word_comparison_info = dict()
            for word in combined_wordlist:
                try:
                    m11 = words_byCity[cityName1][word]
                except:
                    m11 = 0
                try:
                    m21 = words_byCity[cityName2][word]
                except:
                    m21 = 0
                m12 = total_words1 - m11
                m22 = total_words2 - m21
                contingency_matrix = [[m11, m12], [m21, m22]]

                # TODO: throw out m11 and m22 < 5
                # fisher_exact is slow
                #oddsratio, pvalue = stats.fisher_exact(contingency_matrix)
                chi2, pvalue, dof, ex = stats.chi2_contingency(contingency_matrix, correction=False)

                word_comparison_info[word] = {'pvalue':pvalue*bonferonni_correction,'rate1':m11/(m11+m12),'rate2':m21/(m21+m22),'contingency_matrix':contingency_matrix}
            t1=time.time()
            pairwise_chi2_matrix[cityName1][cityName2] = word_comparison_info
    print('Time to do ' + cityName1 + ': ' + str(t1-t0) + ' seconds')

# save work
output = open('wordcloud_comparison.pkl', 'wb')
pickle.dump(pairwise_chi2_matrix, output)
output.close()
