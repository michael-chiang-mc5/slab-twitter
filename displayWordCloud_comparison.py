#from wordcloud import WordCloud, STOPWORDS
from MCWordCloud import WordCloud
import json
import time
import parameters
import matplotlib.pyplot as plt
import scipy.stats as stats
import copy
import pickle

#
min_count=5

# load
t0=time.time()
pkl_file = open('wordcloud_comparison.pkl', 'rb')
pairwise_chi2_matrix = pickle.load(pkl_file)
pkl_file.close()
t1=time.time()
print('Time to load wordcloud_comparison.pkl: ' + str(t1-t0) + ' seconds')
cityNames = pairwise_chi2_matrix.keys()
bonferonni_correction = (len(cityNames)*len(cityNames) - len(cityNames))/2
print(bonferonni_correction)
eps = 0.01

# filter for words by p-value
p_threshold = 0.05*bonferonni_correction
pairwise_chi2_matrix_filtered = copy.deepcopy(pairwise_chi2_matrix)
for cityName1 in cityNames:
    for cityName2 in cityNames:
        try:
            word_comparison_info1 = pairwise_chi2_matrix[cityName1][cityName2]
            # filter by p-value
            word_comparison_info2 = [x for x in word_comparison_info1.items() if x[1]['pvalue'] < p_threshold \
                                                                              and (x[1]['contingency_matrix'][0][0] >= min_count \
                                                                                  or x[1]['contingency_matrix'][1][0] >=min_count \
                                                                                   )
            ]
            # calculate rate_ratio, bigger
            for x in word_comparison_info2:
                rate_ratio = max ((x[1]['rate1']+eps)/(x[1]['rate2']+eps) , (x[1]['rate2']+eps)/(x[1]['rate1']+eps))
                if x[1]['rate1'] > x[1]['rate2']:
                    bigger = 1
                else:
                    bigger = 2
                x[1]['rate_ratio'] = rate_ratio
                x[1]['bigger'] = bigger
            # store
            pairwise_chi2_matrix_filtered[cityName1][cityName2] = dict(word_comparison_info2)
        except:
            pass



frequencies = pairwise_chi2_matrix_filtered['compton']['mapTemplate']
sorted_frequencies_p = sorted(frequencies.items(), key = lambda x: x[1]['pvalue'], reverse=False)
sorted_frequencies_r = sorted(frequencies.items(), key = lambda x: x[1]['rate_ratio'], reverse=True)

print([x[0] for x in sorted_frequencies_p if x[1]['bigger'] is 1 ])


wC = WordCloud(
                      font_path='/Users/mcah5a/Library/Fonts/CabinSketch-Bold.ttf',
                      background_color='black',
                      width=1800,
                      height=1400,
                      relative_scaling=1,
                     )

for cityName1 in cityNames:
    for cityname2 in cityNames:
        if cityName1 == cityname2:
            continue
        wC.MCgenerate_from_frequencies(pairwise_chi2_matrix_filtered[cityName1][cityname2].items())
        plt.imshow(wC)
        plt.axis('off')
        plt.savefig('./img_wordcloud/' + cityName1 + '-' + cityname2 + '.png', dpi=300)
        #plt.show()
