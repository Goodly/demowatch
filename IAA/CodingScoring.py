from UnitizingScoring import *
from ThresholdMatrix import *
from dataV2 import *
from ExtraInfo import getTextFromIndices
from math import ceil
from repScores import *
import numpy as np

def evaluateCoding(answers, users, starts, ends, numUsers, length, sourceText, hlUsers, hlAns, repDF = None, dfunc = None, num_choices = 15):
    """ calculate all scores for any coding question
        inputs:
        answers, users, starts, and ends are all lists that are in the same order,
        meaning that index 0 of each list refers to the user at any index selected one answer, one startpoint, and
        one endpoint being evaluated, it is possible for users to appear in the list multiple times, for instance
        if they highlighted multiple portions of the text or chose more than one answer.
        numUsers refers to the number of unique users that answered the question
        length is the total length of the article being annotated in characters
        dfunc is the distance function that should be used, ordinal or nominal
        output:
        This method returns the most chosen answer, all characters that were highlighted enough to pass the
        threshold matrix test, and reliability scores (between 0 and 1) for the coding and unitizing portions of the
        agreement score.  The variable 'iScore' refers to the unitizing agreement score calculated using Krippendorff's
        alpha including users who never highlighted any characters that passed the threshold matrix
    """
    #This only occurs when the users are prompted for a textual input.

    repScaledAnswers, repScaledUsers = repScaleAnsUsers(answers, users, repDF)

    assert(len(repScaledUsers) == len(repScaledAnswers))
    highScore, winner, weights, firstSecondScoreDiff = scoreCoding(repScaledAnswers, repScaledUsers, dfunc, num_choices = num_choices)
    if dfunc == 'ordinal':
        # This functions as an outlier test, if 4 users categorizes as 'very likely' and one categorizes as
        # 'very not likely', it will fail the threshold matrix test, this method, while not rigorous, provides
        # some defense against outliers that likely were produced by trolls, misunderstandings of the question,
        # and misclicks

        #It seemed like this made every ordinal q way more lenient without the extra clause
        if evalThresholdMatrix(highScore, numUsers)!= 'H' and \
                (num_choices > 3 and winner == 1 or winner == num_choices):
            highScore, winner, weights, firstSecondScoreDiff = scoreCoding(answers, users, 'ordinal', scale = 2)
    # These all return tuples (array of answers, amount of scaling done), element at index 1 is same for all
    assert(len(answers) == len(users))
    # weightScaledAnswers, weightScaledUsers, weightScaledHlUsers, \
    #                                         weightScaledStarts, \
    #                                         weightScaledEnds, \
    #                                         weightScaledNumUsers,\
    #                                         userWeightDict= weightScaleEverything(hlAns, weights, hlUsers, users,
    #                                                                                      starts,ends, repDF)
    assert (len(np.unique(users)) >= len(np.unique(hlUsers)))
    weightScaledAnswers, weightScaledNumUsers, userWeightDict = scaleFromWeights(answers, answers, weights, users, repDF)
    weightScaledHlUsers, weightScaledStarts, weightScaledEnds = scaleHighlights(userWeightDict, hlUsers, hlAns, starts, ends)
    #TOPTWO metric add the score diference
    #weight scale the hlUsers for future usage
    winner, units, uScore, iScore, selectedText= passToUnitizing(weightScaledAnswers,weightScaledHlUsers,weightScaledStarts,
                                                    weightScaledEnds,numUsers,length, highScore, winner,
                                                    weightScaledNumUsers, userWeightDict, sourceText)
    return winner, units, uScore, iScore, highScore, numUsers, selectedText, firstSecondScoreDiff

def repScaleAnsUsers(answers, users, repDF):
    if repDF is None:
        return answers, users
    repScaledAnswers, repScaledUsers = scaleFromRep(answers, users, repDF), scaleFromRep(users, users, repDF)
    return repScaledAnswers, repScaledUsers

def weightScaleEverything(answers,weights, users, hlUsers, starts, ends, repDF):
    arrs = [answers, users, hlUsers, starts, ends]
    assert (len(answers) == len(users))
    scaledArrs, sumTotalScaling, userWeightDict = scaleManyFromWeights(arrs,answers, weights, users, repDF)

    if len(scaledArrs)>0:
        # answers, users, starts, ends
        return scaledArrs[0], scaledArrs[1], scaledArrs[2], scaledArrs[3], scaledArrs[4], sumTotalScaling, userWeightDict
    return [0],[0],[0],[0],sumTotalScaling, userWeightDict

#TOPTWO metric add the top two score difference as  an input
def passToUnitizing(answers, hlusers, starts, ends, numUsers, length, \
                    highScore, winner, scaledNumUsers, userWeightDict, sourceText):
    """ calculates unitizing agreement for any coding question after verifying that it passes the threshold matrix
    Only calculates unitizing agreement amongst users who selected the most agreed-upon answer"""
    #assert len(starts) == len(users), 'starts, users mismatched'
    #TOPTWO metric change next line to have the score difference as an arg
    if evalThresholdMatrix(highScore, numUsers) == 'H':
        #f for filtered
        starts, ends, hlusers = np.array(starts), np.array(ends), np.array(hlusers)
        #fStarts, fEnds, fUsers = starts[goodIndices], ends[goodIndices], users[goodIndices]
        fStarts, fEnds, fhlusers = starts, ends, hlusers
        #fNumUsers = len(np.unique(fUsers))
        fNumUsers = scaledNumUsers
        #If somebody highlights something
        if len(starts)>3:
            assert len(fStarts) == len(fhlusers)
            uScore, iScore, units = scoreNuUnitizing(fStarts, fEnds, length, fNumUsers, fhlusers,
                                                     userWeightDict, answers, winner)
            selectedText = 'N/A'
            if uScore == 'U':
                return 'U','U','U','U','U'
            if uScore != 'M' and uScore != 'L' and uScore != 'U':
                selectedText = getTextFromIndices(units, sourceText)
            return winner, units, uScore, iScore, selectedText
        else:
            uScore = 'NA'
            iScore = 'NA'
            units = []
            selectedText = 'NA'
        return winner, units, uScore, iScore, selectedText
    else:
        status = evalThresholdMatrix(highScore, numUsers)
        return status, status, status, status, status


def scoreCoding(answers, users, dfunc, scale = 1, num_choices = 25):
    """scores coding questions using an ordinal distance
    function(defined in getWinners method)
    inputs:
    answers array like object of the answers for the question
    users is array-like object of users that answered
    dfunc should be 'ordinal' or 'nominal', defaults to nominal
        answers and users should be the same length
    outputs:
    highest score any answer earned,
    the answer chosen most often
    a list containing userIds of users who chose that answer
    """
    answers = [int(a) for a in answers]
    if dfunc == 'ordinal':
        highscore, winner, weights, secondWinner, secondScore = getWinnersOrdinal(answers, num_choices = num_choices, scale = scale)
    else:
        highscore, winner, weights, secondWinner, secondScore = getWinnersNominal(answers, num_choices = num_choices)
    firstSecDiff = highscore - secondScore
    return highscore, winner, weights, firstSecDiff

def getWinnersOrdinal(answers, num_choices = 5, scale = 1):
    # Todo:confirm that I said the right thing about Shannon
    """Calculates the most-common answer and assigns it an agreement score
    uses shannon's thingy-ma-jig to assign weights to different answers"""
    # Shannon Entropy ordinal metric
    # Todo: get number of possible answers as an input so we don't have to assume it's 5
    length = num_choices * scale
    # index 1 refers to answer 1, 0 and the last item are not answer choices, but
    # deal with corner cases that would cause errors
    original_arr = np.array(answers) - 1
    aggregate_arr = np.zeros(length)
    for i in original_arr:
        aggregate_arr[i] += 1
    topScore, winner, weights, secondTop, secondTopScore = shannon_ordinal_metric(original_arr, aggregate_arr)
    # shift array so indexes consistent across ordinal and nominal data
    weights = np.append(0, weights)
    ntp = 0
    return topScore, winner + 1, weights, secondTop, secondTopScore

def shannon_ordinal_metric(original_arr, aggregate_arr):
    """"calculates ordinal metric (Thanks Shannon) """

    original_arr = np.array(original_arr)
    aggregate_arr = np.array(aggregate_arr)
    prob_arr = aggregate_arr / sum(aggregate_arr)
    x_mean = np.mean(original_arr)
    total_dist = len(aggregate_arr)
    score = 1 + np.dot(prob_arr, np.log2(1 - abs(np.arange(total_dist) - x_mean) / total_dist))
    winner = np.where(aggregate_arr == aggregate_arr.max())[0][0]
    #Now exclude the winner
    aggregate_arr[winner] = 0
    second = np.where(aggregate_arr == aggregate_arr.max())[0][0]
    #TODO: work out a way to compare first and second best options for ordinal data
    #might be best to just not do first v second and just have a stricter threshold matrix that's solely based
    #on the shannon metric
    secondScore = 0
    weights= 1+np.log2(1 - abs(np.arange(total_dist) - x_mean) / total_dist)
    return score, winner, weights, second, secondScore

def getWinnersNominal(answers, num_choices = 5):
    """returns the most-chosen answer and the percentage of users that chose that answer"""
    length = num_choices+1
    #index 1 refers to answer 1, 0 and the last item are not answerable
    scores = np.zeros(length)
    for a in answers:
        scores[a] = scores[a]+1
    winner = np.where(scores == scores.max())[0][0]
    topScore = scores[winner] / (len(answers))
    #Now get second best, exclude winnerScore
    scores[winner] = 0
    winnerSecond = np.where(scores == scores.max())[0][0]
    secondScore = scores[winnerSecond] / len(answers)
    weights = np.zeros(num_choices+1)
    weights[winner] = 1
    return topScore, winner, weights, winnerSecond, secondScore

def scaleFromRep(arr, users, repDF):
    """Scales the array based on user reps"""
    scaled = np.zeros(0)
    checked = []
    for i in range(len(arr)):
        if (arr[i], users[i]) not in checked:
            checked.append((arr[i], users[i]))
            addition = np.array(arr[i])
            rep = ceil(get_user_rep(users[i], repDF))
            addition = np.repeat(addition, rep)
            scaled = np.append(scaled, addition)
    return scaled

def scaleFromWeights(arr,answers,weights, users, repDF):
    """Scales the array based on the weights and the user reps"""
    #weights is array of fractions now
    weights = weights
    scaled = np.zeros(0)
    sumTotalScaling = 0
    checked = []
    userWeightDict = {}
    for i in range(len(arr)):
        if (arr[i], users[i], answers[i]) not in checked:
            checked.append((arr[i], users[i], answers[i]))
            addition = np.array(arr[i])
            rep = get_user_rep(users[i], repDF)
            ans = answers[i]
            weight = weights[int(ans)]
            if weight < 0:
                weight = 0
            scaleBy = ceil(weight*rep)
            setUserWeightDict(users[i], answers[i], scaleBy, userWeightDict)
            sumTotalScaling += scaleBy
            addition = np.repeat(addition, scaleBy)
            scaled = np.append(scaled, addition)
    return scaled, sumTotalScaling, userWeightDict


def makeUWeightDict(answers, weights, users, repDF):
    """
    :param arr:
    :param answers:
    :param weights:
    :param users:
    :param repDF:
    :return: scaled number of actual users, ie total of everyone's rep/weight;
        the dictionary mapping userIds to their weight for thi question
    """
    #weights is array of fractions now
    #arr is array of the arrays we're scaling
    if repDF is None:
        print('repDF not found')
        return 1, {}
    weights = weights
    sumTotalScaling = 0
    checked = []
    userWeightDict = {}
    for i in range(len(answers)):
        if (users[i], answers[i]) not in checked:
            checked.append( users[i], answers[i])

            rep = get_user_rep(users[i], repDF)
            ans = answers[i]
            weight = weights[int(ans)]
            if weight < 0:
                weight = 0
            #round up to avoid empty arrays, and prevent users from having 0 weight
            scaleBy = ceil(weight*rep)
            setUserWeightDict(users[i], answers[i], scaleBy, userWeightDict)
            sumTotalScaling += scaleBy

    return sumTotalScaling, userWeightDict

def scaleHighlights(userWeightDict, hlUsers, hlAns, starts, ends):
    """

    :param userWeightDict:
    :param hlUsers:
    :param starts:
    :param ends:
    :return: weight scaled  hlUsers, starts, and ends
    """

    scaledUsers = np.zeros(0)
    scaledStarts = np.zeros(0)
    scaledEnds = np.zeros(0)
    for u in range(len(hlUsers)):
        weight = userWeightDict[(hlUsers[u], hlAns[u])]
        usersAddendum = np.repeat(np.array(hlUsers[u]), weight)
        endsAddendum = np.repeat(np.array(ends[u]), weight)
        startsAddendum = np.repeat(np.array(starts[u]), weight)
        scaledUsers = np.append(scaledUsers, usersAddendum)
        scaledEnds = np.append(scaledEnds, endsAddendum)
        scaledStarts = np.append(scaledStarts, startsAddendum)

    return scaledUsers, scaledStarts, scaledEnds


def scaleManyFromWeights(arr,answers,weights, users, repDF):
    """Scales the array based on the weights and the user reps"""
    #weights is array of fractions now
    #arr is array of the arrays we're scaling
    if repDF is None:
        return arr, 1, {}
    weights = weights
    num_arrs = len(arr)
    scaled = list_of_arrs(num_arrs)
    sumTotalScaling = 0
    checked = []
    userWeightDict = {}
    for i in range(len(arr[1])):
        if (arr[1][i], users[i], answers[i]) not in checked:
            checked.append((arr[1][i], users[i], answers[i]))

            rep = get_user_rep(users[i], repDF)
            ans = answers[i]
            weight = weights[int(ans)]
            if weight < 0:
                weight = 0
            #round up to avoid empty arrays, and prevent users from having 0 weight
            scaleBy = ceil(weight*rep)
            setUserWeightDict(users[i], scaleBy, userWeightDict)
            sumTotalScaling += scaleBy
            for i in range(num_arrs):
                addition = np.array(arr[i])
                addition = np.repeat(addition, scaleBy)
                scaled[i] = np.append(scaled[i], addition)

    return scaled, sumTotalScaling, userWeightDict

def list_of_arrs(length):
    out = []
    for i in range(length):
        out.append(np.zeros(0))
    return out
def setUserWeightDict(user, answer, value, dict):
    if (user, answer) not in dict.keys() or value > dict[(user, answer)]:
        dict[(user, answer)] = value