import parameters
tweets = parameters.importTweets(parameters.boundingBox['pasadena'])
parameters.plotMap(tweets,'./figures/pasadena.png')
