#Testing the new Unitizing scoring functions on our invented DataSet to

import pandas as pd
import numpy as np
#from jnius import autoclass
import csv
from UnitizingScoring import *
from CodingScoring import *
#
# CAS = autoclass('org.dkpro.statistics.agreement.coding.CodingAnnotationStudy')
# UAS = autoclass('org.dkpro.statistics.agreement.unitizing.UnitizingAnnotationStudy')
# UAU = autoclass('org.dkpro.statistics.agreement.unitizing.UnitizingAnnotationUnit')
# KAUA = autoclass('org.dkpro.statistics.agreement.unitizing.KrippendorffAlphaUnitizingAgreement')
# KAA = autoclass('org.dkpro.statistics.agreement.coding.KrippendorffAlphaAgreement')
# NDF = autoclass('org.dkpro.statistics.agreement.distance.NominalDistanceFunction')
# ODF = autoclass('org.dkpro.statistics.agreement.distance.OrdinalDistanceFunction')
# Integer = autoclass('java.lang.Integer')
# Long = autoclass('java.lang.Long')
# Object = autoclass('java.lang.Object')

path = './pe_test_data.csv'

def calc_scores(filename):
    data = pd.read_csv(filename)
    uberDict = data_storer(data)
    #@TODO initialize csv file here, and any writer we would need
    data = [["Article Number", "Question Number", "Nick Agreement", "Alpha Agreement", "Coding Agreement"]]

    for article in uberDict.keys(): #Find a way to iterate through only articles that there agreement
        for ques in uberDict[article].keys(): #get a way to iterate through questions in the csv
            agreements = score(article, ques, uberDict)
            print(ques)
            #@TODO add to the csv, one column of the 'correct' question answer is agreements[0], degree of agreement is agreements[1]
            if type(agreements) is dict:
                for k in agreements.keys():
                    data.append([article,ques, k, agreements[k]])
            else:
                data.append([article,ques, agreements[0], agreements[1]])
    #@TODO return the csv, or make sure it's pushed out of the womb and into the world
    print('going to csv')
    scores = open('question_scores.csv', 'w')

    with scores:
        writer = csv.writer(scores)
        writer.writerows(data)

    print("Table complete")

def get_responses(article, question, csv_dict):
    return csv_dict[article][question][1:]

def get_user_count(article,question, csv_dict):
    return csv_dict[article][question][0]

def data_storer(data):
    article_nums = np.unique(data['taskrun_article_number'])
    dict_of_article_df = dict()
    for i in article_nums:
        article =data[data['taskrun_article_number'] == i]
        question_nums = np.unique(article['question_number'])
        new_dict = dict()
        for x in question_nums:
            array = []
            array.append(article.loc[article['question_number']== x, 'question_text'][0:1])

            answers = [article.loc[article['question_number']== x, 'answer_number']]
            answers.append([article.loc[article['question_number']== x, 'contributor_id']])
            answers.append([article.loc[article['question_number']== x, 'start_pos']])
            answers.append([article.loc[article['question_number']== x, 'end_pos']])
            answers.append([article.loc[article['question_number']== x, 'source_text_length']])
            array.append(answers)

            new_dict[x] = array
            #this is where krippendorf goes
        dict_of_article_df[i] = new_dict
    return dict_of_article_df

def get_question_answers(data, article_num, question_num):
    return data[article_num][question_num][1][0]

def get_question_userid(data, article_num, question_num):
    return data[article_num][question_num][1][1][0]

def get_question_start(data, article_num, question_num):
    return data[article_num][question_num][1][2][0]

def get_question_end(data, article_num, question_num):
    return data[article_num][question_num][1][3][0]

def get_text_length(data, article_num, question_num):
    return data[article_num][question_num][1][4][0].iloc[0]

def get_num_users(data, article_num, question_num):
    return len(np.unique(get_question_userid(data, article_num, question_num)))

def score(article, ques, data):
    """Call this to get what you want
    It'll check for different types of questionsAnswered
    ifit's an interval question it'll return a random number

    returns a tuple, element 0 is winning answer, element 1 is the disagreement score """
    starts,ends,length,numUsers, users = get_question_start(data,article,ques).tolist(),get_question_end(data,article,ques).tolist(),\
                    get_text_length(data,article,ques), get_num_users(data,article,ques),  get_question_userid(data, article, ques).tolist()
    percentageScore = scoreNickUnitizing(starts,ends,length,numUsers, users)
    alphaScore = scoreAlphaUnitizing(starts,ends,length,numUsers,'nominal')
    return (percentageScore, alphaScore)

def pickWinnerBecauseAlgorithmsTeamWantsMeToUgh(responses):
    """https://stackoverflow.com/questions/6252280/find-the-most-frequent-number-in-a-numpy-vector"""
    a = np.array(responses)
    (values,counts) = np.unique(a,return_counts=True)
    ind=np.argmax(counts)
    return values[ind]

def toStudy(responses):
    intResponses = [Integer(int(i)) for i in responses]
    size = len(intResponses)
    study = CAS(size)
    study.addItemAsArray(intResponses)
    return study


#TODO: Make list of offset length by subtracting start pos from end pos
#TODO: Make list of categories corresponding

test_path = './PE_test_data.csv'
test_path1 = './PE_test_data_120.csv'
test_data_OG = pd.read_csv(test_path)
test_data_120 = pd.read_csv(test_path1)

def test_all(data):
    table_data = [["Article Number", "Question Number", "Agreement Score"]]

    uberDict = data_storer(data)

    for article in uberDict.keys(): #Find a way to iterate through only articles that there agreement
        for ques in uberDict[article].keys(): #get a way to iterate through questions in the csv
            categories = get_question_answers(uberDict, article, ques)
            for cat in categories:
                score = score_Unitizing_Q(uberDict, article,ques, cat)
                print(score)
                #@TODO add to the csv, one column of the 'correct' question answer is agreements[0], degree of agreement is agreements[1]
            table_data.append([article,ques, score])

    scores = open('test_scores_120.csv', 'w')

    with scores:
        writer = csv.writer(scores)
        writer.writerows(table_data)

    print("Table complete")


def score_Unitizing_Q(data_dict, article, question, category):

    titles = [["Article Number", "Question Number", "Agreement Score"]]


    clean_dict = cleanForUnitization(data_dict, article, question)
    total_length = get_text_length(data_dict, article, question)
    num_users = get_num_users(data_dict, article, question)

    alpha = create_UStudy_alpha(num_users, total_length, clean_dict)
    return alpha.calculateCategoryAgreement(Integer(category))

def create_UStudy_alpha(num_users, total_length, anno_dict):
    offsets = anno_dict["Offsets"]
    lengths = anno_dict["Lengths"]
    raters = anno_dict["Raters"]
    categories = anno_dict["Categories"]

    unique_categories = np.unique(categories)

    QUstudy = UAS(int(num_users), int(total_length))


    for i in range(len(offsets)):
        # offset, length, rater, category
        # print(offsets[i])
        # print(lengths[i])
        # print(raters[i])
        # print(categories[i])
        QUstudy.addUnit(float(offsets[i]), float(lengths[i]), int(raters[i]), Integer(categories[i]))
    alpha = KAUA(QUstudy)


    return alpha


def cleanForUnitization(data, article_num, question_num):
    returnDict = dict()
    returnDict['Offsets'] = get_question_start(data, article_num,question_num).tolist()
    returnDict['Lengths'] = np.asarray((get_question_end(data, article_num, question_num)) -  np.asarray(get_question_start(data, article_num,question_num)))
    returnDict['Categories'] = get_question_answers(data, article_num, question_num).tolist()
    returnDict['Raters'] = get_question_userid(data, article_num, question_num).tolist()
    returnDict['Ends'] = np.asarray(get_question_end(data, article_num,question_num))
    return returnDict









# def toUnitizingStudy(begins, ends, ids, arLength):
#     begins = begins[0]
#     ends = ends[0]
#     ids = ids[0]
#     intBegins = [(int(i)) for i in begins]
#     intEnds = [(int(i)) for i in ends]
#     intIDs = [(int(i)) for i in ids]
#     size = len(intBegins)
#     if len(intBegins) != len(intEnds):
#         print("begins and ends not the same")
#         return None
#     units = []
#     numRaters = (len(np.unique(ids)))
#     uStudy = UAS(numRaters, int(arLength[0].iloc[0]))
#     for i in range(size):
#         offset = (intBegins[i])
#         length = (intEnds[i]-intBegins[i])
#         uID = intIDs[i]
#         category = Integer(1)#category might matter, if it does let's stop using 1
#         uStudy.addUnit(offset,length,uID,category)
#     return uStudy
#
# def scoreUnitizing(begins, ends, ids, arLength):
#     study = toUnitizingStudy(begins, ends, ids, arLength)
#     alpha = KAUA(study)
#     return alpha.calculateCategoryAgreement(Integer(1))

def unitizingTest():
    study = toUnitizingStudy([39,18,45,60,140], [60,40,70,65,180], [1,2,3,2,1],230)
    return KAUA(study)

def unitizingSame():
    return KAUA(toUnitizingStudy([39,39,39,39,39], [60,60,60,60,60], [1,2,3,4,5],230))

def unitizingDiff():
    return KAUA(toUnitizingStudy([0,10,20,30,40], [10,20,30,40,50], [1,2,3,4,5],50))

def unitizingRandom():
    length = np.random.randint(20)+5
    size = np.random.randint(1000)+100
    begs,  users = randArray(length, minRange = size),  randArray(length, minRange = 10)
    ends = randAddtoArray(50, begs)
    #print(begs,ends,users,size)
    return (toUnitizingStudy(begs,ends,users,size))

def manyTests(numTests):
    answers = np.zeros(numTests)
    for i in range(numTests):
        stud = unitizingRandom()
        alpha = KAUA(stud)
        ans = alpha.calculateCategoryAgreement(Integer(1))
        #category is 1 because the unitizingstudy decides category of everything is 1
        answers[i] = ans
    return answers

def getScoreBreakdown(lst):
    plt.hist(lst)

def randArray(length, minRange = 100):
    return np.random.randint(minRange, size = length)

def randAddtoArray(maxAddition, oldArray):
    newArray = np.zeros(len(oldArray))
    for i in range(len(oldArray)):
        add = np.random.randint(maxAddition)
        newArray[i] = oldArray[i]+maxAddition
    return newArray




def toAlpha(study, dFunc):
    alph = KAA(study,dFunc())
    return alph

def scoreNominal(responses):
    study = toStudy(responses)
    alpha = toAlpha(study, NDF)
    return alpha.calculateObservedDisagreement()

def scoreOrdinal(responses):
    study = toStudy(responses)
    alpha = toAlpha(study, ODF)
    observed = alpha.calculateObservedDisagreement()
    expected = alpha.calculateExpectedDisagreement()
    agreement = alpha.calculateAgreement()
    cat1 = alpha.calculateCategoryAgreement(Integer(1))


    #val = (observed/(len(responses)**2)*5.75-.6) * 2.5
    # if val<0:
    #     return 0
    # elif val >1:
    #     return 1
    return 1- val


def scoreInterval():
    return 0
#split into different questions, and IAA each one as if it was a yes/no for each option
def scoreMultiple(responses,numUsers):
    out = dict()
    for r in responses:
        scor = nomList(responses, r, numUsers)
        out[r] = scor
    return out

def nomList(responses, r, numUsers):
    l = len(responses)
    i = 0
    for resp in responses:
        if resp == r:
            i+=1
    return i/numUsers
