from dataV2 import *
from math import exp
import numpy as np
import pandas as pd
from dataV2 import *
import ast


def create_user_reps(uberDict, csvPath=None):
    if csvPath:
        user_rep = pd.read_csv(csvPath)
    else:
        user_rep = pd.DataFrame(columns=['Users', 'Score', 'Questions', 'Influence', 'Index'] + list(range(30)))
    for article_sha256 in uberDict.keys():
        for question_num in uberDict[article_sha256]['quesData'].keys():
            # TODO make this not hardCoded, it's identical to data_utils get quesiton userid but we had importerror
            # users_q = data[article_num][question_num][1][1][0]
            users_q = get_question_userid(uberDict, article_sha256, question_num)

            for ids in users_q:
                print(len((users_q)))
                print(set(users_q))
                if ids not in user_rep.loc[:, 'Users'].tolist():
                    print((ids))
                    user_rep = user_rep.append(pd.Series([ids, 5, 1, 1, 0] + list(np.zeros(30)),
                                                         index=['Users', 'Score', 'Questions', 'Influence',
                                                                'Index'] + list(range(30))), ignore_index=True)
    return user_rep


def do_rep_calculation_nominal(userID, answers, answer_choice, highlight_answer, hlUsers, starts, ends, article_length,
                               user_rep_df,
                               checkListScale=1):
    """Using the same dataframe of userIDs, rep scores, and number of questions, changes the vals of the dataframe
    such that if the user in the list of USERID gets their answer right, they add 1 to their score, and 0 if they are
    wrong."""
    if type(answer_choice) == str or type(highlight_answer) == str or len(highlight_answer) == 0:
        print('oh')
        return 0

    checked = zip(answers, userID)
    highlight_answer_array = np.zeros(article_length)
    winners = []
    print(answers, userID)
    for t in checked:
        user = t[1]
        answer = t[0]

        if (answer == answer_choice):
            print('yay', answer, answer_choice, user)
            do_math(user_rep_df, user, checkListScale)
            winners.append(user)
        else:
            do_math(user_rep_df, user, 0)
    for h in highlight_answer:
        highlight_answer_array[h] = 1

    for x in userID:
        user_highlight = np.zeros(article_length)
        for user_h, user_s, user_e in zip(hlUsers, starts, ends):
            incrementer = user_s
            if user_h == x:
                while incrementer <= user_e:
                    user_highlight[incrementer] = 1
                    incrementer += 1
        score = 1 - np.sum(np.absolute(highlight_answer_array - user_highlight)) / article_length
        do_math(user_rep_df, x, score)



def gaussian_mean(answers):
    result = []
    std = np.std(answers)
    mean = np.mean(answers)
    total = 0
    for i in answers:
        gauss = 1 / (std * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((i - mean) / std) ** 2)
        result.append(i * (gauss * 10) ** 2)
        total += (gauss * 10) ** 2

    return sum(result) / total


def do_rep_calculation_ordinal(userID, answers, answer_aggregated, num_of_choices, highlight_answer, hlUsers, starts,
                               ends,
                               article_length, user_rep_df):
    """Using the same dataframe of userIDs, rep scores, and number of questions, changes the vals of the dataframe
    such that the they receive the distance from the average answer chosen as a ratio of 0 to 1,
    and that is added to their rep score."""

    if type(answer_aggregated) == str or type(highlight_answer) == str:
        return 0
    checked = zip(answers, userID)
    highlight_answer_array = np.zeros(article_length)
    score_dict = {}

    answer_choice = gaussian_mean(answers)
    print(answer_aggregated, answer_choice, answers)
    for h in highlight_answer:
        highlight_answer_array[h] = 1

    for t in range(len(userID)):
        user = userID[t]
        answer = answers[t]
        print(user, answer)
        points = (1 - abs(answer_choice - answer) / num_of_choices)
        do_math(user_rep_df, user, points)
        score_dict[user] = points

    if len(userID) != 4:
        print(userID)
        print("wtf")
    for x in userID:
        points = score_dict[x]
        user_highlight = np.zeros(article_length)
        print(article_length, "hwat is going on")
        for user_h, user_s, user_e in zip(hlUsers, starts, ends):
            incrementer = user_s
            if user_h == x:
                while incrementer <= user_e:
                    user_highlight[incrementer] = 1
                    incrementer += 1
        print(points, highlight_answer_array, user_highlight, article_length, "nani")
        score = points * (1 - np.sum(np.absolute(highlight_answer_array - user_highlight)) / article_length)
        print(score, "hold up")
        do_math(user_rep_df, x, score)


def getUserHighlights(userId, hlUsers, starts, ends, length):
    hlUsers = np.array(hlUsers)
    starts = np.array(starts)
    ends = np.array(ends)
    userMask = hlUsers == userId
    print(userMask)
    uStarts = starts[userMask]
    uEnds = ends[userMask]
    hlArr = startsToBool(uStarts, uEnds, length)
    return hlArr


def startsToBool(starts, ends,length):
    out = np.zeros(length)
    for i in range(len(starts)):
        for x in range(starts[i], ends[i]):
            out[x] = 1
    return out

def checkDuplicates(answers, userID, starts, ends, article_length):
    checked = []
    int_users = {}
    #Changed this to just starts, ends; guaranteed no duplicates of answers or userID
    for i in range(len(starts)):
        if [starts[i], ends[i]] not in checked:
            checked.append([starts[i], ends[i]])
    for x in checked:
        article_array = np.zeros(article_length).tolist()
        if x[0] not in int_users.keys():
            print("HELLO THERE", x[2], x[3])
            article_array[x[2]:x[3] + 1] = np.ones(x[3] - x[2] + 1).tolist()
            int_users[x[0]] = article_array
        else:
            article_array = int_users[x[0]]
            article_array[x[2]:x[3] + 1] = np.ones(x[3] - x[2] + 1).tolist()
            int_users[x[0]] = article_array

    return checked, int_users


def do_math(data, userID, reward):
    """This function takes in the points added to one user and changes the dataframe to update that one user's score
    using the equations set for calculating reputation."""

    oldlast30mean = np.mean(np.array(data.loc[data['Users'] == userID, range(30)]))
    # oldlast30q_score = len(np.array(data.loc[data['Users'] == userID, range(30)]))
    oldlast30score = np.sum(np.array(data.loc[data['Users'] == userID, range(30)]))
    user = data.loc[data['Users'] == userID]
    index = data.loc[data['Users'] == userID, 'Index'].tolist()[0]
    data.loc[data['Users'] == userID, index] = reward

    last30 = data.loc[data['Users'] == userID, range(30)]
    last30mean = np.mean(np.array(last30.dropna(axis=1)))
    # last30q_score = len(np.array(last30.dropna(axis=1)))
    last30score = sum(np.array(last30.dropna(axis=1)))

    if (index < 29):
        data.loc[data['Users'] == userID, 'Index'] = index + 1
    else:
        data.loc[data['Users'] == userID, 'Index'] = 0

    r = float(user['Score'].iloc[0]) * 2 - oldlast30mean * 30
    n = float(user['Questions'].iloc[0])

    # q_score = 1.5 * (1 - exp(-n / .7))

    points = r * n
    points = points + reward

    n = n + 1
    data.loc[data['Users'] == userID, 'Questions'] = n
    # q_score = 1.5 * (1 - exp(-n / .7))

    if n > 29:
        data.loc[data['Users'] == userID, 'Score'] = ((points) + last30mean * 30) / 2
    else:

        data.loc[data['Users'] == userID, 'Score'] = ((points / n))

    score = data.loc[data['Users'] == userID, 'Score']
    data.loc[data['Users'] == userID, 'Influence'] = 2 / (1 + exp(-.07 * score + 2))


def calc_influence(data, userID):
    """Taking in a list of UserID's, this will take the repuation score of each User and output a list of their influence
    based on their reputation score."""
    return_vals = list()
    for u in userID:
        r = data.loc[data['Users'] == u]['Score']
        inf = 2 / (1 + exp(-r + 5))
        return_vals.append(inf)
    return return_vals


def user_rep_task(uberDict, task_csv, user_rep_df):
    """This is the function every time agreement is calculated. To use, input the master data structure, the agreed upon
    answers csv, and the pre-existing user_rep dataframe created by function create_user_reps."""
    answers = pd.read_csv(task_csv)
    for i in answers.itertuples():
        article_sha = i[2]
        agreement = i[7]
        task_num = i[3]
        question_num = i[5]
        question_type = i[6]
        highlights = i[10]
        if highlights == 'L' or highlights == 'M' or highlights == 'U':
            None
        else:

            highlights = ast.literal_eval(i[10])
        num_of_users = i[16]
        users = get_question_userid(uberDict, task_num, question_num)
        answers = get_question_answers(uberDict, task_num, question_num)

        user_highlights_id = get_question_hlUsers(uberDict, task_num, question_num)
        user_highlights_start = get_question_start(uberDict, task_num, question_num)
        user_highlights_end = get_question_end(uberDict, task_num, question_num)
        user_highlights_answer = get_question_hlAns(uberDict, task_num, question_num)
        article_len = get_text_length(uberDict, task_num, question_num)
        number_of_answers = i[17]
        if agreement == 'L' or agreement == 'M' or agreement == 'U' or agreement == 0 or type(article_len) == pd.Series:
            pass
        else:
            print("yaya")
            agreement = int(agreement)
            if question_type == 'nominal':
                do_rep_calculation_nominal(users, answers, agreement, highlights, user_highlights_id,
                                           user_highlights_start, user_highlights_end, article_len,
                                           user_rep_df=user_rep_df)

            if question_type == 'ordinal':
                hl_users = get_question_hlUsers(uberDict, task_num, question_num)
                print(users, hl_users)
                do_rep_calculation_ordinal(users, answers, agreement, number_of_answers, highlights, hl_users,
                                           user_highlights_start, user_highlights_end, article_len,
                                           user_rep_df=user_rep_df)
            elif question_type == 'checklist':
                i = 0
                user_array = [0] * num_of_users
                answer_array = [0] * num_of_users
                highlight_users_array = []
                highlight_starts = []
                highlight_ends = []
                for a, u in zip(answers, users):
                    if i == num_of_users:
                        break
                    if int(a) == int(agreement):
                        user_array[i] = u
                        answer_array[i] = 1
                    else:
                        if u not in user_array:
                            user_array[i] = u
                    i += 1

                for h_a, h_u, h_s, h_e in zip(user_highlights_answer, user_highlights_id, user_highlights_start,
                                              user_highlights_end):
                    if h_a == agreement:
                        highlight_users_array.append(h_u)
                        highlight_starts.append(h_s)
                        highlight_ends.append(h_e)
                do_rep_calculation_nominal(user_array, answer_array, 1, highlights, highlight_users_array,
                                           highlight_starts, highlight_ends, article_len, user_rep_df)


def userid_to_CSV(dataframe):
    """This function will save the User Rep Score dataframe as UserRepScores.csv"""
    dataframe.to_csv("UserRepScores.csv")


def CSV_to_userid(path):
    """This function will take in the path name of the UserRepScore.csv and output the dataframe corresponding."""
    return pd.read_csv(path, index_col=False).loc[:, ['Users', 'Score', 'Questions', 'Influence']]


def last30_to_CSV(dataframe):
    """This function will save the last 30 questions rep points dataframe as last30.csv"""
    dataframe.to_csv("last30.csv")


def CSV_to_last30(path):
    """This function opens the csv of the last 30 questions rep points dataframe as last30.csv"""
    return pd.read_csv(path, index_col=False).loc[:, ['Users', 'Index'] + list(range(30))]

def get_user_rep(id, repDF):
    if repDF is None:
        return 50
    if repDF.loc[repDF['Users']==id]['Questions'].iloc[0]<30:
        influence = .8
    else:
        influence = float(repDF.loc[repDF['Users']==id]['Influence'].iloc[0])
    return influence*50

