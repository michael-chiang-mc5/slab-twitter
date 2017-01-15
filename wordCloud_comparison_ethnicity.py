import parameters
import json
from MCWordCloud import WordCloud, STOPWORDS
import pickle
import time

# load
pkl_file = open('lastNameEthnicity.pkl', 'rb')
surnames = pickle.load(pkl_file)
pkl_file.close()

# load
t0=time.time()
boundingBox = parameters.boundingBox['mapTemplate']
tweets = parameters.importTweets(boundingBox)
t1=time.time()
print('Time to load tweets: ' + str(t1-t0) + ' seconds')

#
surnames_byRace = dict()
surnames_byRace['white']    = [x[0] for x in surnames.items() if x[1]=='white']
surnames_byRace['black']    = [x[0] for x in surnames.items() if x[1]=='black']
surnames_byRace['asian']    = [x[0] for x in surnames.items() if x[1]=='asian']
surnames_byRace['native']   = [x[0] for x in surnames.items() if x[1]=='native']
surnames_byRace['hispanic'] = [x[0] for x in surnames.items() if x[1]=='hispanic']

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

tweets_byRace = dict()
for race in ['white','black','asian','native','hispanic']:
    t0=time.time()
    tweets_byRace[race] = [ tweet for tweet in tweets if checkLastName(tweet['user']['name'],surnames_byRace[race]) ]
    t1=time.time()
    print('Time to get ' + race + ' tweets: ' + str(t1-t0) + ' seconds')

# save
output = open('tweets_byRace.pkl', 'wb')
pickle.dump(tweets_byRace, output)
output.close()


#[tweet['user']['name'] for tweet in tweets_byRace['asian'] ]

#names = [tweet['user']['name'] for tweet in tweets_filtered]
#last_names = " ".join([name.split()[-1].lower() for name in names])


# initialize wordCloud object
#wC = WordCloud(
#                      font_path='/Users/mcah5a/Library/Fonts/CabinSketch-Bold.ttf',
#                      stopwords=STOPWORDS,
#                      background_color='black',
#                      width=1800,
#                      height=1400
#                     )
#lastname_frequencies = dict(wC.MCprocess_text(last_names)) # process_text will remove stopwords


#sorted(lastname_frequencies.items(), key=lambda x: x[1])
