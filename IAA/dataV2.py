import pandas as pd
import numpy as np
import ast
from math import floor
import json
import os


def data_storer(path, answerspath, schemapath):
    """Function that turns csv data. Input the path name for the csv file.
    This will return a super dictionary that is used with other abstraction functions."""
    highlightData = pd.read_csv(path, encoding = 'utf-8')
    answersData = pd.read_csv(answerspath, encoding = 'utf-8')
    schemaData = pd.read_csv(schemapath, encoding = 'utf-8')
    task_uuid = np.unique(answersData['quiz_task_uuid'])
    uberDict = {}
    for task in task_uuid:
        task_ans = answersData[answersData['quiz_task_uuid'] == task]
        task_hl = highlightData[highlightData['quiz_task_uuid'] == task]
        qlabels, qNums = get_questions(task_ans)
        uberDict[task] = {}


        #use Qlabels to find things in the input csvs, use Qnums within the program
        schema_name = find_schema(task_ans)
        task_schema = schemaData[schemaData['schema_namespace'] == schema_name]
        article_num, article_sha = find_article_data(task_ans)
        schema_style = find_schema_topic(task_schema)
        #down the road cache this to make it go faster
        dependencies = create_dependencies_dict(task_schema)
        uberDict[task]['taskData'] = {
            'question_labels': qlabels,
            'question_numbers': qNums,
            'article_num':article_num,
            'article_sha':article_sha,
            'schema_name':schema_style,
            'dependencies': dependencies
        }
        numUsersD = makeNumUsersDict(task_ans)
        qDict = {}
        for i in range(len(qNums)):
            qnum = qNums[i]
            qlabel = findLabel(qlabels, qnum)
            numUsers = findNumUsers(numUsersD, qlabel)
            q_type = get_q_type(task_schema, qlabel)
            answer_contents = find_answer_contents(task_schema, qlabel)
            question_text = find_question_text(task_schema, qlabel)
            #ANSWER block
            if q_type == 'CHECKBOX':
                answers, users= find_answers_checklist(task_ans, qnum)
            elif q_type == 'TEXT':
                answers, users = [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0]
            elif q_type == 'RADIO':
                answers, users = find_answers_radio(task_ans, qlabel, task_schema)
                assert(len(answers) == len(users))
            starts, ends, hlUsers, length, targetText, hlAns = findStartsEnds(task_schema, qlabel, task_hl)
            qDict[qnum] = {
               'answers': answers,
               'users': users,
               'numUsers': numUsers,
               'starts': starts,
               'ends': ends,
               'hlUsers': hlUsers,
               'length': length,
               'target_text': targetText,
                'hlAns': hlAns,
                'answer_content': answer_contents,
                'question_text': question_text,
                'parents': dependencyStatus(dependencies, qnum)
             }
        uberDict[task]['quesData'] = qDict
    return uberDict


def dependencyStatus(dependencies, qnum):
    try:
        return dependencies[qnum]
    except:
        return {}
def evalDependency(data, task_id, parentdata, question, answer, indices, alpha, alphainc):
    depDict = get_article_dependencies(data, task_id)
    try:
        l = answer+5
        isInt = True
    except:
        isInt = False
    if isInt and isinstance(indices, list):
        parentdata = saveParentData(depDict, parentdata,question, answer, indices, alpha, alphainc)
    elif isinstance(answer, int):
        if checkIfChild(depDict, question):
            parents = get_question_parents(data, task_id, question)
            indices, alpha, alphainc = get_parent_data(parents, parentdata)
    return parentdata, indices, alpha, alphainc

def get_parent_data(parents, parentData):
    indices = []
    alpha = []
    alphainc = []
    for p in parents.keys():
        for a in parents[p]:
            try:
                newInd = parentData[p][a][0]
                newAlph = parentData[p][a][1]
                newAlphinc = parentData[p][a][2]
                indices.append(newInd)
                alpha.append(newAlph)
                newAlphinc.append(newAlphinc)
            except:
                print('parentdata not found')
    indices = np.unique(indices)
    alpha = average(alpha)
    alphainc = average(alphainc)
    return indices, alpha, alphainc


def average(alpha):
    if len(alpha) == 0:
        return 0
    return np.mean(alpha)
def checkIfChild(depDict, question):
    if question in depDict.keys():
        return True
def saveParentData(dependenciesDict, parentData, question, answer, indices, alpha, alphainc):
    if checkIfParent(dependenciesDict, question, answer):
        parentData[question] = parentAddendum(parentData, answer, [indices, alpha, alphainc])
    return parentData
def parentAddendum(parentData, answer, newStuff):
    if answer not in parentData.keys():
        parentData[answer] = [newStuff]
    else:
        parentData[answer].append(newStuff)
    return parentData
def checkIfParent(dependenciesDict, question, answer):
    for k in dependenciesDict.keys():
        if question in dependenciesDict[k].keys():
            if answer in dependenciesDict[k][question]:
                return True
            return False


def create_dependencies_dict(schemadata):
    dependers = schemadata[schemadata['answer_next_questions'].notnull()]
    allChildren = dependers['answer_next_questions'].tolist()
    parents = dependers['answer_label'].tolist()
    tempDict = dict()
    for i in range(len(allChildren)):
        dictAddendumList(tempDict, allChildren[i], parents[i])
    d = {}
    for k in tempDict.keys():
        questions = parseMany(k,'Q',',')
        thisParents = tempDict[k]
        thisParentQs = [parse(thisParent, 'Q', '.') for thisParent in thisParents]
        thisParentAs = [parse(thisParent, 'A', ',') for thisParent in thisParents]
        extendedFamDict = {}
        for i in range(len(thisParentQs)):
            extendedFamDict = dictAddendumList(extendedFamDict, thisParentQs[i], thisParentAs[i])
        for q in questions:
            #d[q] = extendedFamDict
            d = dictAddendumDict(d, q, extendedFamDict)

    # parQuestions = [parse(parLab, 'Q', '.') for parLab in parents]
    # parAnswers = [parse(parLab, 'A', '.') for parLab in parents]
    # childQuestions = [parse(childLabel, 'Q', ',') for childLabel in allChildren]
    return d
def dictAddendumDict(dict, key, newDict):
    if key not in dict.keys():
        dict[key] = newDict
    else:
        for k in newDict:
            if k in dict[key].keys():
                dict[key][k].append(newDict[k][0])
            else:
                if isinstance(newDict[k][0], list):
                    dict[key][k] = newDict[k][0]
                else:
                    dict[key][k] = [newDict[k][0]]
    return dict

def deepAddendumDicts(dict, key,newDict):
    return
def dictAddendumList(dict, key, newFriend):
    if key not in dict.keys():
        if isinstance(newFriend, list):
            dict[key] = newFriend
        else:
            dict[key] = [newFriend]
    else:
        curr = dict[key]
        curr.append(newFriend)
    return dict
def find_question_text(schemadata,qlabel):
    questiondf = schemadata[schemadata['question_label'] == qlabel]
    qText = questiondf['question_text'].iloc[0]
    return qText


def find_answer_contents(schemadata, qlabel):
    questiondf = schemadata[schemadata['question_label'] == qlabel]
    pot_answers = questiondf['answer_content'].tolist()
    pot_answers.insert(0,'zero')
    return pot_answers


def find_article_data(task_ans):
    return task_ans['article_number'].iloc[0], task_ans['article_sha256'].iloc[0]


def indicesFromString(indices):
    indices = clearBogusChars(indices)
    try:
        return json.loads(indices)
    except TypeError:
        return json.loads((str(indices).replace(' ', ', ')))
    except:
        filtered = []
        for s in indices:
            f = s.replace('\n', '')
            if ',' not in f:
                f = f.replace(' ', ', ')
            f = ast.literal_eval(f)
            filtered.append(f)
    return filtered
def clearBogusChars(string):
    if not isinstance(string, str):
        string = str(string)
    string = string.replace("\\", "")
    string = string.replace("\n", '')
    string = string.replace('n', '')
    string = string.replace("'", '')
    string = string.replace('"', '')
    string = string.replace(' , ', '')
    string = string.strip()
    string = string.replace(',,',',')
    i = 1
    while not string[i].isdigit():
        i+=1
    string = string[0]+string[i:]
    return string
def findStartsEnds(schemadata, qlabel, highlightdata):
    # hasHighlight = max(questiondf['nohighlight'])<1
    # if hasHighlight:
    #TODO: implement a check to see if people thought there should've been a highlight
    #Don't filter by answer for checklist questions here
    relevant_hl = highlightdata[highlightdata['question_label'] == qlabel]
    starts = relevant_hl['start_pos'].tolist()
    ends = relevant_hl['end_pos'].tolist()
    users = relevant_hl['contributor_uuid'].tolist()
    length = relevant_hl['source_text_length']
    answerText = relevant_hl['target_text'].str.decode('unicode-escape')
    answer_labels = relevant_hl['answer_label']
    answer_nums = [parse(ans, 'A') for ans in answer_labels]
    return starts, ends, users, length, answerText, answer_nums
    #else:
        #return [0], [0], [0], 0, '',[0]


def checkIfHighlight(answers, qlabel, questiondf):
    numAns = len(answers)
    ansLabels = [AnstoLabel(ans) for ans in answers]


def AnstoLabel(answer, qlabel):
    return qlabel+'.A'+str(answer)
def makeNumUsersDict(answerData):
    queue = answerData['final_queue']
    d = {}
    for ro in queue:
        lis = parseMany(ro, separator=',')
        for label in lis:
            d = dictIncrement(d, label)
    return d
def dictIncrement(dict, k):
    if not k in dict.keys():
        dict[k] = 1
    else:
        dict[k] = dict[k]+1
    return dict
def findNumUsers(numUsersDict, qlabel):
    """

    :param schemadata: df from current schema
    :param qlabel: questionlabel of current question
    :return: numUsers,
    """
    return numUsersDict[qlabel]


def find_answers_radio(ansData, qlabel, schemaData):
    ansData = ansData.dropna(subset=[qlabel])
    col = ansData[qlabel]
    assert (len(col) == len(col.dropna()))
    stringAnswers = col.tolist()
    users = ansData['contributor_uuid'].tolist()
    assert(len(stringAnswers) == len(users))
    numAnswers = []
    for ans in stringAnswers:
        if isinstance(ans, int):
            numAnswers.append(ans)
        else:
            numAnswers.append(stringAnsToInt(schemaData, ans, qlabel))
    return numAnswers, users


def stringAnsToInt(schemadata, answer, qlabel):
    questiondf = schemadata[schemadata['question_label'] == qlabel]
    ansMatched = questiondf[questiondf['answer_content'] == answer]
    ansLabel = ansMatched['answer_label'].iloc[0]
    numAnswer = parse(ansLabel,'A')
    return numAnswer
def findLabel(qlabels, qnum):
    for label in qlabels:
        if str(qnum) in label:
            if parse(label, 'Q') == qnum:
                return label

def find_answers_checklist(ans_data, qnum):
    columns = ans_data.head(0)
    good_cols =find_matching_columns(columns, qnum)
    answers = []
    users = []
    for colName in good_cols:
        aNum = parse(colName, 'A')
        column = ans_data[colName]
        ansCount = sum(column)
        answeredRows = ans_data[ans_data[colName]!=0]
        newUsers = answeredRows['contributor_uuid'].tolist()
        for newU in range(len(newUsers)):
            users.append(newUsers[newU])

        for i in range(ansCount):
            answers.append(aNum)
    return answers, users
def find_matching_columns(cols, qnum):
    #This needs columns to be in ascending order by question number
    out = []
    found = False
    answerCols = []
    for col in cols:
        if 'Q' in col and '.' in col:
            if parse(col, 'Q', '.') == qnum:
                out.append(col)
    return np.unique(out)


def get_q_type(schemaData, qLabel):

    return schemaData[schemaData['question_label'] == qLabel].iloc[0]['question_type']
def get_indices_hard(string):
    if isinstance(string, list):
        if len(string == 1) and isinstance(string[0], str):
            string = string[0]
    out = []
    num = 0
    for i in range(len(string)):
        if string[i].isdigit():
            num = 10*num+int(string[i])
        elif num!=0:
            out.append(num)
            num = 0
    return out

def find_schema_topic(schemaData):

    return schemaData.iloc[0]['topic_name']

def find_schema(ansData):

    return ansData['schema_namespace'].iloc[0]

def get_questions(ansData):
    relTags = np.zeros(0)
    relNums = np.zeros(0)
    relTopics = np.zeros(0)
    for queue in ansData['final_queue']:
        relTags = np.append(relTags, parseMany(queue, separator = ','))
        #qnum = parseMany(queue, field = 'Q', separator = ',')
        #tnum =
        relNums = np.append(relNums, parseMany(queue, field = 'Q', separator=','))
        relTopics = np.append(relTopics, parseMany(queue, field = 'T', separator=','))

    ### A hack to deal with topic numbers in DW project...not necessary for PE.
    relNums = relNums + (relTopics * 100)
    
    relTags = np.unique(relTags)
    relNums = np.unique(relNums).astype(int)
    return relTags, relNums

def readIndices(strIndices):
    #end = strIndices.index(']')
    separated = parseMany(strIndices[1:-1], separator = ' ')
    fin = [int(floor(float(i))) for i in separated]
    return fin

def parseMany(base, field = None, separator = None):
    """
    returns
    :param base: input string
    :param field: char that you want the number after
    :param separator: char separating useful strings
    :return: the field desired, if there's a separator returns a list of everything from the field
    """
    if separator == None:
        return parse(base, field)
    else:
        out = []
        while len(base)>0:
            if separator in base:
                end = base.index(separator)
            else:
                end = len(base)
            label = parse(base[:end], field)
            out.append(label)
            base = base[end+1:]
    return out

def parse(base, field, end = None):
    if field == None:
        return base.strip()
    if end != None:
        aSpot = base.index(field)
        rest  =base[aSpot:]
        try:
            eSpot = rest.index(end)+aSpot
        except:
            return int(base[aSpot+1:])
        #if this is a bug then has to be end+1 or end -1
        ansString = base[aSpot +1: eSpot]
        return int(ansString)
    aSpot = base.index(field)
    ### Part of the hack for topic nums in DW project...
    if field == 'T':
        endpt = base.index('.')
        ansString = base[aSpot+1:endpt]
    else:
        ansString = base[aSpot+1:]
    return int(ansString)

def get_question_answers(data, task_id, question_num):

    return data[task_id]['quesData'][question_num]['answers']


def get_question_userid(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['users']

def get_question_highlight_userid(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['hlUsers']

def get_question_start(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['starts']

def get_question_end(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['ends']


def get_text_length(data, task_id, question_num):
    try:
        #TODO investigate why this is sometimes a series
        return data[task_id]['quesData'][question_num]['length'].iloc[0]
    except:
        return data[task_id]['quesData'][question_num]['length']

def printType(iterable):
    for i in iterable:
        print(type(i))
def get_num_users(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['numUsers']

def get_answer_texts(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['target_text'].tolist()

def get_schema(data, task_id):
    return data[task_id]['taskData']['schema_name']

def get_question_hlUsers(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['hlUsers']
def get_question_hlAns(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['hlAns']

def get_article_num(data,task_id):
    return data[task_id]['taskData']['article_num']
def get_article_sha(data,task_id):
    return data[task_id]['taskData']['article_sha']


def get_question_type(data, task_id, question_num):
    return None


def get_answer_content(data, task_id, question_num, answer_num):
    if answer_num == 'U' or answer_num == 'L' or answer_num == 'M' or answer_num == 'N/A':
        return answer_num
    contents = data[task_id]['quesData'][question_num]['answer_content']
    myAnswer = contents[answer_num]
    return myAnswer

def get_question_text(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['question_text']

def get_question_parents(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['parents']

def get_article_dependencies(data,task_id):
    return data[task_id]['taskData']['dependencies']

def get_namespace(data, article, question_num):
    return data[article][question_num][1][7][0].iloc[0]

def finder(ser, a):
    if len(ser)<1:
        return -1
    for i in range(len(ser)):
            if ser[i]==a:
                    return i
    return -1
def make_directory(directory):
    if directory[-1] != '/':
        directory = directory +'/'
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass
    return directory
def get_type_hard(type, ques):
    #ques = parse(ques, 'Q')
    print('type', type, ques)

    ### typing_dict is a super-dictionary. In typing_dict:
    ###     Keys are names of schemas. 
    ###     Values are dictionaries, where
    ###         Keys are question numbers in the schema.
    ###         Values are two item lists, where:
    ###             Item 0 is the type of question (nominal, ordinal, etc.).
    ###             Item 1 is the number of possible answer choices.

    ### typing_dict can be dynamically updated as new schemas are developed. 

    typing_dict = {
        'Police':
            {
                1: ['nominal', 3],
                2: ['checklist', 6],
                101: ['nominal', 9],
                102: ['checklist', 12],
                104: ['checklist', 8],
                105: ['checklist', 9],
                106: ['checklist', 7],
                107: ['nominal', 10],
                108: ['checklist', 14],
                109: ['nominal', 3],
                110: ['ordinal', 6],
                111: ['checklist', 7],
                112: ['nominal', 5],
                113: ['checklist', 6],
                114: ['checklist', 8],
                115: ['checklist', 7],
                116: ['checklist', 6],
                201: ['checklist', 3],
                202: ['checklist', 11],
                203: ['checklist', 7],
                204: ['ordinal', 6],
                205: ['ordinal', 6],
                206: ['ordinal', 6],
                207: ['ordinal', 9],
                301: ['nominal', 3],
                302: ['nominal', 5],
                303: ['text', 1],
                304: ['text', 1],
                305: ['nominal', 2],
                306: ['ordinal', 13],
                307: ['text', 1],
                308: ['nominal', 3],
                309: ['nominal', 5],
                310: ['text', 1],
                311: ['text', 1],
                312: ['ordinal', 12],
                313: ['ordinal', 12],
                314: ['text', 1],
                315: ['nominal', 7],
                316: ['nominal', 5],
                317: ['text', 1],
                318: ['text', 1],
                319: ['nominal', 2],
                320: ['ordinal', 13],
                321: ['text', 1],
                322: ['nominal', 3],
                323: ['nominal', 5],
                324: ['text', 1],
                325: ['text', 1],
                326: ['ordinal', 12],
                327: ['ordinal', 12],
                328: ['text', 1],
                329: ['nominal', 7],
                330: ['checklist', 15],
                331: ['checklist', 7],
                332: ['checklist', 11],
                333: ['checklist', 12],
                334: ['checklist', 7],
                335: ['checklist', 7],
                336: ['checklist', 8],
                337: ['checklist', 25],
                401: ['nominal', 5],
                402: ['text', 1],
                403: ['text', 1],
                404: ['nominal', 7],
                405: ['checklist', 15],
                406: ['checklist', 7],
                501: ['nominal', 7],
                503: ['text', 1],
                504: ['text', 1],
                505: ['checklist', 13],
                506: ['nominal', 3],
                507: ['ordinal', 6],
                508: ['checklist', 11],
                509: ['checklist', 6],
                510: ['checklist', 6],
                601: ['nominal', 3],
                602: ['nominal', 7],
                603: ['nominal', 5],
                604: ['text', 1],
                605: ['text', 1],
                606: ['nominal', 3],
                607: ['ordinal', 6],
                608: ['nominal', 7],
                609: ['nominal', 5],
                610: ['text', 1],
                611: ['text', 1],
                612: ['nominal', 3],
                613: ['nominal', 6],
                614: ['nominal', 5],
                615: ['text', 1],
                616: ['text', 1],
                617: ['nominal', 3],
                618: ['ordinal', 6],
                619: ['nominal', 7],
                620: ['nominal', 5],
                621: ['text', 1],
                622: ['text', 1],
                623: ['nominal', 3],
                624: ['nominal', 4],
                625: ['text', 1],
                626: ['text', 1],
                627: ['nominal', 7],
                628: ['checklist', 7]
            },
    }

    out = typing_dict[type][ques]
    #print('typing success', out[0], out[1])
    return out[0], out[1]


#for purpose of naming outputFile
def get_path(fileName):
    name = ''
    path = ''
    for c in fileName:
        name = name +c
        if c == '/':
            path = path + name
            name = ''
    return path, name

#############TEST CASES

# ans = pd.read_csv('testans.csv')
# print(ans.head(0))
# q = ans['final_queue']
#
#
# first = q.iloc[0]
# tags = parseMany(first, separator = ',')
# parseMany(first, 'Q', ',')
# print(get_questions(ans))

#data_storer('testhl.csv', 'testans.csv', 'testsch.csv')