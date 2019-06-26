from datascience import *
import numpy as np
import pandas as pd
import os


def launch_Weighting(directory):
    print("WEIGHTING STARTING")
    iaaFiles = []
    print('weightdir',directory)
    for root, dir, files in os.walk(directory):
        for file in files:
            print(file)
            if file.endswith('.csv'):
                if 'Dep_S_IAA' in file:
                    print('gotaFile')
                    iaaFiles.append(directory+'/'+file)
    for f in iaaFiles:
        weighting_alg(f, './weight_key.csv', directory)

def weighting_alg(IAA_csv_file, credibility_weights_csv_file, directory = './'):

    IAA_csv = Table.read_table(IAA_csv_file)
    #IndexError when the csv is empty
    try:
        IAA_csv_schema_name = IAA_csv.column("schema_namespace").item(0)
    except IndexError:
        if IAA_csv.shape[0]<1:
            return
        else:
            print(len(IAA_csv))
            print(IAA_csv)
            raise Exception('EricIsAnIdiotError')

    print(IAA_csv_schema_name)
    if "uage" in IAA_csv_schema_name:
        IAA_csv_schema_type = "Language"
    elif "Reason" in IAA_csv_schema_name:
        IAA_csv_schema_type = "Reason"
    elif "Evidence" in IAA_csv_schema_name:
        IAA_csv_schema_type = "Evidence"
    elif "Probability" in IAA_csv_schema_name:
        IAA_csv_schema_type = "Probability"
    else:
        print("unweighted IAA", IAA_csv_file, "aborting")
        return
    print("WEIGHINGWITHSCHEMA", IAA_csv_schema_type, IAA_csv_file)
    IAA_csv = IAA_csv.with_column("Schema", IAA_csv_schema_type)
    IAA_csv = IAA_csv.relabeled("question_Number", "Question_Number")
    #because data sciecne module doesn't support a where to distinguish between strings and ints, we're casting
    #the ints to strings.
    IAA_csv.append_column("Answer_Number", [str(a) for a in IAA_csv.column('agreed_Answer')])
    IAA_csv = IAA_csv.where("Answer_Number", are.not_contained_in('ULM'))



    credibility_weights_csv = Table.read_table(credibility_weights_csv_file)
    credibility_weights_csv = credibility_weights_csv.to_df()


    q6_points = 0
    if IAA_csv_schema_type == "Evidence":
        if 6 in IAA_csv.column("Question_Number"):

            question_six_table = IAA_csv.where("Question_Number", are.equal_to(6))
            q6_holder_points = 0
            a = "Correlation"
            b = "Cause precedes effect"
            c = "The correlation appears across multiple independent contexts"
            d = "A plausible mechanism is proposed"
            e = "An experimental study was conducted (natural experiments OK)"
            f = "The bigger the cause, the bigger the effect (dose response curve)"
            g = "Experts are cited"
            h = "Other evidence"
            i = "No evidence given"

            for row in question_six_table.rows:
                if row.item("answer_content") == a or row.item("answer_content") == b or row.item("answer_content") == d:
                    q6_holder_points += row.item("agreement_score") * 50
                if row.item("answer_content") == c or row.item("answer_content") == e or row.item("answer_content") == f:
                    q6_holder_points += row.item("agreement_score") * 10
                if row.item("answer_content") == g or row.item("answer_content") == h:
                    q6_holder_points += row.item("agreement_score") * 1

            q6_points = weighted_q6(q6_holder_points)

    IAA_csv = IAA_csv.to_df()



    IAA_csv["Question_Number"]= IAA_csv["Question_Number"].apply(int)
    print(IAA_csv['Answer_Number'])
    for num in IAA_csv['Answer_Number']:
        print(type(num))
    IAA_csv["Answer_Number"]= IAA_csv["Answer_Number"].apply(convertToInt)
    new_csv = pd.merge(credibility_weights_csv, IAA_csv, on =["Schema", "Question_Number", "Answer_Number"], how = "inner")


    points = new_csv["Point_Recommendation"] * new_csv["agreement_score"]
    new_csv = new_csv.assign(Points = points)



    column_names = ["article_num", "article_sha256", "task_uuid", "Question_Number", "Answer_Number",
                    "highlighted_indices", "Point_Recommendation", "Points", "Label", "target_text"]
    for_visualization = new_csv[column_names]
    for_visualization = new_csv
    if IAA_csv_schema_type == "Evidence":
        for_visualization.loc['Quality of evidence', 'Points'] = q6_points
    for_visualization = for_visualization[for_visualization["Points"] != 0]
    length = len(for_visualization)
    # schema_name = []
    # for i in range(length):
    #     schema_name.append(IAA_csv_schema_type)
    for_visualization['schema'] = pd.Series(IAA_csv_schema_type for i in range(len(for_visualization['article_sha256'])+1))


    for_visualization.to_csv(directory+"/Point_recs_"+IAA_csv_schema_type+".csv", encoding = 'utf-8')
    # You can choose to specify the path of the exported csv file in the .to_csv() method.
def weighted_q6(num):
    if num >= 160:
        score = 0
    elif 150 <= num < 160:
        score = 0.5
    elif 100 <= num <150:
        score = 2
    elif 50 <= num <100:
        score = 3
    elif num < 50:
        score = 4
    else:
        score = 5
    return score


def convertToInt(string):
    try:
        out = int(string)
        return out
    except:
        return -1

#launch_Weighting('./demo1')