import matplotlib.pyplot as plt
import matplotlib.cm
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize
import parameters
import pickle
import csv
import time

# Initialize basemap
themap = Basemap(projection='merc',
              llcrnrlon = parameters.westlimit,              # lower-left corner longitude, westlimit
              llcrnrlat = parameters.southlimit,               # lower-left corner latitude, southlimit
              urcrnrlon = parameters.eastlimit,               # upper-right corner longitude, eastlimit
              urcrnrlat = parameters.northlimit,               # upper-right corner latitude, northlimit
              resolution = 'h',         # Can be c (crude), l (low), i (intermediate), h (high), f (full) or None
              #area_thresh = 100000.0,
              )

# Read in shapefile containing highways
themap.readshapefile('/Users/mcah5a/Desktop/projects/slab-twitter/tl_2010_06_prisecroads/tl_2010_06_prisecroads', 'Streets',drawbounds = False)

# Filter highways
# Filter by: MTFCC (S1100 for primary, S1200 for secondary) Ex: # road[1]['MTFCC'] == 'S1100'
# Filter by: RTTYP (C county, I	Interstate, S state recognized)
# Filter by: FULLNAME (road name)
road_zipped = zip(themap.Streets,themap.Streets_info)
road_zipped = [road for road in road_zipped if '57' in str(road[1]['FULLNAME']) or \
                                               ' 60' in str(road[1]['FULLNAME']) or \
                                               '60 ' in str(road[1]['FULLNAME']) or \
                                               road[1]['MTFCC'] == 'S1100' \
              ]
# plot figure
fig = plt.subplot(111)
for shape in road_zipped:
    xx,yy, = zip(*shape[0])
    themap.plot(xx, yy, linewidth = 2, color='0.7')
themap.drawcoastlines()
themap.fillcontinents(color = '0.9')
themap.drawmapboundary(fill_color='steelblue')

# Save for future use
output = open('pickle_files/map_template.pkl', 'wb')
pickle.dump(fig, output)
output.close()








###### Ethnicity by last name
def toFloat(str):
    if str == '(S)':
        return 0
    else:
        return float(str)

# parameters
percent_threshold = 0.9

ifile  = open('census_data/Names_2010Census.csv', "r")
reader = csv.reader(ifile)


rownum = 0
surnames = dict()
for row in reader:
    # Save header row.
    if rownum == 0:
        header = row
    else:
        surname =       row[0].lower()
        pctwhite =      toFloat(row[5])
        pctblack =      toFloat(row[6])
        pctapi   =      toFloat(row[7])
        pctaian  =      toFloat(row[8])
        pct2prace =     toFloat(row[9])
        pcthispanic =   toFloat(row[10])
        if pctwhite > percent_threshold*100:
            surnames[surname] = 'white'
        if pctblack > percent_threshold*100:
            surnames[surname] = 'black'
        if pctapi > percent_threshold*100:
            surnames[surname] = 'asian'
        if pctaian > percent_threshold*100:
            surnames[surname] = 'native'
        if pct2prace > percent_threshold*100:
            surnames[surname] = 'biracial'
        if pcthispanic > percent_threshold*100:
            surnames[surname] = 'hispanic'
    rownum += 1
ifile.close()

t0=time.time()
surnames_byRace = dict()
surnames_byRace['white']    = [x[0] for x in surnames.items() if x[1]=='white']
surnames_byRace['black']    = [x[0] for x in surnames.items() if x[1]=='black']
surnames_byRace['asian']    = [x[0] for x in surnames.items() if x[1]=='asian']
surnames_byRace['native']   = [x[0] for x in surnames.items() if x[1]=='native']
surnames_byRace['hispanic'] = [x[0] for x in surnames.items() if x[1]=='hispanic']
t1=time.time()
print('Time to create surname dictionary: ' + str(t1-t0) + ' seconds')

output = open('pickle_files/ethnicity_by_lastName.pkl', 'wb')
pickle.dump(surnames_byRace, output)
output.close()





# get tweets by ethnicity
tweets = parameters.importTweets()
tweets_byRace = dict()
for race in ['white','black','asian','native','hispanic']:
    tweets_byRace[race] = parameters.filterTweetsByRace(tweets,race)
output = open('pickle_files/tweets_byEthnicity.pkl', 'wb')
pickle.dump(tweets_byRace, output)
output.close()
