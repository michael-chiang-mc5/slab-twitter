# https://marcobonzanini.com/2015/03/09/mining-twitter-data-with-python-part-2/

import json

with open('data/stream_apple.json', 'r') as f:
    line = f.readline() # read only the first tweet/line
    tweet = json.loads(line) # load it as Python dict
    print(json.dumps(tweet, indent=4)) # pretty-print
