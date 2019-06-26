import argparse

from IAA import calc_agreement_directory
from Dependency import *
from Weighting import *
from pointAssignment import *
from Separator import *


def calculate_scores_master(directory, tua_file = None, iaa_dir = None, scoring_dir = None, repCSV = None):
    print("IAA PROPER")
    iaa_dir = calc_agreement_directory(directory, hardCodedTypes=True, repCSV=repCSV, outDirectory=iaa_dir)
    print('iaaaa', iaa_dir)
    print("DEPENDENCY")
    scoring_dir = eval_dependency(directory, iaa_dir, out_dir=scoring_dir)
    print("WEIGHTING")
    launch_Weighting(scoring_dir)
    print("SORTING POINTS")
    pointSort(scoring_dir, tua_file)
    print("----------------SPLITTING-----------------------------------")
    splitcsv(scoring_dir)

def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input-dir',
        help='Directory containing DataHuntHighlights DataHuntAnswers, '
             'and Schema .csv files.')
    parser.add_argument(
        '-t', '--tua-file',
        help='Filename to use for file with TUAs for taskruns in input-dir.')
    parser.add_argument(
        '-o', '--output-dir',
        help='Pathname to use for IAA output directory.')
    parser.add_argument(
        '-s', '--scoring-dir',
        help='Pathname to use for output files for scoring of articles.')
    parser.add_argument(
        '-r', '--rep-file',
        help='Filename to use for User Reputation scores file.')
    return parser.parse_args()

if __name__ == '__main__':
    args = load_args()
    input_dir = './data/Setup_Testing_4-18-19'
    tua_file = './mt/allTUAS.csv'
    output_dir = None
    scoring_dir  = None
    rep_file = './UserRepScores.csv'
    if args.input_dir:
        input_dir = args.input_dir
    if args.tua_file:
        tua_file = args.tua_file
    if args.output_dir:
        output_dir = args.output_dir
    if args.scoring_dir:
        scoring_dir = args.scoring_dir
    if args.rep_file:
        rep_file = args.rep_file
    calculate_scores_master(input_dir, tua_file=tua_file, iaa_dir=output_dir, scoring_dir=scoring_dir, repCSV=rep_file)

#calculate_scores_master("./langdeptest")