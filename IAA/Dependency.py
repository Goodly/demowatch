import math
import pandas as pd
import numpy as np
import os
import json
from dataV2 import *
def eval_dependency(directory, iaa_dir, out_dir = None):
    print("DEPENDENCY STARTING")
    if out_dir is None:
        out_dir = 'scoring_'+directory
    print('dir', directory, iaa_dir, out_dir)
    schema = []
    iaa = []
    for root, dir, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv') and 'Dep' not in file:
                print("evaluating dependencies  for "+directory+'/'+file)
                if 'Schema' in file:
                    schema.append(directory+'/'+file)
    for root, dir, files in os.walk(iaa_dir):
        for file in files:
            if file.endswith('.csv') and 'Dep' not in file:
                print("evaluating dependencies for "+directory+'/'+file)
                if 'S_IAA' in file:
                    iaa.append(iaa_dir+'/'+file)

    schema.sort()
    iaa.sort()
    assert(len(schema)==len(iaa), 'mismatched files ', len(schema), 'schema', len(iaa), 'iaa oututs')
    out_dir = make_directory(out_dir)
    for i in range(len(schema)):
        handleDependencies(schema[i], iaa[i], out_dir)
    return out_dir

def handleDependencies(schemaPath, iaaPath, out_dir):
    schemData = pd.read_csv(schemaPath, encoding = 'utf-8')
    iaaData = pd.read_csv(iaaPath,encoding = 'utf-8')
    dependencies = create_dependencies_dict(schemData)
    tasks = np.unique(iaaData['task_uuid'].tolist())
    iaaData['prereq_passed'] = iaaData['agreed_Answer']

    iaaData = iaaData.sort_values(['question_Number'])
    for t in tasks:
        #filter out questions that should never of been asksed because no agreement on prerequisites
        for q in range(len(iaaData)):
            qnum = iaaData['question_Number'].iloc[q]
            ans = iaaData['agreed_Answer'].iloc[q]
            iaaData['prereq_passed'].iloc[q] = checkPassed(qnum, dependencies, iaaData, t, ans)
    #     #get just the task
        iaaTask = iaaData[iaaData['task_uuid'] == t]

        iaaData = iaaData[iaaData['prereq_passed'] == True]
        iaaTask = iaaData[iaaData['task_uuid'] == t]

        #childQuestions
        for ch in dependencies.keys():

            child = dependencies[ch]
            needsLove = checkNeedsLove(iaaTask, ch)
            if needsLove:
                indices = np.zeros(0)
                alpha = np.zeros(0)
                alphainc = np.zeros(0)
                #check if this question even got a score
                iaaQ = iaaTask[(iaaTask['question_Number']) == (ch)]
                answers = iaaQ['agreed_Answer'].tolist()
                answers = find_real_answers(answers)
                rows = find_index(iaaQ, answers, 'agreed_Answer')
                validParent = False
                if len(answers)>0:
                    #questions the child depends on
                    for par in child.keys():
                        iaaPar = iaaTask[iaaTask['question_Number'] == (par)]
                        neededAnswers = child[par]

                        for ans in neededAnswers:
                            iaaparAns = iaaPar[iaaPar['agreed_Answer'] == ans]
                            if len(iaaparAns>0):
                                validParent = True
                                newInds = [get_indices_hard(ind) for ind in iaaparAns['highlighted_indices'].tolist()]
                                #newInds = parseList(newInds)
                                newAlph = iaaparAns['alpha_unitizing_score'].tolist()
                                newIncl = iaaparAns['alpha_unitizing_score_inclusive'].tolist()
                                for i in range(len(newInds)):
                                    indices = np.append(indices, newInds[i])
                                alpha = np.append(alpha, (newAlph[0]))
                                alphainc = np.append(alphainc, (newIncl[0]))
                #If parent didn't pass, this question should not of been asked
                if not validParent:
                    for row in rows:
                        iaaData.at[row,'agreed_Answer'] = -1
                        iaaData.at[row, 'coding_perc_agreement'] = -1
                indices = np.unique(indices).tolist()
                try:
                    alpha = alpha[0]
                    alphainc = alphainc[0]
                except IndexError:
                    alpha, alphainc = -1,-1

                for row in rows:
                    iaaData.at[row, 'highlighted_indices'] = json.dumps(indices)
                    iaaData.at[row, 'alpha_unitizing_score'] = alpha
                    iaaData.at[row, 'alpha_unitizing_score_inclusive'] = alphainc
    print('exporting to csv')
    path, name = get_path(iaaPath)

    iaaData.to_csv(out_dir+'Dep_'+name,  encoding = 'utf-8')

    print("Table complete")
    return out_dir

def parseList(iterable):
    out = []
    for i in range(len(iterable)):
        addendum = indicesFromString(iterable[i])
        out.append(addendum)
    return out
def checkNeedsLove(df, qNum):
    qdf = df[df['question_Number'] == qNum]
    alphas = (qdf['alpha_unitizing_score'])
    if qdf.empty:
        return False
    for a in alphas:
        if not checkIsNum(a):
            return False
    return True

def checkPassed(qnum, dependencies, iaadata, task, answer):
    iaatask = iaadata[iaadata['task_uuid'] == task]
    qdata = iaatask[iaatask['question_Number'] == qnum]
    if not checkIsNum(answer):
        return False
    #print('keys', dependencies.keys())
    if qnum in dependencies.keys():
        #fprint("QNUM", qnum)
        #this loop only triggered if child question depends on a prereq
        for parent in dependencies[qnum].keys():
            pardata = iaatask[iaatask['question_Number'] == parent]
            parAns = pardata['agreed_Answer'].tolist()
            valid_answers = dependencies[qnum][parent]
            for v in valid_answers:
                strv = str(v)
                if strv in parAns:
                    par_ans_data = pardata[pardata['agreed_Answer'] == strv]
                    #print(len(par_ans_data['prereq_passed']), 'ppassed', par_ans_data['prereq_passed'])
                    if par_ans_data['prereq_passed'].iloc[0] == True:
                       return True
            return False
    return True


def checkIsNum(value):
    try:
        j = float(value) + 1
        ans = math.isnan(j)
        if ans:
            return False
        return True
    except:
        pass
    return False
def find_real_answers(answers):
    out = []
    for a in answers:
        if isinstance(a, int) or a.isdigit():
            out.append(int(a))
    return out


def find_index(df, targetVals,col):
    indices = []
    for v in targetVals:
        shrunk = df[df[col] == v]
        if len(shrunk)>0:
            inds = []
            for i in shrunk.index:
                inds.append(i)
            for i in inds:
                indices.append(i)
    return indices

#eval_depenency('./demo1')
