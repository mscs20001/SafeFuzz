import platform
import sys
import os
import copy
import time
import shutil
import filecmp
import argparse
import subprocess
from subprocess import check_output
import networkx as nx
from difflib import SequenceMatcher
from collections import OrderedDict

testId_dict = {
    "AES_128_TestCase_0" : 0,
    "CancelJob_TestSuite" : 1,
    "CertificateParse_TestSuite" : 2,
    "CertificateVerify_TestSuite" : 3,
    "KeyCopy_TestSuite" : 4,
    "KeyDerive_TestSuite" : 5,
    "KeyElementCopy_TestSuite" : 6,
    "KeyElementGet_TestSuite" : 7,
    "KeyElementIdsGet_TestSuite" : 8,
    "KeyElementSet_TestSuite" : 9,
    "KeyExchangeCalcPubVal_TestSuite" : 10,
    "KeyExchangeCalcSecret_TestSuite" : 11,
    "KeyGenerate_TestSuite" : 12,
    "KeySetValid_TestSuite" : 13,
    "RandomSeed_TestSuite" : 14,
    "RNG_TestSuite" : 15,
}

addresses2funcnames_dict = {}

#https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def read_inputs(inputDir):
    input_tuple_list = []
    for dirpath, dirnames, filenames in os.walk(inputDir):
        for filename in filenames:
            lines = []
            with open(os.path.join(dirpath, filename), 'r') as f:
                lines = f.readlines()
            for line in lines:
                tokens = line.split(',')
                if len(tokens) > 0:
                    input_list = [testId_dict[filename.replace('.txt', '')]]
                    for token in tokens:
                        input_list.append(int(token.split()[0]))
                    input_tuple_list.append(input_list)
    return input_tuple_list

def read_weights(weightFile):
    funcweight_dict = {}
    lines = []
    with open(weightFile, 'r') as f:
        lines = f.readlines()
    for line in lines[1:]: # skip first line
        tokens = line.split(',')
        key = tokens[0]
        value = float(tokens[1].split()[0])
        funcweight_dict[key] = value
    return funcweight_dict

def read_calls(exeFile, runId = 0):
    global addresses2funcnames_dict
    # ENTER: makes a new node and EXIT: terminates it.
    # in case of exception, there is missing last EXIT
    call_dict = OrderedDict()
    lines = []
    currentFunc = None
    callerFunc = None
    calleeFunc = None
    HistoryList = []
    with open('out/trace_' + str(runId) + '.out', "r") as f:
        lines = f.readlines()
    Enter = 0
    Exit = 0
    try:
        for index, line in enumerate(lines):
            if line.startswith('ENTER:'):
                #print(line)
                #print(line.split(':')[1].split()[0])
                Enter += 1
                address = line.split(':')[1].split()[0]
                if address in addresses2funcnames_dict.keys():
                    funcname = addresses2funcnames_dict[address]
                else:
                    try:
                        out = check_output(["addr2line.exe", "-f", "-e" + exeFile, line.split(':')[1].split()[0]], universal_newlines=True)
                    except:
                        print("Unexpected error:", sys.exc_info())
                    #print(out)
                    #print(out.split('\n')[0].split()[0])
                    funcname = out.split('\n')[0].split()[0]
                    addresses2funcnames_dict[address] = funcname
                HistoryList.append(funcname)
                if currentFunc is not None:
                    key = currentFunc
                    value = HistoryList[-1]
                    call_dict[key].append(value)
                    call_dict[value] = [] # empty list of functions called by this func
                    currentFunc = value
                else:
                    key = HistoryList[-1]
                    call_dict[key] = [] # empty list of functions called by this func
                    currentFunc = key
            elif line.startswith('EXIT:'):
                Exit += 1
                del HistoryList[-1]
                if currentFunc is not None:
                    if len(HistoryList) > 0:
                        currentFunc = HistoryList[-1]
                else:
                    print('Error')
                    print(index)
            else:
                currentFunc = None
                callerFunc = None
                calleeFunc = None
    except:
        print("Number of Enter and Exits don't match")
        print("Enter = " + str(Enter))
        print("Exit = " + str(Exit))
    return call_dict

def build_graph(callGraphFile):
    lines = []
    with open(callGraphFile, 'r') as f:
        lines = f.readlines()
    callGraph = nx.DiGraph()
    for line in lines[1:]:
        tokens = line.split(',')
        if len(tokens) > 0:
            callGraph.add_nodes_from([tokens[0].split()[0]])
            if len(tokens) > 1:
                callGraph.add_edge(tokens[0].split()[0], tokens[1].split()[0])
    return callGraph

def coverage_reset(covFile):
    covResultFile = covFile.replace('.cov', '.csv')
    covResultBackupFile = covFile.replace('.cov', '.csv.bak')
    subprocess.run([shutil.which('covclear'), '-f', covFile, '--no-banner'])
    subprocess.run([shutil.which('covfn'), '-f', covFile, '-c', '--no-banner', '--output', covResultFile])
    shutil.copy(covResultFile, covResultBackupFile)

def coverage_increased(covFile, i):
    covResultFile = covFile.replace('.cov', '.csv')
    covResultBackupFile = covFile.replace('.cov', '.csv.bak')
    result = True
    subprocess.run([shutil.which('covfn'), '-f', covFile, '-c', '--no-banner', '--output', covResultFile])
    if filecmp.cmp(covResultFile, covResultBackupFile):
        result = False
    if result == True:
        shutil.copy2(covResultFile, covResultBackupFile)
    #shutil.copy2(covResultFile, covResultFile + str(i))
    return result

def IsHighInput(call_dict, callGraph, highFunc_list):
    for  key, value_list in call_dict.items():
        if key in highFunc_list:
            return True
        else:
            for value in value_list:
                if value in highFunc_list:
                    return True
    # check if last called function has a path to highFunc_list
    value_list = call_dict[list(call_dict.keys())[-1]]
    if len(value_list) > 0:
        # in case of OK execution
        for highFunc in highFunc_list:
            if value_list[-1] in callGraph and nx.has_path(callGraph, value_list[-1], highFunc):
                return True
    else:
        # in case of CRASH or HANG execution
        for highFunc in highFunc_list:
            if list(call_dict.keys())[-1] in callGraph and nx.has_path(callGraph, list(call_dict.keys())[-1], highFunc):
                return True
    return False

def run_tests(exeFile, covFile, callGraphFile, funcweight_dict, input_tuple_list):
    highInput_list = []
    lowInput_list = []
    allInput_list = []
    highFunc_list = []
    lowFunc_list = []
    # divide funcweight_dict into high and low weight lists, list is divided into two equal parts
    funcweight_dict = dict(sorted(funcweight_dict.items(), key=lambda x:x[1]))
    middle_index = len(funcweight_dict) / 2
    for index, (key, value) in enumerate(funcweight_dict.items()):
        if index > middle_index:
            highFunc_list.append(key)
        else:
            lowFunc_list.append(key)
    callGraph = build_graph(callGraphFile)
    print('')
    coverage_reset(covFile)
    # Initial call to print 0% progress
    printProgressBar(0, len(input_tuple_list), prefix = 'Progress:', suffix = 'Complete', length = 100)
    result_dict = {}
    for i, input_list in enumerate(input_tuple_list):
        time.sleep(0.1)
        cmd_timeout_sec = 5
        cmd_params = str(0) + '\n'
        for one_input in input_list:
            cmd_params += str(one_input) + '\n'
        #print(cmd_params)
        p2 = subprocess.Popen([exeFile], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        try:
            out, err = p2.communicate(input = bytes(cmd_params, "utf-8"), timeout = cmd_timeout_sec)
            p2.wait(cmd_timeout_sec)
            #print(out.decode("utf-8"))
            if coverage_increased(covFile, i) == True:
                if 0 == p2.returncode:
                    result_dict[tuple(input_list)] = 'OK'
                    call_dict = read_calls(exeFile)
                    if IsHighInput(call_dict, callGraph, highFunc_list) == True:
                        highInput_list.append(input_list)
                    else:
                        lowInput_list.append(input_list)
                else:
                    print(input_list)
                    result_dict[tuple(input_list)] = 'CRASH'
            else:
                allInput_list.append(input_list)
        except subprocess.TimeoutExpired:
            p2.kill()
            if coverage_increased(covFile, i) == True:
                print(input_list)
                result_dict[tuple(input_list)] = 'HANG'
        # Update Progress Bar
        printProgressBar(i + 1, len(input_tuple_list), prefix = 'Progress:', suffix = 'Complete', length = 100)
    print('')
    print('Total Inputs: ' + str(len(input_tuple_list)))
    covResultBackupFile = covFile.replace('.cov', '.csv.bak')
    shutil.copy2(covResultBackupFile, covResultBackupFile + '_base')
    return result_dict, highInput_list, lowInput_list, allInput_list

def validate_results(result_dict):
    print('Unique Total Inputs: ' + str(len(result_dict.values())))
    print('Unique Valid Inputs: ' + str(sum(value == 'OK' for value in result_dict.values())))
    print('Unique Crashes: ' + str(sum(value == 'CRASH' for value in result_dict.values())))
    print('Unique Hangs: ' + str(sum(value == 'HANG' for value in result_dict.values())))
    if sum(value == 'CRASH' for value in result_dict.values()) + sum(value == 'HANG' for value in result_dict.values()) > 0:
        print('FATAL ERROR: Please provide valid inputs only!')
        exit(-1)
    else:
        return True

def generate_report(seed_list, outFile):
    with open(outFile, 'w') as f:
        f.write('testId, {params, ...}\n')
        for value_list in seed_list:
            value_line = str(value_list[0])
            for value in value_list[1:]:
                value_line += ', ' + str(value)
            f.write(value_line + '\n')

def parse_args(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', action="store", dest="inputDir", required=True)
    parser.add_argument('-e', action="store", dest="exeFile", required=True)
    parser.add_argument('-c', action="store", dest="covFile", required=True)
    parser.add_argument('-w', action="store", dest="weightFile", required=True)
    parser.add_argument('-g', action="store", dest="callGraphFile", required=True)
    parser.add_argument('--high', action="store", dest="highFile", required=True)
    parser.add_argument('--low', action="store", dest="lowFile", required=True)
    parser.add_argument('--all', action="store", dest="allFile", required=True)
    args = parser.parse_args(arg_list)
    print(" - inputDir = " + args.inputDir)
    print(" - exeFile = " + args.exeFile)
    print(" - covFile = " + args.covFile)
    print(" - weightFile = " + args.weightFile)
    print(" - callGraphFile = " + args.callGraphFile)
    print(" - highFile = " + args.highFile)
    print(" - lowFile = " + args.lowFile)
    print(" - allFile = " + args.allFile)
    input_tuple_list = read_inputs(args.inputDir)
    funcweight_dict = read_weights(args.weightFile)
    result_dict, highInput_list, lowInput_list, allInput_list = run_tests(args.exeFile, args.covFile, args.callGraphFile, funcweight_dict, input_tuple_list)
    if validate_results(result_dict):
        generate_report(highInput_list, args.highFile)
        generate_report(lowInput_list, args.lowFile)
        generate_report(allInput_list, args.allFile)

if __name__ == "__main__":  # pragma: no cover
    parse_args(sys.argv[1:])
