import pandas as pd
import numpy as np
import os

def splitcsv(directory):
    #print('splitting')
    pointsFile = findMaster(directory)
    #print(pointsFile)
    pointsdf = pd.read_csv(directory+'/'+pointsFile)
    #print(pointsdf)
    articles = np.unique(pointsdf['Article ID'])
    for art in articles:
        artdf = pointsdf[pointsdf['Article ID'] == art]
        print(len(artdf))
        artdf = artdf.drop_duplicates(subset = ['Points', 'Credibility Indicator Name', 'Start', 'End'])
        print(len(artdf))
        print('exporting Finale')
        artdf.to_csv(directory+'/VisualizationData_'+str(art)+'.csv', index = False, encoding='utf-8')

def findMaster(directory):
    for root, dir, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv') and 'SortedPts_' in file:
                return file

#splitcsv('pred1')