#This file houses utility functions for finding outputs that aren't essential to PE calculations, but make
#outputs more readable, and hopefully easier for the public to understand what goes on under the hood

import numpy as np

def addToSourceText(starts, ends, texts, sourceText):
    #print(texts)
    for i in range(len(starts)):
        pointer = 0
        myText = texts[i]
        #BUG had a bug going to the end, one time output from tagworks where the target text isn't as long as start->
        #end; 2381df5d-1599-4fef-ac63-63cb29c18b72	http://pe.goodlylabs.org/project/SSSPECaus2/task/790	SSSPETest3
        # 1722	1722SSSArticle.txt	ce4e4600-2da1-41ba-9f0c-a942cead5093	b18b8534-c9ce-4bec-9670-9d3b5e7f73da
        # SSScience and Causality Questions V2	1	Science and Causality Questions for SSS Students V2	6
        # What evidence is given for the primary causal claim? *Check all that apply.*
        # Highlight sections of the article that illustrate each selection. (Hill's Criteria)	4
        # A plausible mechanism is proposed	f60f5102-17cb-447a-9b58-1e0d5f5cd0dd	ce4e4600-2da1-41ba-9f0c-a942cead5093
        # A plausible mechanism is proposed	0	1533	1643	just 1 percent of all the Earth’s available oxygen mixes
        # into the ocean the vast majority remains in the air.	6236
        #SSPE caus2--ar1722, q 6, 1533-1643

        for c in range(starts[i], ends[i]):
            #print(starts[i], ends[i])
            sourceText[c] = myText[pointer]
            pointer += 1
    return sourceText

def getTextFromIndices(indices,  sourceText):
    out = ''
    last = indices[0] - 1
    for i in range(len(indices)):
        if indices[i] -1 !=last:
            out = out + '//'
        last = indices[i]
        out = out+str(sourceText[indices[i]])
    return out
def makeList(size):
    out = []
    for i in range(size):
        out.append(0)
    return out

def getText(start,end, sourceText):
    out = ''
    for i in range(start,end):
        out = out+sourceText[i]
    return out

def oddsDueToChance(percentage, num_users = 5, num_choices = 2):
    """Simulates the odds that agreement is due to chance based off of a coinflip"""
    #print('simulating chance')
    return .5
    if percentage<.5:
        return 1
    percentages = np.zeros(0)
    for i in range(10000):
        flips = np.random.choice(num_choices, num_users)
        for choice in range(num_choices):
            counts = []
            counts.append(np.sum(flips == choice))
        highCount = max(counts)
        highScore = highCount/num_users
        percentages = np.append(percentages, highScore)
        #print(flips, counts, highCount,highScore, percentages)
    winRate = np.sum(percentages>=percentage)/10000
    #print('Done')
    return winRate