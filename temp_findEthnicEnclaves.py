## Create image of LA map and tweets in LA
#import parameters
#tweets = parameters.importTweets(parameters.boundingBox['mapTemplate'])
#parameters.plotMap([],'./figures/passadena.png')
#parameters.plotMap(tweets,'./figures/mapTemplate.png')



#
import pickle
import parameters
import scipy.stats as stats

ethnicities = ['white','asian','hispanic']

pkl_file = open('pickle_files/tweets_byEthnicity.pkl', 'rb')
tweets_byEthnicity = pickle.load(pkl_file)
pkl_file.close()

ethnicity_byCity = dict()
for city in [city for city in parameters.boundingBox.keys() if city != 'mapTemplate']:
    population_city = dict()
    population_total = dict()
    for ethnicity in ethnicities:
        population_city[ethnicity] = len(parameters.filterTweetsByBoundingBox(tweets_byEthnicity[ethnicity],parameters.boundingBox[city]))
        population_total[ethnicity] = len(parameters.filterTweetsByBoundingBox(tweets_byEthnicity[ethnicity],parameters.boundingBox['mapTemplate']))
    population_city['all'] = sum([item[1] for item in population_city.items()])
    population_total['all'] = sum([item[1] for item in population_total.items()])
    normalized_city = dict()
    for ethnicity in ethnicities:
        # contigency matrix should look like this:
        #           pizza   not_pizza
        # city1     m11     m12
        # city2     m21     m22
        m11 = population_city[ethnicity]
        m12 = population_total[ethnicity]
        m21 = population_city['all']
        m22 = population_total['all']
        contingency_matrix = [[m11, m12], [m21, m22]]
        oddsratio, pvalue = stats.fisher_exact(contingency_matrix)
        ratio_city_ethnicity = m11/m12
        ratio_city_all = m21/m22
        normalized_ratio = ratio_city_ethnicity/ratio_city_all
        storage = dict()
        storage['pvalue'] = pvalue
        storage['normalized_ratio'] = normalized_ratio
        normalized_city[ethnicity] = storage
    ethnicity_byCity[city] = normalized_city
    #print(city)
    #print(population_city)
    #print(population_total)
    #print(normalized_city)
    #print('******')

# display
for ethnicity in ethnicities:
    print(ethnicity + ": *****************")
    s = sorted([(city,ethnicity_byCity[city][ethnicity]['normalized_ratio'],ethnicity_byCity[city][ethnicity]['pvalue']) for city in ethnicity_byCity if ethnicity_byCity[city][ethnicity]['pvalue'] < 0.05 ], key=lambda x: x[1], reverse=True)
    for ss in s:
        print(ss[0]+"\t"+str(ss[1])+"\t"+str(ss[2]))
