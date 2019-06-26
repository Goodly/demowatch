from UnitizingScoring import *
import numpy as np
import pandas as pd
import os
import ast
from dataV2 import printType
from dataV2 import get_indices_hard
from dataV2 import indicesFromString
import csv
import json
from dataV2 import readIndices
sourceDatabase = {}
JournalistDatabase = {}
ArticleDatabase = {}

#-1 is a default value,
argValToWeightDict= {1:3, 2:2, 3:1, 4:.5, 5:1, 6:1, -1:1}
sourceValToWeightDict= {1:2, 2:1, 3:.5, 4:.25, 5:.5, 6:.5, 7:.5, -1:1}



def pointSort(directory, allTUAS_filename):
    print("SORTING STARTING")
    sourceFile, argRelevanceFile, weightFile = getFiles(directory)

    outData = [['Article ID', 'Credibility Indicator ID ', 'Credibilty Indicator Category',
                'Credibility Indicator Name',
                'Points', 'Indices of Label in Article', 'Start', 'End', 'target_text']]

    artNum = 0000
    print('files', weightFile)
    for weightSet in weightFile:
        print(sourceFile, argRelevanceFile, weightSet)
        dataDict = storeData(sourceFile, argRelevanceFile, weightSet, allTUAS_filename)
        print(dataDict)
        articles = dataDict.keys()
        #mergeWeightFiles(weightFile)
        print('arty farty', articles)
        for art in articles:


                counter= 0
                artNum = retrieveArtNum(dataDict, art)
                argDic = retrieveArgDict(dataDict, art)
                sorcDic = retrieveSourceDict(dataDict, art)
                weightQ, weightA = getweightQA(dataDict, art)
                pointRecs = getpointRec(dataDict, art)
                print('poir', pointRecs)
                weightInds = getweightIndices(dataDict, art)
                weightTexts = getweightText(dataDict, art)
                print('wtwtwtwtxt', weightTexts)
                labels = getLabels(dataDict,art)
                schema =getSchema(dataDict, art)
                for i in range(len(pointRecs)):
                    wu = weightInds[i]
                    wt = weightTexts[i]
                    if isinstance(wu, str):
                        wu = get_indices_hard(wu)
                    bestSourceTask = findBestMatch(wu, sorcDic)
                    bestArgTask = findBestMatch(wu, argDic)
                    ptsRec = pointRecs[i]
                    # it's zero when there's no answers that passed the specialist IAA
                    # -1 is default answer value, it'll pass the ptsrec to the final score
                    if bestSourceTask!=0:
                        sourceData = sorcDic[bestSourceTask]
                        sourceUnits, sourceAns = sourceData[1], sourceData[0]
                    else:
                        sourceUnits = 0
                        sourceAns = -1
                    if bestArgTask!=0:
                        argData = argDic[bestArgTask]
                        argUnits, argAns = argData[1], argData[0]
                    else:
                        argUnits = []
                        argAns = -1
                    journalist = 'Joe The Journalist'
                    pts = assignPoints(ptsRec,wu, sourceUnits, argUnits, argAns, sourceAns, art, journalist)
                    if pd.isna(pts):
                        pts = 0

                    #credId = counter
                    credId = schema[0]+str(counter)
                    counter+=1
                    starts, ends = indicesToStartEnd(wu)
                    addendum = [artNum, credId, schema, labels[i], pts, wu, starts[0], ends[0], wt]
                    outData.append(addendum)
                    print('anum', artNum)
                    #TODO: figure out how visualization handles stuff with multiple starts and ends
                    for k in range(1, len(starts)-1):
                        addendum = [artNum, credId, schema, labels[i], 0, wu, starts[k], ends[k], wt]
                        outData.append(addendum)
                print('exporting to csv')
                scores = open(directory + '/SortedPts_'+str(artNum)+'.csv', 'w', encoding='utf-8')
                with scores:
                   writer = csv.writer(scores)
                   writer.writerows(outData)

    print("Table complete")
    print('Sources')
    print(sourceDatabase)
    print('Journalists')
    print(JournalistDatabase)
    print('Article Scores')
    print(ArticleDatabase)
def mergeWeightFiles(weightSet):
    df = pd.read_csv(weightSet[0])
    for i in range(1, len(weightSet)):
        weights = pd.read_csv(weightSet[i])
        df.append(weights, ignore_index = True)
    df.to_csv('combined_weights.csv')

def storeData(sourceFile, argRelFile, weightFile, allTuas):
    print('weightFile', weightFile)
    sourceData = pd.read_csv(sourceFile)
    argData = pd.read_csv(argRelFile)
    weightData = pd.read_csv(weightFile)
    tuas = pd.read_csv(allTuas)
    #by articles not by tasks
    #Use article not tasks, finding which task best fits the weighting recommenation
    argArticles = np.unique(argData['article_sha256'])
    print('weightdat \n',weightData['article_sha256'])
    nuqWeightArts = weightData[weightData['article_sha256'].notnull()]['article_sha256']
    print('nuqweight', nuqWeightArts)
    weightArticles = np.unique(nuqWeightArts)
    print('weightArt', weightArticles)
    uqArticles = np.append(argArticles, weightArticles)
    print('uqart', uqArticles)
    bigDict = {}
    for art in uqArticles:
        print('thisArt', art)
        artArgData = argData[argData['article_sha256'].notnull()]
        artArgData = artArgData[artArgData['article_sha256'] == art]
        try:
            artNum = artArgData['article_num'].iloc[0]
            taskAnsArg = getAnswersTask(artArgData)
        except IndexError:
            print("INDEX ERROR", artArgData)
            artNum = art
            taskAnsArg = {-1:-1}
        artSourceData = sourceData[sourceData['article_sha256'].notnull()]
        artSourceData = artSourceData[artSourceData['article_sha256'] == art]
        #there's many questions, only q 4 is relevant
        artQSourceData = artSourceData[artSourceData['question_Number'] == 4]
        taskAnsSource = getAnswersTask(artQSourceData)
        artWeights = weightData[weightData['article_sha256'].notnull()]
        artWeights = artWeights
        print('checksametypeerror', art,artWeights['article_sha256'])
        print(weightFile)
        #TODO: same bug with nan line. hate pt. assignment
        try:
            artWeights = artWeights[artWeights['article_sha256'] == art]
            weightTasks = artWeights['task_uuid'].tolist()
            labels = artWeights['Label'].tolist()
            weightInds = artWeights['highlighted_indices'].apply(get_indices_hard).tolist()
            weightTexts = artWeights['target_text']
            weightRec = artWeights['Points'].tolist()
            weightQs = artWeights['Question_Number'].tolist()
            weightAnswers = artWeights['Answer_Number'].tolist()
        except TypeError:
            print('')
            artWeights = []
            weightTasks = []
            labels = []
            weightInds = []
            weightRec = []
            weightQs = []
            weightTexts = []
            weightAnswers = []
        weightDict = {}
        for t in range(len(weightTasks)):
            weightDict[weightTasks[t]] = {
                'indices':weightInds[t],
                'pointRec': weightRec[t],
                'label':labels[t],

            }
        try:
            s = artWeights['schema']
            schema = s.iloc[0]
        except:
            schema = 'SCHEMANOTFOUND'
        argtasks = artArgData['task_uuid']
        taskTuaArg = {}
        print('wtwtwtwtwtwtwt', weightTexts)
        print('wiii', weightInds)
        for t in argtasks:
            tua = getTUA(t, tuas)
            taskTuaArg[t] = tua
        sorctasks = artQSourceData['task_uuid']
        taskTuaSourc = {}

        for t in sorctasks:
            tua = getTUA(t, tuas)
            taskTuaSourc[t] = tua
        argDict = mergeByTask(taskAnsArg, taskTuaArg)
        sorcDict = mergeByTask(taskAnsSource, taskTuaSourc)
        bigDict[art] = {
            'argDict':argDict,
            'sourceDict': sorcDict,
            'weightDict':weightDict,
            'labels':labels,
            'weightIndices': weightInds,
            'pointRec': weightRec,
            'weightQuestions':weightQs,
            'weightAnswers': weightAnswers,
            'weightText': weightTexts,
            'schema': schema,
            'artNum': artNum
        }
    return bigDict
def runjson(targ):
    return json.loads(targ)
def retrieveArtNum(data, article):
    return data[article]['artNum']
def retrieveweightDict(data, article):
    return data[article]['weightDict']
def retrieveArgDict(data, article):
    return data[article]['argDict']

def retrieveSourceDict(data, article):
    return data[article]['sourceDict']

def retrievesorctaskTua(data, article):
    return data[article]['sorctua']

def retrieveargtaskTua(data, article):
    return data[article]['argtua']

def getTUA(task, tuaDF):
    taskDF = tuaDF[tuaDF['quiz_task_uuid'] == task]
    tuas = []
    starts = []
    ends = []
    for t in taskDF['offsets']:
        formatted = json.loads(t)
        #print('formed', formatted)
        for f in formatted:
            starts.append(f[0])
            ends.append(f[1])
    indices = []
    for i in range(len(starts)):
        for n in range(starts[i], ends[i]):
            indices.append(n)
        #tuas.append((getStartsEndsFromString(t)))
    #print("TUAS", indices)
    #print('-------------------')
    return indices

def getStartsEndsFromString(bigStr):

    onStart = True
    starts = []
    ends = []
    ind = 0
    num = 0
    #TODO:if there's a number within the string this will freak out
    while ind<len(bigStr):
        if bigStr[ind].isdigit():
            if num>0:
                num = 10*num+int(bigStr[ind])
            else:
                num = int(bigStr[ind])
        else:
            if num!=0:
                if onStart:
                    starts.append(num)
                else:
                    ends.append(num)
                onStart = not onStart
                num = 0
        ind += 1
    indices = []
    for i in range(len(ends)):
        for n in range(starts[i], ends[i]):
            indices.append(n)
    return np.unique(indices).tolist()

def indicesToStartEnd(indices):
    starts = []
    ends = []
    last = -1
    arr = np.array(indices)
    if len(indices)<1:
        return [-1],[-1]
    for i in range(len(indices)):
        if indices[i]-last>1 and indices[i] not in starts:
            starts.append(indices[i])
            ends.append(indices[i-1])
        last = indices[i]
    #ends.append(indices[len(indices)-1])
    return sorted(starts), sorted(ends)


def getSchema(data, article):
    return data[article]['schema']
def getTaskid(data, article):
    return data[article]['task']
def getweightQA(data, article):
    return data[article]['weightQuestions'], data[article]['weightAnswers']
def getpointRec(data, article):
    return data[article]['pointRec']
def getweightIndices(data,article):
    indices = data[article]['weightIndices']
    return indices
def getweightText(data,article):
    indices = data[article]['weightText']
    return indices


def getLabels(data, article):
    return data[article]['labels']
def getArgAnswers(data, article):
    return data[article]['argAnswers']


def getArgIndices(data, article):
    return data[article]['argIndices']


def getSourceAnswers(data, article):
    return data[article]['sourceAnswers']


def getSourceIndices(data, article):
    return data[article]['sourceIndices']


def strLstToIntLst(string):
    out = []
    num = None
    for i in range(len(string)):
        if string[i].isdigit():
            if num:
                num = num*10
                num = num+int(string[i])
            else:
                num = int(string[i])
        else:
            if num:
                out.append(num)
                num = None
    return out


def getAnswersTask(artData):
    #indices = np.array(artData['highlighted_indices'].tolist())
    answers = np.array(artData['agreed_Answer'].tolist())
    tasks = np.array(artData['task_uuid'].tolist())
    passingVals = findNumVals(answers)
    #indices = indices[passingVals]
    answers = answers[passingVals]
    tasks = tasks[passingVals]
    #indices = [strLstToIntLst(ind) for ind in indices]
    d = {}
    for t in range(len(tasks)):
        d[tasks[t]] = answers[t]
    return d
#def getTextTask()
def mergeByTask(answerDict, tuaDict):
    for k in answerDict.keys():
        if k in tuaDict.keys():
            temp = answerDict[k]
            answerDict[k] = (temp, tuaDict[k])
        else:
            temp = answerDict[k]
            answerDict[k] = (temp, [])
    return answerDict
def getFiles(directory):
    #NEEDS: WeightingOutputs, sourceTriagerIAA, arg Source IAA
    sourceFile = None
    argRelevanceFile = None
    weightOutputs = []
    for root, dir, files in os.walk(directory):
        for file in files:
            #print(file)
            if 'Dep_S_IAA' in file:
                print('depsiaa file-------------', file)
                if file.endswith('.csv')  and 'ource' in file:
                    print("found Sources File" + directory + '/' + file)
                    sourceFile = directory+file
                    print('Found Sources File ' + sourceFile)
                if file.endswith('.csv')   and 'Arg' in file:

                    argRelevanceFile = directory+file
                    print('Found Arguments File ' + argRelevanceFile)
            if file.endswith('.csv')  and 'Point' in file:
                print('Found Weights File '+ directory + file)
                weightOutputs.append(directory+file)
                print('foud Weights File...', weightOutputs)

    print('all', sourceFile, argRelevanceFile, weightOutputs)
    return sourceFile, argRelevanceFile, weightOutputs


def findNumVals(lst):
    indices = []
    for i in range(len(lst)):

        try:
            if lst[i].isdigit():
                indices.append(i)
        except AttributeError:
            print("attributeerror", i, lst[i])
            indices.append(i)
    return indices


def findBestMatch(ptsUnits, modDict):
    """
    :param ptsUnits: one list of passing units
    :param modUnits: list of lists of units of the modifier
    :return: index of the best modifier Unit
    """
    bestTask =0
    bestScore = -1
    for i in modDict.keys():
        modUnits = modDict[i][1]
        score, units = calcOverlap(modUnits, ptsUnits)
        if score>bestScore:
            bestScore = score
            bestTask = i
    return bestTask


def assignPoints(ptsRec, ptsRecUnitization, sourceUnitization, argUnitization, argVal, sourceVal, article, journalist):
    """

    :param ptsRec:
    :param ptsRecUnitization: list of every index that was from the pointrec
    :param sourceUnitization: list of eveyr index that's a source
    :param argUnitization: list of eveyr index that's an arg
    :param argVal: the answer to the question about this
    :param sourceVal:
    :param article:
    :param journalist:
    :return:
    """
    doesPass, passingIndices = checkAgreement(ptsRecUnitization, sourceUnitization)
    if doesPass:
        print("IT'S A SOURCE")
        source = getSource(sourceUnitization)
        sendPoints(source, ptsRec, sourceDatabase)
        if checkSpecialCase(argVal, sourceVal, ptsRec, article, journalist) != 'NotSpecial':
            print("It's Special")
            return
        sourceMult = calcImportanceMultiplier(sourceVal, sourceValToWeightDict)
        sourceAdjustedValue = sourceMult*ptsRec
        argMult = calcArgImportanceMultiplier(argUnitization, ptsRecUnitization, argVal)
        final_points = sendArticleJournalistPoints(sourceAdjustedValue, argMult, article, journalist)
    else:
        argMult = calcArgImportanceMultiplier(argUnitization, ptsRecUnitization, argVal)
        final_points = sendArticleJournalistPoints(ptsRec, argMult, article, journalist)
    return final_points


def sendArticleJournalistPoints(ptsrec, multiplier, article, journalist):
    points = ptsrec*multiplier
    sendPoints(article, points, ArticleDatabase)
    sendPoints(journalist, points, JournalistDatabase)
    print("Sending ", points, "to ", article)
    return points

def checkSpecialCase(argVal, sourceVal, ptsRec, article, journalist):
    if argVal == 5 and (sourceVal == 5 or sourceVal == 6 or sourceVal == 7):
        multiplier = -1
        sendArticleJournalistPoints(ptsRec, multiplier, article, journalist)
        return
    elif argVal == 2:
        sendArticleJournalistPoints(7, 1, article, journalist)
        return
    else:
        return 'NotSpecial'


def calcImportanceMultiplier(value, dict):
    return dict[int(value)]


def calcArgImportanceMultiplier(argUnitization, ptsRecUnitization, argVal):
    doesPass, passingIndices = checkAgreement(ptsRecUnitization, argUnitization)
    if doesPass:
        print("ARGONJARGON")
        return calcImportanceMultiplier(argVal, argValToWeightDict)
    else:
        return 1


def checkAgreement(arr1, arr2, threshold = 2):
    """arr1 and arr2 are lists of every unitization
    Raw score might be best indicator, highest percentage of aunits in agreement with either of the unitizaitons"""
    rawScore, passingIndices = calcOverlap(arr1, arr2)
    doesPass = rawScore > threshold
    return doesPass, passingIndices


def calcOverlap(arr1, arr2):
    if isinstance(arr1, int) or isinstance(arr2, int) or len(arr1)<1 or len(arr2)<1:
        return 0,[]

    arr1 = get_indices_hard(str(arr1))
    arr2 = get_indices_hard((str(arr2)))
    arr1 = checkOneString(arr1)
    arr2 = checkOneString(arr2)
    length = max(max(arr1), (max(arr2))) + 1

    answerMatrix = indicesToMatrix(arr1, arr2, length)
    percentageArray = np.array(scorePercentageUnitizing(answerMatrix, length, 2))
    passingIndices = np.nonzero(percentageArray == 1)[0]
    numPasses = len(passingIndices)
    rawScore = max((numPasses / len(arr1), numPasses / len(arr2)))
    return rawScore, passingIndices
def checkOneString(arr):
    if len(arr) == 1:
        if isinstance(arr[0], str):
            return get_indices_hard(arr)
    return arr


def indicesToMatrix(arr1, arr2, length):
    """converts lists of the indices of unitizations to an answer matrix"""
    arr2 = [int(a) for a in arr2]
    arr1 = [int(a) for a in arr1]
    col1 = np.zeros(length)
    col2 = np.zeros(length)
    col1[arr1] = 1
    col2[arr2] = 1
    together = col1+col2
    unTogether = 2-together
    matrix = np.stack((together, unTogether),axis = 0).T
    return matrix


log = []
def sendPoints(target, points, targetDatabase):
    log.append(points)
    if target in targetDatabase.keys():
        targetDatabase[target] = targetDatabase[target]+points
    else:
        targetDatabase[target] = points


def getSource(sourceUnitizaiton):
    return 0

# print(checkAgreement([1,2,3,4], [1,2,3,4]))
#
# u1 = [3,4,5,6,7,8,9,10]
# u2 = [6,7,8,9,10,11,12,13]
# u3 = [1,2,3,4,5,6]
# u4 = [17,18,19,20,21]
#
# assignPoints(10,u1,u1,u1,3, 3, 1, 'bill')
# # print('source', sourceDatabase)
# # print('journalists', JournalistDatabase)
# # print('articles', ArticleDatabase)
# # assignPoints(10,u1,u1,u4,3,3,2, 'bill')
# # print('source', sourceDatabase)
# # print('journalists', JournalistDatabase)
# # print('articles', ArticleDatabase)
# # assignPoints(10,u1,u4,u4,3,3,2, 'bill')
# # print('source', sourceDatabase)
# # print('journalists', JournalistDatabase)
# # print('articles', ArticleDatabase)
# # assignPoints(10,u4,u4,u4,5,5,2, 'bill')
# # print('source', sourceDatabase)
# # print('journalists', JournalistDatabase)
# # print('articles', ArticleDatabase)
# #source,args,weight = getFiles('./demo1')
# #data = (storeData(source,args,weight))
# #print(data)
#pointSort('./pred1')
# print(sourceDatabase)
# print(ArticleDatabase)
# print(JournalistDatabase)
# print(log)
