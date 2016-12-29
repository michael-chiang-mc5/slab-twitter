import matplotlib.pyplot as plt
import matplotlib.cm
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize
import parameters
import pickle

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
output = open('map_template.pkl', 'wb')
pickle.dump(fig, output)
output.close()
