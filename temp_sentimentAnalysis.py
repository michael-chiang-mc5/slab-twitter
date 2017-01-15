# see https://github.com/Ejhfast/empath-client

from empath import Empath
import pickle
import parameters
from importlib import reload
pkl_file = open('pickle_files/tweets_byEthnicity.pkl', 'rb')
tweets_byEthnicity = pickle.load(pkl_file)
pkl_file.close()
lexicon = Empath()



#
ethnicities = ['asian','hispanic']
enclaves_byEthnicity = {'asian':    ['westminster','rowlandHeights','ranchoPalosVerde','irvine'] , \
            'hispanic': ['ontario','compton','pomona'] , \
           }

stats_ethnicity_enclave = dict()

for ethnicity in ethnicities:
    ethnicity_inEnclave = dict()
    for enclave_ethnicity in ethnicities:
        enclaves = enclaves_byEthnicity[enclave_ethnicity]
        tweets = []
        for city in enclaves:
            tweets = tweets + parameters.filterTweetsByBoundingBox(tweets_byEthnicity[ethnicity],parameters.boundingBox[city])
        # get corpus
        corpus=parameters.tweetsToCorpus(tweets,depluralize=False)
        # get sentiment scores
        emotion_inEnclave = lexicon.analyze(corpus, categories=["positive_emotion","negative_emotion"], normalize=True)
        # get number of tweets
        numTweets_inEnclave = len(tweets)

        # store
        ethnicity_inEnclave[enclave_ethnicity] = \
                       {'positive': emotion_inEnclave['positive_emotion'],
                        'negative': emotion_inEnclave['negative_emotion'],
                        'aggregate': emotion_inEnclave['positive_emotion'] - emotion_inEnclave['negative_emotion'],
                        'numTweets_inEnclave': numTweets_inEnclave,
                        'tweets':tweets,
                       }
    stats_ethnicity_enclave[ethnicity] = ethnicity_inEnclave


print(stats_ethnicity_enclave['asian']['asian']['aggregate'] / stats_ethnicity_enclave['asian']['hispanic']['aggregate'] )
print(stats_ethnicity_enclave['hispanic']['asian']['aggregate']  / stats_ethnicity_enclave['hispanic']['hispanic']['aggregate'] )

#for tweet in stats_ethnicity_enclave['asian']['hispanic']['tweets']:
#    print(tweet['text'])
