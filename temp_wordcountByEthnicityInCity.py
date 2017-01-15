

####

import pickle
import parameters
from importlib import reload
pkl_file = open('pickle_files/tweets_byEthnicity.pkl', 'rb')
tweets_byEthnicity = pickle.load(pkl_file)
pkl_file.close()

# modify this
#tweets1 = tweets_byEthnicity['asian']
#tweets2 = tweets_byEthnicity['white'] + tweets_byEthnicity['asian'] + tweets_byEthnicity['hispanic']
ethnicity='asian'
city='mapTemplate'
tweets1 = parameters.filterTweetsByBoundingBox(tweets_byEthnicity[ethnicity],parameters.boundingBox[city])
tweets2 = parameters.filterTweetsByBoundingBox(tweets_byEthnicity['white'] + tweets_byEthnicity['asian'] + tweets_byEthnicity['hispanic'],parameters.boundingBox[city])


corpus_1=parameters.tweetsToCorpus(tweets1)
corpus_2 = parameters.tweetsToCorpus(tweets2)
wordcount_1=parameters.corpusToWordcount(corpus_1)
wordcount_2= parameters.corpusToWordcount(corpus_2)

word_comparison_info1 = parameters.compareWordcount(wordcount_1, wordcount_2)
print("*****")
print("length tweets1 = " + str(len(tweets1)))
print("length tweets2 = " + str(len(tweets2)))
word_comparison_info2 = [x for x in word_comparison_info1.items() if x[1]['pvalue'] < 0.05 \
                                                     and (x[1]['contingency_matrix'][0][0] >= 0 \
                                                      or x[1]['contingency_matrix'][1][0] >= 0 \
                                                      )
]

eps = 0.01
for x in word_comparison_info2:
    rate_ratio = max ((x[1]['rate1']+eps)/(x[1]['rate2']+eps) , (x[1]['rate2']+eps)/(x[1]['rate1']+eps))
    if x[1]['rate1'] > x[1]['rate2']:
        bigger = 1
    else:
        bigger = 2
    x[1]['rate_ratio'] = rate_ratio
    x[1]['bigger'] = bigger

sorted_frequencies_p = sorted(word_comparison_info2, key = lambda x: x[1]['pvalue'], reverse=False)
sorted_frequencies_r = sorted(word_comparison_info2, key = lambda x: x[1]['rate_ratio'], reverse=True)

print([x[0] for x in sorted_frequencies_r if x[1]['bigger'] is 1 ])


#parameters.wordcountToWordcloud(count,'deleteMe.png')
