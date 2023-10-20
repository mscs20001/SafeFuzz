# Based on https://github.com/eliben/pycparser/blob/master/examples/func_calls.py

from __future__ import print_function
import platform
import sys
import os
import copy
import argparse
import networkx as nx
import matplotlib.pyplot as plt

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#sys.path.extend(['.', '..'])

from pycparser import c_parser, c_ast, parse_file, c_generator
        
def get_funcnames(callGraphFile):
    funckey_list = []
    with open(callGraphFile, 'r') as f:
        lines = f.readlines()
    for line in lines[1:]: # skip first line
        tokens = line.split(',')
        for token in tokens:
            func = token.split()[0] # remove whitespaces
            if func not in funckey_list:
                funckey_list.append(func)
    return funckey_list

def read_metrices(metricsFile):
    metrics_dict = {}
    lines = []
    with open(metricsFile, 'r') as f:
        lines = f.readlines()
    for line in lines[1:]: # skip first line
        tokens = line.split(',')
        key = tokens[0].split(":")[1]
        value = []
        for token in tokens[1:]:
            value.append(float(token.split()[0]))
        metrics_dict[key] = value
    return metrics_dict

def calculate_weights(funckey_list, metrices_dict_list):
    funcweight_dict = {}
    for funckey in funckey_list:
        print(funckey)
        pass
    for metrices_dict in metrices_dict_list:
        # get max_value_list for normalization
        max_value_list = None
        for key, value_list in metrices_dict.items():
            if key in funckey_list:
                if max_value_list is None:
                    max_value_list = value_list
                else:
                    for index, value in enumerate(value_list):
                        if max_value_list[index] < value:
                            max_value_list[index] = value
        # now normalize all values between 0 and 1
        for key, value_list in metrices_dict.items():
            if key in funckey_list:
                metrices_dict[key] = [value / max_value for value, max_value in zip(value_list, max_value_list)]
        # add all elements of value_list from a given metric
        for key, value_list in metrices_dict.items():
            if key in funckey_list:
                metrices_dict[key] = sum(value_list)
        # get max_value for normalization again
        max_value = 0
        for key, value in metrices_dict.items():
            if key in funckey_list:
                if max_value < value:
                    max_value = value
        # now normalize value between 0 and 1
        for key, value in metrices_dict.items():
            if key in funckey_list:
                metrices_dict[key] = value / max_value
    # add all normalized metric values
    for metrices_dict in metrices_dict_list:
        for key, value in metrices_dict.items():
            if key in funckey_list:
                if key in funcweight_dict.keys():
                    funcweight_dict[key] += value
                else:
                    funcweight_dict[key] = value
    # get max_value for normalization of weights
    max_value = 0
    for key, value in funcweight_dict.items():
        if max_value < value:
            max_value = value
    # now normalize value between 0 and 1
    for key, value in funcweight_dict.items():
        funcweight_dict[key] = value / max_value
    return funcweight_dict

def generate_report(funcweight_dict, outFile):
    with open(outFile, 'w') as f:
        f.write('filename_function, weight\n')
        for key, value in funcweight_dict.items():
            f.write(key + ', ' + str(value) + '\n')

def parse_args(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', action="store", dest="callGraphFile", required=True)
    parser.add_argument('-c', action="store", dest="complexityFile", required=True)
    parser.add_argument('-f', action="store", dest="fluctuationFile", required=True)
    parser.add_argument('-o', action="store", dest="outFile", required=True)
    args = parser.parse_args(arg_list)
    outFile = args.outFile
    print(" - callGraphFile = " + args.callGraphFile)
    print(" - complexityFile = " + args.complexityFile)
    print(" - fluctuationFile = " + args.fluctuationFile)
    print(" - outFile = " + args.outFile)
    funckey_list = get_funcnames(args.callGraphFile)
    metrices_dict_list = []
    metrices_dict_list.append(read_metrices(args.complexityFile))
    metrices_dict_list.append(read_metrices(args.fluctuationFile))
    funcweight_dict = calculate_weights(funckey_list, metrices_dict_list)
    generate_report(funcweight_dict, args.outFile)

if __name__ == "__main__":  # pragma: no cover
    parse_args(sys.argv[1:])

