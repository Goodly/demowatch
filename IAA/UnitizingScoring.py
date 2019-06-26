import krippendorff
import numpy as np
from ThresholdMatrix import evalThresholdMatrix

def scoreNuUnitizing(starts,ends,length,numUsers,users, userWeightDict, answers, winner):
    answerMatrix = toArray(starts,ends,length, users, userWeightDict, answers, winner)
    #TODO: SCALE answerMatrix by rep
    numUsers = len(np.unique(users))
    percentageArray = scorePercentageUnitizing(answerMatrix,length,numUsers)
    assert len(starts) == len(users)
    filteredData = filterSingular(percentageArray, numUsers,users,starts,ends)
    fStarts,fEnds,fNumUsers,goodIndices, fUsers = filteredData[0], filteredData[1], \
                                                  filteredData[2], filteredData[3], filteredData[4]
    if len(fStarts)==0:
        return 'L', 'L', 'L'
    if fUsers[0] == 'U':
        return 'U','U','U'
    filteredMatrix = toArray(fStarts, fEnds,length, fUsers, userWeightDict, answers, winner)
    score = scoreAlpha(filteredMatrix, 'nominal')
    inclusiveScore = scoreAlpha(answerMatrix, 'nominal')
    return score, inclusiveScore, goodIndices


def scoreAlphaUnitizing(starts,ends,length,numUsers,dFunc,users):
    """takes in iterables starts,and ends as well as length of the document
    and the total number of Users who were asked to annotate
    returns krippendorff unitizing score for the article, this method
    used mainly for testing and is not used in final algorithm for this"""
    matrix = toArray(starts,ends,length,numUsers, users)
    return scoreAlpha(matrix, distanceFunc = dFunc)

def scoreAlpha(answerMatrix, distanceFunc):
    """provides the krippendorff scores
    of the data passed in, distanceFunc should be
    'nominal', 'ordinal', 'interval', 'ratio' or a callable
    """

    return krippendorff.alpha(value_counts = answerMatrix, \
        level_of_measurement = distanceFunc)

def scorePercentageUnitizing(answerMatrix,length,numUsers):
    """takes in iterables starts,and ends as well as length of the document
    and the total number of Users who were asked to annotate
    returns array of percentage agreement each character"""
    totalNumUsers = numUsers
    PercentScoresArray = np.zeros(length)
    for i in range(len(answerMatrix)):
        PercentScoresArray[i] = answerMatrix[i][0]/totalNumUsers
    return PercentScoresArray


def unitsToArray(starts, ends, length, numUsers):
    def raiseMatrix(start, end):
        for i in range(start, end):
            unitsMatrix[i][0] = unitsMatrix[i][0]+1
            unitsMatrix[i][1] = unitsMatrix[i][1]-1
    col1= np.zeros(length)
    col2 = np.zeros(length)
    unitsMatrix = np.stack((col1,col2), axis = 0).T
    for i in range(length):
        unitsMatrix[i][1] = numUsers
    for i in range(len(starts)):
        raiseMatrix(starts[i],ends[i])
    return unitsMatrix

def toArray(starts,ends,length, users, userWeightDict = None, answers = None, winner = None):
    uniqueUsers = np.unique(np.array(users))
    userBlocks = np.zeros((len(uniqueUsers), length))
    astarts, aends = np.array(starts), np.array(ends)
    totalWeight = 0
    print('toArr seu', len(starts), len(ends), len(users))
    for u in range(len(uniqueUsers)):
        try:
            weight = userWeightDict[uniqueUsers[u]]
            totalWeight = totalWeight + weight
        except:
            totalWeight = len(uniqueUsers)
            weight = 1

        thisU = uniqueUsers[u]
        print('inloop', len(astarts), len(aends), len(users))
        uIndices = getIndicesFromUser(users, uniqueUsers[u])
        ustarts, uends = astarts[uIndices], aends[uIndices]
        for start in range(len(ustarts)):
            for i in range(int(ustarts[start]), int(uends[start])):
                userBlocks[u][i] = weight
    #Now there are arrays of 1s and 0s, gotta collapse them
    #and make the possibilities column
    col1 = np.zeros(length)
    for userBlock in userBlocks:
        col1 = col1+userBlock
    col2 = np.zeros(length)
    for i in range(len(col2)):
        col2[i] = totalWeight-col1[i]
    unitsMatrix = np.stack((col1, col2), axis=0).T
    return unitsMatrix

def filterSingular(percentageScoresArray, numUsers,users,starts,ends):
    """
    filters the data so that only users who highlighted units that passed the
    thresholdmatrix after their percentage agreement was calculated get scored
    by the krippendorff unitizing measurement
    Used when users select a single answer choice
    output is tuple(starts,ends,numGoodUsers)
    """
    #assert len(starts) == len(users), 'starts, users mismatched'
    passingIndexes = np.zeros(len(percentageScoresArray))
    #adjust so user count isn't inflated by reps
    num_reals = len(np.unique(users))
    #if minPassPercent == 'U':
    #    return 'U','U','U','U','U'
    for i in range(len(percentageScoresArray)):
        if type(percentageScoresArray[i]) == 'numpy.ndarray':
            print("OOOOO")
#TODO: get math done for minpasspercent
#        if percentageScoresArray[i]>minPassPercent:

        if evalThresholdMatrix(percentageScoresArray[i], num_reals, scale = 1.2) == 'H':
            passingIndexes[i] = i
    passingIndexes = np.nonzero(passingIndexes)[0]
    assert len(starts) == len(users)
    majorityUsersUnique = getMajorityUsers(passingIndexes, users, starts, ends)
    goodIndices = getIndicesFromMajorityUsers(users, majorityUsersUnique)
    if  len(goodIndices)<1:
        return ([],[],0,[],[])
    starts, ends, users = np.array(starts), np.array(ends), np.array(users)
    starts = starts[goodIndices]
    ends = ends[goodIndices]
    users = users[goodIndices]
    numGoodUsers = len(users)
    out = [starts, ends, numGoodUsers, passingIndexes, users]
    return out

def getMajorityUsers(passingIndexes, users, starts, ends):
    """returns array of unique users who highlighted
    anything that passed the agreement threshold Matrix
    """
    assert len(starts) == len(users), 'starts, users mismatched'
    majorityUsers = []
    for i in range(len(starts)):
        for j in range(int(starts[i]), int(ends[i])):

            if j in passingIndexes:
                if users[i] not in majorityUsers:
                    majorityUsers.append(users[i])
    majorityUsers = np.array(majorityUsers)
    return majorityUsers


def filterIndexByAnswer(winner, answers):
    majorityIndices = np.nonzero(answers == winner)
    return majorityIndices

def getIndicesFromUserAnswer(users, majorityUser, answers, winner):
    """Takes in array of all users ordered
    the same as the starts and ends lists and an array
    of unique users who had an agreed upon highlight and
    returns array of all the indices that any user with
    an agreed upon highlight had highlighted
    Does same filter based on answers and winner, necesary fix for checklist questions"""

    indices = []
    for i in range(len(users)):
        if users[i] == majorityUser and (answers is None or answers[i] == winner):
            indices.append(i)
    return np.array(indices)
def getIndicesFromUser(users, majorityUser):
    """Takes in array of all users ordered
    the same as the starts and ends lists and an array
    of unique users who had an agreed upon highlight and
    returns array of all the indices that any user with
    an agreed upon highlight had highlighted
    """

    indices = []
    for i in range(len(users)):
        if users[i] == majorityUser:
            indices.append(i)
    return np.array(indices)

def getIndicesFromMajorityUsers(users,majorityUsers):
    """Takes in array of all users ordered
    the same as the starts and ends lists and an array
    of unique users who had an agreed upon highlight and
    returns array of all the indices that any user with
    an agreed upon highlight had highlighted """
    goodUserIndices = []
    for i in range(len(users)):
        if users[i] in majorityUsers:
            goodUserIndices.append(i)
    return np.array(goodUserIndices)

