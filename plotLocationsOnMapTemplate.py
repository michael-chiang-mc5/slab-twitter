import time
t0=time.time()
import json
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
t1=time.time()
print('Time to load libraries: ' + str(t1-t0) + ' seconds')


# load map template
t0=time.time()
pkl_file = open('map_template.pkl', 'rb')
fig = pickle.load(pkl_file)
pkl_file.close()
t1=time.time()
print('Time to load map_template.pkl: ' + str(t1-t0) + ' seconds')

t0=time.time()
import parameters
themap = Basemap(projection='merc',
              llcrnrlon = parameters.westlimit,              # lower-left corner longitude, westlimit
              llcrnrlat = parameters.southlimit,               # lower-left corner latitude, southlimit
              urcrnrlon = parameters.eastlimit,               # upper-right corner longitude, eastlimit
              urcrnrlat = parameters.northlimit,               # upper-right corner latitude, northlimit
              resolution = 'c',         # Can be c (crude), l (low), i (intermediate), h (high), f (full) or None
              #area_thresh = 100000.0,
              )
t1=time.time()
print('Time to create basemap ' + str(t1-t0) + ' seconds')



# Tweets are stored in "fname"
t0=time.time()
lon=[]
lat=[]
with open('twitter_data/la_stream.json', 'r') as f:
    for line in f:
        tweet = json.loads(line)
        lon.append(tweet['geo']['coordinates'][1])
        lat.append(tweet['geo']['coordinates'][0])
        text = tweet['text']
        print(text)
        print("*******************************")
        print("*******************************")

t1=time.time()
print('Time to get lon, lat: ' + str(t1-t0) + ' seconds')


t0=time.time()
x, y = themap(lon, lat)
themap.plot(x, y,
            'o',                    # marker shape
            color='red',         # marker colour
            markersize=7            # marker size
            )
t1=time.time()
print('Time to plot lon, lat: ' + str(t1-t0) + ' seconds')

plt.show()
