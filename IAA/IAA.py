import csv
from ChecklistCoding import *
from ExtraInfo import *
from dataV2 import *
from repScores import *
import os

path = 'sss_pull_8_22/SSSPECaus2-2018-08-22T2019-DataHuntHighlights.csv'

def calc_agreement_directory(directory, hardCodedTypes = False, repCSV=None, answersFile = None, outDirectory = None):
    print("IAA STARTING")
    if outDirectory is None:
        outDirectory = 's_iaa_'+directory
    highlights = []
    answers = []
    schema = []
    for root, dir, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv') and 'IAA' not in file:
                print("Checking Agreement for "+directory+'/'+file)
                if 'Highlights' in file:
                    print('highlight')
                    highlights.append(directory+'/'+file)
                elif 'Answers' in file:
                    answers.append(directory+'/'+file)
                elif 'Schema' in file:
                    schema.append(directory+'/'+file)
    #sorting filenames alphabetically separates them into the right schemas, it's a gimmick and might not scale
    #if it doesn't work there'll be key errors because taskIDS won't align
    highlights.sort()
    answers.sort()
    schema.sort()
    assert(len(highlights) == len(schema), 'files not found')
    for i in range(len(highlights)):
         calc_scores(highlights[i], hardCodedTypes=hardCodedTypes, repCSV = repCSV,
                            answersFile = answers[i], schemaFile=schema[i], outDirectory=outDirectory)
                    #will be an error for every file that isn't the right file, there's a more graceful solution, but
                    #we'll save that dream for another day
    return outDirectory

def calc_scores(highlightfilename, hardCodedTypes = False, repCSV=None, answersFile = None, schemaFile = None, fileName = None, thirtycsv = None, outDirectory = 's_iaa'):
    print('collecting Data')
    uberDict = data_storer(highlightfilename, answersFile, schemaFile)
    print("donegettingdata")
    data = [["article_num", "article_sha256", "task_uuid","schema_namespace","question_Number", "question_type", "agreed_Answer", "coding_perc_agreement", "one_two_diff",
             "highlighted_indices", "alpha_unitizing_score", "alpha_unitizing_score_inclusive", "agreement_score","odds_by_chance", "binary_odds_by_chance",
             "num_users", "num_answer_choices","target_text", 'question_text', 'answer_content']]
    #initialize rep
    # print('starting rep')
    # try:
    #     repDF = pd.read_csv(repCSV)
    # except:
    #     repDF = create_user_dataframe(uberDict, csvPath = None)
    # thirtyDf = create_last30_dataframe(uberDict, thirtycsv)
    repDF, thirtyDf = None, None
    print('initialized repScores')
    for task in uberDict.keys():  # Iterates throuh each article
        #task_id = get_article_num(uberDict, task)

        task_id = task
        article_num = get_article_num(uberDict,task_id)
        article_sha = get_article_sha(uberDict, task_id)
        schema_namespace = get_schema(uberDict, task_id)
        questions = uberDict[task]['quesData'].keys()
        #has to be sorted for questions depending on each other to be handled correctly
        for ques in sorted(questions):  # Iterates through each question in an article


            agreements = score(task, ques, uberDict, repDF, thirtyDf = thirtyDf,hardCodedTypes = hardCodedTypes)
            # if it's a list then it was a checklist question
            question_text = get_question_text(uberDict, task, ques)
            if type(agreements) is list:
                #Checklist Question
                for i in range(len(agreements)):
                    codingPercentAgreement, unitizingScore = agreements[i][4], agreements[i][2]
                    winner, units = agreements[i][0], agreements[i][1]
                    inclusiveUnitizing = agreements[i][3]
                    selectedText, firstSecondScoreDiff = agreements[i][6], agreements[i][7]
                    question_type, num_choices = agreements[i][8], agreements[i][9]
                    num_users = agreements[i][5]
                    totalScore = calcAgreement(codingPercentAgreement, unitizingScore)
                    answer_text = get_answer_content(uberDict,task, ques, agreements[i][0])
                    # parent_data, units, unitizingScore, inclusiveUnitizing = evalDependency(uberDict, task, parentData,
                    #                                                                         ques, winner, units,
                    #                                                                         unitizingScore, inclusiveUnitizing)
                    bin_chance_odds = oddsDueToChance(codingPercentAgreement,num_users=num_users, num_choices=2)
                    #Treat each q as a binary yes/no
                    chance_odds = bin_chance_odds
                    ques_num = ques
                    units = str(units).replace('\n', '')
                    units = units.replace(' ', ', ')
                    data.append([article_num, article_sha, task_id, schema_namespace, ques_num, agreements[i][8], winner,
                                 codingPercentAgreement, agreements[i][7], units,
                                 unitizingScore, inclusiveUnitizing, totalScore, chance_odds, bin_chance_odds, num_users, agreements[i][9],agreements[i][6],
                                question_text, answer_text])

            else:
                #winner, units, uScore, iScore, highScore, numUsers, selectedText, firstSecondScoreDiff
                winner, units = agreements[0], agreements[1]
                inclusiveUnitizing, numUsers = agreements[3], agreements[5]
                selectedText, firstSecondScoreDiff = agreements[6], agreements[7]
                question_type, num_choices = agreements[8], agreements[9]
                codingPercentAgreement, unitizingScore = agreements[4], agreements[2]

                num_users = agreements[5]
                # parent_data, units, unitizingScore, inclusiveUnitizing = evalDependency(uberDict, task, parentData,
                #                                                                         ques, winner, units,
                #                                                                         unitizingScore,
                #                                                                         inclusiveUnitizing)
                bin_chance_odds = oddsDueToChance(codingPercentAgreement,num_users=num_users, num_choices=2)
                chance_odds = oddsDueToChance(codingPercentAgreement,num_users=num_users, num_choices=num_choices)
                answer_text = get_answer_content(uberDict, task, ques, agreements[0])
                totalScore = calcAgreement(codingPercentAgreement, unitizingScore)
                #ques_num = parse(ques, 'Q')
                ques_num = ques
                units = str(units).replace('\n', '')
                units = units.replace(' ', ', ')
                data.append([article_num, article_sha,task_id,schema_namespace, ques_num, agreements[8], winner, codingPercentAgreement, agreements[7],
                             units, unitizingScore, inclusiveUnitizing,
                             totalScore, chance_odds, bin_chance_odds, num_users, agreements[9], selectedText,
                             question_text, answer_text])


    # push out of womb, into world
    #print('exporting rep_scores')
    # print(repDF)
#    repDF.to_csv('RepScores/Repscore10.csv', mode='a', header=False)
 #   userid_to_CSV(repDF)
    print('exporting to csv')
    # if outDirectory[-1] != '/':
    #     outDirectory = outDirectory +'/'
    #
    # try:
    #     scores = open(outDirectory+'S_IAA_'+name, 'w', encoding = 'utf-8')
    # except FileNotFoundError:
    #     os.mkdir(outDirectory)
    outDirectory = make_directory(outDirectory)
    path, name = get_path(highlightfilename)
    scores = open(outDirectory + 'S_IAA_' + name, 'w', encoding='utf-8')
    with scores:
        writer = csv.writer(scores)
        writer.writerows(data)
    print("Table complete")
    print('iaa outdir', outDirectory)
    return outDirectory
def adjustForJson(units):
    units = str(units)
    out = '['
    prev = False
    for u in range(len(units)):
        if units[u].isdigit():
            out+=units[u]
            prev = True
        elif units[u] == ' ' and prev == True:
            out+=', '
        else:
            prev = False
    out+=']'
    return out



def score(article, ques, data, repDF = None, thirtyDf = None, hardCodedTypes = False):
    """calculates the relevant scores for the article
    returns a tuple (question answer most chosen, units passing the threshold,
        the Unitizing Score of the users who highlighted something that passed threshold, the unitizing score
        among all users who coded the question the same way (referred to as the inclusive unitizing score),
         the percentage agreement of the category with the highest percentage agreement """

    """ Commnted code below previously denoted different types of questions for hard-coding,
    can still be used for hard-coding but eventually will be phased out by a line of code that
    checks the question_type based off the table data"""
    # ordinal_questions = [1,2,4,12,13,14,15,16,17,18,19,20,21,25]
    # nominal_questions = [7,22]
    # unit_questions = [9,10,11, 24] #asks users to highlight, nothing else OR they highlight w/ txt answer
    # multiple_questions = [3,5,8,23]

    starts = get_question_start(data,article, ques)
    ends = get_question_end(data, article, ques)
    length = get_text_length(data, article, ques)
    if len(ends)>0 and max(ends)>0:
        texts = get_answer_texts(data, article, ques)
        sourceText = makeList(length)
        sourceText = addToSourceText(starts, ends, texts, sourceText)
        hlUsers = get_question_hlUsers(data, article,ques)
        hlAns = get_question_hlAns(data, article, ques)
    else:
        sourceText = []
        hlUsers = []
        hlAns = []
    # TODO: find actual number of choices always
    num_choices = 5
    question_type = get_question_type(data, article, ques)

    if hardCodedTypes:
        schema = get_schema(data, article)
        question_type, num_choices = get_type_hard(schema, ques)
        #print("QUESTION TYPE IS", question_type)
    #This block for scoring only a single article, iuseful for debugging
    # print()
    # if article!= '171SSSArticle.txt':
    #     #print(question_type)
    #     if question_type == 'checklist':
    #         return [
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #
    #         ]
    #     return(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    if question_type == 'interval':
        # TODO: verify if these still exist, if they do, bring up to speed with new output formats
        return run_2step_unitization(data, article, ques, repDF)
    answers = get_question_answers(data, article, ques)
    users =get_question_userid(data, article, ques)
    print('art', article,ques)
    numUsers = get_num_users(data, article, ques)
    print('nu', numUsers, users)
    assert (len(answers) == len(users))
    if num_choices == 1:
        return 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    if question_type == 'ordinal':
        #assert(len(answers) == len(users))
        out = evaluateCoding(answers, users, starts, ends, numUsers, length,  sourceText, hlUsers, hlAns, repDF = repDF, dfunc='ordinal', num_choices=num_choices)
        #print("ORDINAL", out[1], starts, ends)
        #do_rep_calculation_ordinal(users, answers, out[0], num_choices, out[1], hlUsers, starts, ends, length, repDF, thirtyDf)
        out = out+(question_type, num_choices)
    elif question_type == 'nominal':
        print('nominal', users)
        out = evaluateCoding(answers, users, starts, ends, numUsers, length,  sourceText,hlUsers, hlAns, repDF = repDF, num_choices=num_choices)
        #do_rep_calculation_nominal(users, answers, out[0], out[1], starts, ends, length, repDF)
        #print("NOMINAL", out[1], starts, ends)
        out = out+(question_type, num_choices)
    elif question_type == 'checklist':
        out = evaluateChecklist(answers, users, starts, ends, numUsers, length, repDF, sourceText, hlUsers, hlAns, num_choices = num_choices)
    return out


def calcAgreement(codingScore, unitizingScore):
    """averages coding and unitizing agreement scores to create a final agreement score to be used elsewhere in the
    Public Editor algorithm"""
    if codingScore == 'NA':
        return unitizingScore
    elif codingScore == 'L' or codingScore == 'M' or codingScore == 'U':
        return codingScore
    elif unitizingScore == 'NA':
        return codingScore
    elif unitizingScore == 'L' or unitizingScore == 'M' or unitizingScore == 'U':
        unitizingScore = 0

    return (float(codingScore) + float(unitizingScore)) / 2


def run_2step_unitization(data, article, question, repDF):
    starts, ends, length, numUsers, users = get_question_start(data, article, question).tolist(), get_question_end(data,
                                                                                                                   article,
                                                                                                                   question).tolist(), \
                                            get_text_length(data, article, question), get_num_users(data, article,
                                                                                                    question), get_question_userid(
        data, article, question).tolist()
    uqU = np.unique(users)
    userWeightDict = {}
    #for u in uqU:
        #userWeightDict[u] = get_user_rep(u, repDF)
    score, indices, iScore = scoreNuUnitizing(starts, ends, length, numUsers, users, userWeightDict)

    return 'NA', indices, score, score, 'NA'

# # # TEST STUFF
#calc_agreement_directory('./demo1', hardCodedTypes= True)
# calc_scores('./demo1/Demo1ArgRel3-2018-09-01T0658-DataHuntHighlights.csv', answersFile='./demo1/Demo1ArgRel3-2018-09-01T0658-DataHuntAnswers.csv',
#             schemaFile = './demo1/Demo1ArgRel3-2018-09-01T0658-Schema.csv', hardCodedTypes=True)
# calc_scores('./demo1/Demo1QuoSour-2018-09-01T0658-DataHuntHighlights.csv', answersFile='./demo1/Demo1QuoSour-2018-09-01T0658-DataHuntAnswers.csv',
#             schemaFile = './demo1/Demo1QuoSour-2018-09-01T0658-Schema.csv', hardCodedTypes=True)
# calc_scores('./demo1/Demo1Prob-2018-09-01T0758-DataHuntHighlights.csv', answersFile='./demo1/Demo1Prob-2018-09-01T0758-DataHuntAnswers.csv',
#             schemaFile = './demo1/Demo1Prob-2018-09-01T0758-Schema.csv', hardCodedTypes=True)
# calc_scores('./demo1/DemoLang-2018-09-01T0815-DataHuntHighlights.csv', answersFile='./demo1/DemoLang-2018-09-01T0815-DataHuntAnswers.csv',
#             schemaFile = './demo1/DemoLang-2018-09-01T0815-Schema.csv', hardCodedTypes=True)
#calc_scores('testhl.csv', answersFile = 'testans.csv', schemaFile='testsch.csv', hardCodedTypes=True)
#calc_agreement_directory('demo1',  hardCodedTypes=True)

#calc_scores('demo1/Demo1Prob-2018-08-28T2257-DataHuntHighlights.csv', hardCodedTypes= True)
# # calc_scores('data_pull_8_10/PreAlphaLanguage-2018-08-10T0420-DataHuntHighlights.csv', hardCodedTypes=True)
#calc_scores(path, hardCodedTypes=True)
# #in sss file I renamed the filenamecolumn to be sha256 so it fits in with the other mechanisms for extracting data
# calc_scores('data_pull_8_10/SSSPECaus2-2018-08-08T0444-DataHuntHighlights.csv', hardCodedTypes=True)
# calc_scores('data_pull_8_17/ArgumentRelevance1.0C2-2018-08-17T2012-DataHuntHighlights.csv')
# # calc_scores('data_pull_8_17/ArgumentRelevance1.0C2-2018-08-17T2012-DataHuntHighlights.csv')
# # calc_scores('data_pull_8_17/ArgumentRelevance1.0C2-2018-08-17T2012-DataHuntHighlights.csv')
