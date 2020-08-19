import argparse
import requests
import json
import os
import numpy as np
from time import sleep
from os import listdir
from os.path import isfile, isdir, join
from collections import Counter
import re
import shutil
import sys
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
rcParams['figure.figsize'] = 8, 6

def sort_article(a):
    i = a.split('_')[-1]
    if i == 'p1':
        return sys.maxsize - 3
    if i == 'multiclass':
        return sys.maxsize - 2
    if i == 'multilabel':
        return sys.maxsize - 1
    return int(i)

def generate_latex_table_binary(data):
   
    nb_columns = 6
    column_placement = '@{} l' + 'r' * (nb_columns - 1) + '@{}'
    latex_output  = "\\begin{tabular}{" + column_placement + " }\n"
    latex_output += "\\toprule\n"
    latex_output += " & \# cases & min \#features & max \#features & avg \#features & prevalence \\\\ \midrule" + "\n"
    average = 0.
    for i, key in enumerate(sorted(data.keys(), key=sort_article)):
        if key not in ['multiclass', 'multilabel']:
            latex_output += 'Article {} & {} & {} & {} & {:.2f} & {:.2f}\\\\\n'.format(key.split('_')[-1],
                    data[key]['dataset_size'], 
                    data[key]['min_feature'],
                    data[key]['max_feature'],
                    np.round_(data[key]['avg_feature'], 2),
                    np.round_(data[key]['prevalence'][key.split('_')[-1]]['violation_normalized'], 2)
                )

    latex_output += "\\bottomrule\n"
    latex_output += "\end{tabular}"

    return latex_output


def generate_latex_table_multiclass(data):
    data = data['multiclass']
    nb_columns = 6
    column_placement = '@{} l' + 'r' * (nb_columns - 1) + '@{}'
    latex_output  = "\\begin{tabular}{" + column_placement + " }\n"
    latex_output += "\\toprule\n"
    latex_output += " & \# cases & violation & no-violation & prevalence\\\\ \midrule" + "\n"
    average = 0.
    for key in sorted(data['prevalence'].keys(), key=sort_article):
        d = data['prevalence'][key]
        latex_output += 'Article {} & {} & {} ({:.3f}) & {} ({:.3f}) & {:.2f} \\\\\n'.format(key.split('_')[-1],
                    d['violation'] + d['no-violation'], 
                    d['violation'],
                    np.round_(d['violation_normalized'], 3),
                    d['no-violation'],
                    np.round_(d['no-violation_normalized'], 3),
                    np.round_((1.* d['violation']) / (d['violation'] + d['no-violation']), 2)
                )

    latex_output += "\\bottomrule\n"
    latex_output += "\end{tabular}"

    return latex_output


def generate_latex_table_multilabel(data):
    data = data['multilabel']
    nb_columns = 6
    column_placement = '@{} l' + 'r' * (nb_columns - 1) + '@{}'
    latex_output  = "\\begin{tabular}{" + column_placement + " }\n"
    latex_output += "\\toprule\n"
    latex_output += " & \# cases & violation & no-violation \\\\ \midrule" + "\n"
    average = 0.
    for key in sorted(data['prevalence'].keys(), key=sort_article):
        d = data['prevalence'][key]
        latex_output += 'Article {} & {} & {} ({:.3f}) & {} ({:.3f}) \\\\\n'.format(key.split('_')[-1],
                    d['violation'] + d['no-violation'], 
                    d['violation'],
                    np.round_(d['violation_normalized'], 3),
                    d['no-violation'],
                    np.round_(d['no-violation_normalized'], 3)
                )

    latex_output += "\\bottomrule\n"
    latex_output += "\end{tabular}"

    return latex_output


def plot_multilabel_label_count(data, path):
    count = map(len, data)
    counter = Counter(count)
    N = len(counter)
    ind = np.arange(N) + 1
    width = 0.80
    fig, ax = plt.subplots()    
    p1 = ax.bar(ind, counter.values(), width)
    ax.set_ylabel('Cases')
    #plt.title('Distribution of prevalence per article')
    ax.set_xticks(ind, range(1,len(counter)+1))
    for i, v in enumerate(counter.values()):
        ax.text(i + 1 - 0.15, v + 50, str(v))
    #plt.xticks(rotation=45)
    #plt.yticks(np.arange(0, 81, 10))
   # plt.legend((p1[0], p2[0]), ('Violation', 'No Violation'), loc='lower right')
    plt.savefig(join(path, 'multilabel_count_labels.png'), dpi=300)
    plt.clf()


def plot_multilabel_label_distribution(data, path):
    data_stat = data['multiclass']
    article_names = []
    violation_prop = []
    no_violation_prop = []
    for k in sorted(data_stat['prevalence'].keys(), key=sort_article):
        v = data_stat['prevalence'][k]
        article_names.append('Article {}'.format(k))
        violation_prop.append(v['class_normalized'])
        no_violation_prop.append(1. - violation_prop[-1])

    N = len(article_names)
    ind = np.arange(N)
    width = 0.80

    p1 = plt.bar(ind, violation_prop, width)
    p2 = plt.bar(ind, no_violation_prop, width, bottom=violation_prop)

    plt.ylabel('Ratio')
    #plt.title('Distribution of prevalence per article')
    plt.xticks(ind, article_names)
    plt.xticks(rotation=45)
    #plt.yticks(np.arange(0, 81, 10))
    plt.legend((p1[0], p2[0]), ('Violation', 'No Violation'), loc='lower right')
    plt.savefig(join(path, 'multiclass_distribution.png'), dpi=300)
    plt.clf()


def plot_multiclass_label_distribution(data, path):
    data_stat = data['multilabel']
    article_names = []
    violation_prop = []
    no_violation_prop = []
    for k in sorted(data_stat['prevalence'].keys(), key=sort_article):
        v = data_stat['prevalence'][k]
        article_names.append('Article {}'.format(k))
        violation_prop.append(v['class_normalized'])
        no_violation_prop.append(1. - violation_prop[-1])

    N = len(article_names)
    ind = np.arange(N)
    width = 0.80

    p1 = plt.bar(ind, violation_prop, width)
    p2 = plt.bar(ind, no_violation_prop, width, bottom=violation_prop)

    plt.ylabel('Ratio')
    #plt.title('Distribution of prevalence per article')
    plt.xticks(ind, article_names)
    plt.xticks(rotation=45)
    #plt.yticks(np.arange(0, 81, 10))
    plt.legend((p1[0], p2[0]), ('Violation', 'No Violation'), loc='lower right')
    plt.savefig(join(path, 'multilabel_distribution.png'), dpi=300)
    plt.clf()


def plot_multiclass_count_distribution(data, path):
    data_stat = data['multiclass']
    article_names = []
    violation_prop = []
    no_violation_prop = []
    for k in sorted(data_stat['prevalence'].keys(), key=sort_article):
        v = data_stat['prevalence'][k]
        article_names.append('Article {}'.format(k))
        violation_prop.append(v['violation'])
        no_violation_prop.append(v['no-violation'])

    N = len(article_names)
    ind = np.arange(N)
    width = 0.8 

    p1 = plt.bar(ind, violation_prop, width)
    p2 = plt.bar(ind, no_violation_prop, width, bottom=violation_prop)

    plt.ylabel('Number of cases')
    #plt.title('Distribution of prevalence per article')
    plt.xticks(ind, article_names)
    plt.xticks(rotation=45)
    #plt.yticks(np.arange(0, 81, 10))
    plt.legend((p1[0], p2[0]), ('Violation', 'No Violation'), loc='upper left')
    plt.savefig(join(path, 'multiclass_count.png'), dpi=300)
    plt.clf()


def plot_multilabel_count_distribution(data, path):
    data_stat = data['multilabel']
    article_names = []
    violation_prop = []
    no_violation_prop = []
    for k in sorted(data_stat['prevalence'].keys(), key=sort_article):
        v = data_stat['prevalence'][k]
        article_names.append('Article {}'.format(k))
        violation_prop.append(v['violation'])
        no_violation_prop.append(v['no-violation'])

    N = len(article_names)
    ind = np.arange(N)
    width = 0.8

    p1 = plt.bar(ind, violation_prop, width)
    p2 = plt.bar(ind, no_violation_prop, width, bottom=violation_prop)

    plt.ylabel('Number of cases')
    #plt.title('Distribution of prevalence per article')
    plt.xticks(ind, article_names)
    plt.xticks(rotation=45)
    #plt.yticks(np.arange(0, 81, 10))
    plt.legend((p1[0], p2[0]), ('Violation', 'No Violation'), loc='upper left')
    plt.savefig(join(path, 'multilabel_count.png'), dpi=300)
    plt.clf()



def main(args):
    input_folder = os.path.join(args.build, args.processed_folder)
    output_folder = os.path.join(args.build, args.processed_folder)

    # Get the list of cases s.t. we have a BoW and TF-IDF representation
    files = [join(input_folder, f, 'statistics_datasets.json') for f in listdir(input_folder) if isdir(join(input_folder, f))]

    data = {}
    for file in files:
        with open(file, 'r') as f:
            data.update(json.load(f))

    multilabel_outcomes = []
    with open(join(input_folder, 'multilabel', 'outcomes.txt'), 'r') as f:
        lines = f.readlines()
        for l in lines:
            multilabel_outcomes.append(l.split()[1:])

    with open(join(output_folder, 'summary_binary.tex'), 'w') as f:
        f.write(generate_latex_table_binary(data))

    with open(join(output_folder, 'summary_multiclass.tex'), 'w') as f:
        f.write(generate_latex_table_multiclass(data))

    with open(join(output_folder, 'summary_multilabel.tex'), 'w') as f:
        f.write(generate_latex_table_multilabel(data))

    plot_multilabel_label_distribution(data, input_folder)
    plot_multilabel_count_distribution(data, input_folder)
    plot_multiclass_label_distribution(data, input_folder)
    plot_multiclass_count_distribution(data, input_folder)

    plot_multilabel_label_count(multilabel_outcomes, input_folder)


def parse_args(parser):
    args = parser.parse_args()

    # Check path
    return args

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate some statistics from the dataset files')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--processed_folder', type=str, default="datasets_documents")
    parser.add_argument('-f', action='store_true')
    args = parse_args(parser)

    main(args)
 