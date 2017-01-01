# http://sebastianraschka.com/Articles/2014_twitter_wordcloud.html
from wordcloud import WordCloud, STOPWORDS
import json
import time
import parameters
import matplotlib.pyplot as plt
import scipy.stats as stats
import copy

# Only do pairwise comparisons on these cities
cityNames = ['sanGabriel','rowlandHeights','irvine','westminster','compton',
             'santaMonica','beverlyHills','glendale','pasadena','arcadia','azusa',
             'claremont','pomona','chino','newportBeach','ontario','glendora','longBeach',
             'ranchoPalosVerde',]
# extra stopwords
stopwords_extra = ['']
STOPWORDS = STOPWORDS.union(stopwords_extra)

# TODO: filter careerArc, job, etc.






# read all tweets into list
t0=time.time()
tweets = []
with open('twitter_data/la_stream.json', 'r') as f:
    for line in f:
        tweet = json.loads(line)
        tweets.append(tweet)

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
    # list to string
    words = " ".join([tweet['text'] for tweet in tweets_filtered])
    # sanitize
    words = " ".join([word.lower() for word in words.split()
                                if 'http' not in word
                                    and not word.startswith('@')
                                    and word != 'RT'
                                    and word != '-&gt;' # greater than sign
                                ])
    # count word frequencies
    wC = WordCloud(
                          font_path='/Users/mcah5a/Library/Fonts/CabinSketch-Bold.ttf',
                          stopwords=STOPWORDS,
                          background_color='black',
                          width=1800,
                          height=1400
                         )
    word_frequencies = dict(wC.process_text(words)) # process_text will remove stopwords
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
t0=time.time()
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
                oddsratio, pvalue = stats.fisher_exact([[m11, m12], [m21, m22]])
                word_comparison_info[word] = {'pvalue':pvalue*bonferonni_correction,'rate1':m11/(m11+m12),'rate2':m21/(m21+m22)}
            t1=time.time()
            pairwise_chi2_matrix[cityName1][cityName2] = word_comparison_info
    print('Time to do ' + cityName1 + ': ' + str(t1-t0) + ' seconds')

# filter
p_threshold = 0.05*bonferonni_correction
pairwise_chi2_matrix_filtered = copy.deepcopy(pairwise_chi2_matrix)
for cityName1 in cityNames:
    for cityName2 in cityNames:
        try:
            word_comparison_info1 = pairwise_chi2_matrix[cityName1][cityName2]
            word_comparison_info2 = [x for x in word_comparison_info1.items() if x[1]['pvalue'] < p_threshold]
            pairwise_chi2_matrix_filtered[cityName1][cityName2] = dict(word_comparison_info2)
        except:
            pass

# display word cloud

for cityName1 in cityNames:
    for cityName2 in cityNames:
        keywords = pairwise_chi2_matrix_filtered['compton']['pasadena'].keys()
        for keyword in keywords:
             word_comparison_info = pairwise_chi2_matrix_filtered['compton']['pasadena'][keyword]
             word_comparison_info[color] = 'r'

# put in red green colors
keywords = [x for  x in word_comparison_info  ]
for x in keywords:
    print(x)

sorted_word_comparison_info = sorted(word_comparison_info.items(),key=lambda x: x[1]['pvalue'])
print( [word[0] for word in sorted_word_comparison_info] )



# print
word_comparison_info = pairwise_chi2_matrix_filtered['sanGabriel']['rowlandHeights']
sorted_word_comparison_info = sorted(word_comparison_info.items(),key=lambda x: x[1]['pvalue'])
print( [word[0] for word in sorted_word_comparison_info] )
