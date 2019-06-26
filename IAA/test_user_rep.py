import numpy as np
import pandas as pd
import random as rand
from IAA import *

def create_run(agreement, num_run, num_users = 5, num_questions = 10, source_len = 2000, ans_type = 'nominal'):
    """Parameters: Agreement - an array of length = num_users. Each element is a number from 0 to 1 that
    describes how likely it is for that user to agree with the majority. O means least likely an 1 means
    most likely.
    All other parameters are taken from the run dataframe.
    This function returns a dataframe that describes a run of length = num_questions."""
    rows = np.zeros(num_users * num_questions)
    inputs = generate_agreement(agreement, num_users, num_questions, source_len)
    d = {'taskrun_article_number': rows + num_run,
         'contributor_id': np.tile(np.arange(1, num_users + 1), num_questions),
         'question_number': np.repeat(np.arange(1, num_questions + 1), num_users),
         'answer_number': inputs[0], 'start_pos': inputs[1],
         'end_pos': inputs[2], 'source_text_length': rows + source_len,
         'answer_type': np.repeat(ans_type, len(rows)), 'question_text': rows}
    run = pd.DataFrame(d)
    run = run[['taskrun_article_number', 'contributor_id',
         'question_number', 'answer_number', 'start_pos',
         'end_pos', 'source_text_length', 'answer_type', 'question_text']]
    return run

def generate_agreement(agreement, num_users, num_questions, source_len):
    answer_number= np.zeros(0)
    start_pos = np.zeros(0)
    end_pos = np.zeros(0)
    for i in np.arange(num_questions):
        correct_ans = rand.randint(1, 5)
        correct_start = rand.randint(source_len / 4, source_len / 2)
        correct_end = correct_start + get_highlight_length()
        for j in np.arange(num_users):
            answer_number = np.append(answer_number, weighted_random_question(agreement[j], correct_ans))
            start = weighted_random_pos(agreement[j], correct_start, source_len)
            end = weighted_random_pos(agreement[j], correct_end, source_len)
            if start > end:
                temp = start
                start = end
                end = temp
            start_pos = np.append(start_pos, start)
            end_pos = np.append(end_pos, end)
    return answer_number, start_pos, end_pos

def weighted_random_question(agreement_val, correct_ans):
    my_list = []
    for i in np.arange(1, 6):
        if i == correct_ans:
            my_list += [str(correct_ans)] * int(agreement_val * 100)
        else:
            if agreement_val >= 0.5:
                my_list += [str(i)] * int((1 - agreement_val) / abs(correct_ans - i) * 100)
            else:
                my_list += [str(i)] * int((1 - agreement_val) * abs(correct_ans - i) * 100)
    return int(rand.choice(my_list))

def weighted_random_pos(agreement_val, correct_ans, source_length):
    normal = np.random.normal(correct_ans, (1 - agreement_val) * 2 * source_length ** 0.5, 10000)
    return int(rand.choice(normal))

def get_highlight_length():
    normal = np.random.normal(50, 12, 10000)
    return int(rand.choice(normal))

def create_series(agreement_arr):
    """Parameters: agreement_arr - a 2D array of agreement values with length = number of runs. Each
    sub-array is a list of agreement values with length = num_users.
    Returns a series of runs, saved as .csv that describes the answers and highlights of users according
    to their given agreement values."""
    frames = []
    for i in np.arange(len(agreement_arr)):
        current = create_run(agreement_arr[i], i)
        frames.append(current)
    result = pd.concat(frames)
    result.to_csv('Series_Output\Series1.csv')
    return frames

def create_runs(agreement_arr):
    for i in np.arange(len(agreement_arr)):
        current = create_run(agreement_arr[i], i)
        current.to_csv('RepScore\Run' + str(i) + '.csv')
def test_rep(path):
    for i in range(50):
        if i == 0:
            calc_scores(path + 'Run' + str(i) + '.csv')
        else:
            calc_scores(path + 'Run' + str(i) + '.csv', 'UserRepScores.csv')
