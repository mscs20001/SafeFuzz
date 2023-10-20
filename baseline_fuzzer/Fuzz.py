import platform
import sys
import os
import re
import tqdm
import copy
import time
import math
import shutil
import filecmp
import argparse
import datetime
import functools
import subprocess
import multiprocessing
from subprocess import check_output
import networkx as nx
from random import seed
from random import shuffle
from random import randint
from difflib import SequenceMatcher
from itertools import repeat
from threading import Thread
from collections import OrderedDict

from pycparser import c_parser, c_ast, parse_file, c_generator

addresses2funcnames_dict = {}
covResultFile = None
covResultBackupFile = None
mcdc_coverage = 0
mcdc_coverage_total = 0
testId_list = None
allInputTuple_list = None

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

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        

def read_inputs(inputFile):
    input_tuple_list = []
    lines = []
    with open(inputFile, 'r') as f:
        lines = f.readlines()
    for line in lines[1:]:
        tokens = line.split(',')
        if len(tokens) > 0:
            input_list = []
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
    os.remove('out/trace_' + str(runId) + '.out')	
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
    global covResultFile
    global covResultBackupFile
    subprocess.run([shutil.which('covclear'), '-f', covFile, '--no-banner'])
    subprocess.run([shutil.which('covfn'), '-f', covFile, '--decision', '-c', '--no-banner', '--output', covResultFile])
    shutil.copy(covResultFile, covResultBackupFile)

def coverage_increased(covFile, i):
    global covResultFile
    global covResultBackupFile
    global mcdc_coverage
    global mcdc_coverage_total
    result = False
    try:
        subprocess.run([shutil.which('covmerge'), '-f', covFile, covFile + '_' + str(i), '--no-banner'])
    except:
        return True, mcdc_coverage, mcdc_coverage_total
    try:
        subprocess.run([shutil.which('covfn'), '-f', covFile, '--decision', '-c', '--no-banner', '--output', covResultFile])
        if filecmp.cmp(covResultFile, covResultBackupFile):
            result = False
        else:
            result = True
        shutil.copy(covResultFile, covResultBackupFile)
        if result == True:
            lines = []
            subprocess.run([shutil.which('covfn'), '-f', covFile, '-c', '--no-banner', '--output', covResultFile + '_mcdc'])
            with open(covResultFile + '_mcdc', 'r') as f:
                lines = f.readlines()
            for line in lines[-3:]:
                tokens = line.split(',')
                if len(tokens) > 0:
                    if "Total" in tokens[0]:
                        mcdc_coverage = int(tokens[-3])
                        mcdc_coverage_total = int(tokens[-2])
        #    shutil.copy(covFile, covFile + str(i))
        #    shutil.copy(covResultFile, covResultFile + str(i))
        return result, mcdc_coverage, mcdc_coverage_total
    except:
        return True, mcdc_coverage, mcdc_coverage_total

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
            if value_list[-1] in callGraph and nx.has_path(callGraph, value_list[-1], highFunc5):
                return True
    else:
        # in case of CRASH or HANG execution
        for highFunc in highFunc_list:
            if list(call_dict.keys())[-1] in callGraph and nx.has_path(callGraph, list(call_dict.keys())[-1], highFunc):
                return True
    return False

def init_mutate_pool(_testId_list, _allInputTuple_list):
    global testId_list
    global allInputTuple_list
    testId_list = _testId_list
    allInputTuple_list = _allInputTuple_list

def self_mutate(seedInput, magicNumber_list, priority, epoch_count):
    global testId_list
    global allInputTuple_list
    #print(seedInput)
    mutatedInput_list = []
    magic_mutation_count = 0
    if priority != 'BASE':
        if seedInput[0] not in testId_list:
            testId_list.append(seedInput[0])
            magic_mutation_count += ((len(seedInput) - 2) * len(magicNumber_list) * 3) + ((len(seedInput) - 2) * 5)
    magic_mutation_count = 0	
    if priority == 'BASE':
        priority_bias = 0
    elif priority == 'HIGH':
        priority_bias = 10
    elif priority == 'LOW':
        priority_bias = 5
    elif priority == 'UNIQUE':
        priority_bias = 2
    else:
        priority_bias = 1
    bit_mutation_count = 10 * priority_bias
    single_mutation_count = 10 * priority_bias
    crossover_mutation_count = 10 * priority_bias
    # Data Type-Based Mutation:
    # All inputs are treated as unsigned integers.
    tries = priority_bias * 100
    total_magic_mutation_count = 0
    total_single_mutation_count = 0
    total_bit_mutation_count = 0
    miss_magic_mutation_count = 0
    miss_single_mutation_count = 0
    miss_bit_mutation_count = 0
    if priority == 'BASE':
        mutatedInput = copy.deepcopy(seedInput)
        allInputTuple_list.append(tuple())
        if tuple(mutatedInput) not in set(allInputTuple_list):
            mutatedInput_list.append(mutatedInput)
            allInputTuple_list.append(tuple(mutatedInput))
        else:
            print('Repeated input')
            print(mutatedInput)
            print(allInputTuple_list)
            print(len(allInputTuple_list))
            input()
    while (single_mutation_count + magic_mutation_count + bit_mutation_count) > 0 and tries > 0:
        #print(len(mutatedInput_list))
        #print('elapsed time bit_mutation_count (sec): ' + str(total_bit_mutation_count) + ' @ misses = ' + str(miss_bit_mutation_count))
        #print(bit_mutation_count)
        #print('elapsed time single_mutation_count (sec): ' + str(total_single_mutation_count) + ' @ misses = ' + str(miss_single_mutation_count))
        #print(single_mutation_count)
        #print('elapsed time magic_mutation_count (sec): ' + str(total_magic_mutation_count) + ' @ misses = ' + str(miss_magic_mutation_count))
        #print(magic_mutation_count)
        tries -= 1
        start_single_mutation_count = time.time()
        while single_mutation_count > 0 and tries > 0:
            for index, value in enumerate(seedInput[1:]):
                single_miss_single_mutation_count = 0
                while single_mutation_count > 0 and tries > 0:
                    #print('elapsed time single_mutation_count (sec): ' + str(total_single_mutation_count) + ' @ misses = ' + str(miss_single_mutation_count))
                    #print(single_mutation_count)
                    tries -= 1
                    mutatedInput = copy.deepcopy(seedInput)
                    ##operator = randint(0, 4)
                    operator = randint(0, 3)
                    operand = randint(0, 2 ** max(8, mutatedInput[index + 1].bit_length() - 1))
                    if operator == 0:
                        mutatedInput[index + 1] -= operand
                    elif operator == 1:
                        mutatedInput[index + 1] += operand
                    elif operator == 2:
                        mutatedInput[index + 1] *= operand
                    elif operator == 3:
                        if operand != 0:
                            mutatedInput[index + 1] = int(mutatedInput[index + 1] / operand)
                    else:
                        mutatedInput[index + 1] = randint(0, 2 ** 64)
                    if tuple(mutatedInput) not in set(allInputTuple_list):
                        mutatedInput_list.append(mutatedInput)
                        allInputTuple_list.append(tuple(mutatedInput))
                        single_mutation_count -= 1
                        break
                    else:
                        miss_single_mutation_count += 1
                        single_miss_single_mutation_count += 1
                        if single_miss_single_mutation_count > (max(8, seedInput[index + 1].bit_length() - 1) * 2):
                            break
        single_mutation_count = 0
        if bit_mutation_count > 0:
            tries = priority_bias * 100
        end_single_mutation_count = time.time()
        total_single_mutation_count += end_single_mutation_count - start_single_mutation_count
        start_bit_mutation_count = time.time()
        while bit_mutation_count > 0 and tries > 0:
            for index, value in enumerate(seedInput[1:]):
                if bit_mutation_count == 0:
                    break
                else:
                    single_bit_mutation_count = max(8, seedInput[index + 1].bit_length() - 1) * 2
                    single_miss_bit_mutation_count = 0
                    while True and tries > 0:
                        tries -= 1
                        mutatedInput = copy.deepcopy(seedInput)
                        # logic for following check is that we should allow atleast all bit flips in given input
                        if single_miss_bit_mutation_count > max(8, mutatedInput[index + 1].bit_length() - 1) * 2:
                            # force all bit flips now
                            for bit_index in range(max(8, mutatedInput[index + 1].bit_length() - 1)):
                                mutatedInput = copy.deepcopy(seedInput)
                                mutatedInput[index + 1] ^= 1 << bit_index
                                if tuple(mutatedInput) not in set(allInputTuple_list):
                                    mutatedInput_list.append(mutatedInput)
                                    allInputTuple_list.append(tuple(mutatedInput))
                                    single_bit_mutation_count -= 1
                                    if single_bit_mutation_count == 0:
                                        break
                                else:
                                    miss_bit_mutation_count += 1
                            if single_bit_mutation_count == 0:
                                break
                            bits_to_mutate = randint(0, max(8, mutatedInput[index + 1].bit_length() - 1))
                        else:
                            bits_to_mutate = 1
                        if single_bit_mutation_count == 0:
                            break
                        for _ in range(bits_to_mutate):
                            mutatedInput[index + 1] ^= 1 << randint(0, max(8, mutatedInput[index + 1].bit_length() - 1))
                        if tuple(mutatedInput) not in set(allInputTuple_list):
                            mutatedInput_list.append(mutatedInput)
                            allInputTuple_list.append(tuple(mutatedInput))
                            single_bit_mutation_count -= 1
                            bit_mutation_count -= 1
                            if bit_mutation_count == 0 or single_bit_mutation_count == 0:
                                break
                        else:
                            miss_bit_mutation_count += 1
                            single_miss_bit_mutation_count += 1
            bit_mutation_count = 0
        if magic_mutation_count > 0:
            tries = priority_bias * 100
        end_bit_mutation_count = time.time()
        total_bit_mutation_count += end_bit_mutation_count - start_bit_mutation_count
        start_magic_mutation_count = time.time()
        for index, value in enumerate(seedInput[1:]):
            for i in magicNumber_list:
                mutatedInput = copy.deepcopy(seedInput)
                mutatedInput[index + 1] = i
                if tuple(mutatedInput) not in set(allInputTuple_list):
                    mutatedInput_list.append(mutatedInput)
                    allInputTuple_list.append(tuple(mutatedInput))
                else:
                    miss_magic_mutation_count += 1
        for index, value in enumerate(seedInput[1:]):
            for i in magicNumber_list:
                mutatedInput = copy.deepcopy(seedInput)
                mutatedInput[index + 1] = i - 1
                if tuple(mutatedInput) not in set(allInputTuple_list):
                    mutatedInput_list.append(mutatedInput)
                    allInputTuple_list.append(tuple(mutatedInput))
                else:
                    miss_magic_mutation_count += 1
        for index, value in enumerate(seedInput[1:]):
            for i in magicNumber_list:
                mutatedInput = copy.deepcopy(seedInput)
                mutatedInput[index + 1] = i + 1
                if tuple(mutatedInput) not in set(allInputTuple_list):
                    mutatedInput_list.append(mutatedInput)
                    allInputTuple_list.append(tuple(mutatedInput))
                else:
                    miss_magic_mutation_count += 1
        for index, value in enumerate(seedInput[1:]):
            for i in [(2 ** 8) - 1, (2 ** 16) - 1, (2 ** 32) - 1, (2 ** 64) - 1]:
                mutatedInput = copy.deepcopy(seedInput)
                mutatedInput[index + 1] = i
                if tuple(mutatedInput) not in set(allInputTuple_list):
                    mutatedInput_list.append(mutatedInput)
                    allInputTuple_list.append(tuple(mutatedInput))
                else:
                    miss_magic_mutation_count += 1
        magic_mutation_count = 0
        end_magic_mutation_count = time.time()
        total_magic_mutation_count += end_magic_mutation_count - start_magic_mutation_count
    return mutatedInput_list

def cross_mutate(seedInput_list, magicNumber_list, priority, epoch_count):
    global allInputTuple_list
    #print(seedInput_list)
    #print("seedInput_list = " + str(len(seedInput_list)))
    #print(seedInput_list[0])
    mutatedInput_list = []
    if priority == 'BASE':
        priority_bias = 0
    elif priority == 'HIGH':
        priority_bias = 10
    elif priority == 'LOW':
        priority_bias = 5
    elif priority == 'UNIQUE':
        priority_bias = 2
    else:
        priority_bias = 1
    crossover_mutation_count = 10 * priority_bias
   
    # Crossover-Based Mutation:
    tries = (crossover_mutation_count) * 100
    total_crossover_mutation_count = 0
    miss_crossover_mutation_count = 0
    while (crossover_mutation_count) > 0 and tries > 0:
        tries -= 1
        for value_index, value_list in enumerate(seedInput_list):
            start_crossover_mutation_count = time.time()
            if crossover_mutation_count > 0:
                for index, value in enumerate(value_list[2:]):
                    if crossover_mutation_count == 0:
                        break
                    else:
                        mutatedInput = copy.deepcopy(value_list)
                        cross_index = randint(0, len(allInputTuple_list) - 1)
                        if len(list(allInputTuple_list[cross_index])) == len(mutatedInput) and len(list(allInputTuple_list[cross_index])) > 1:
                            cross_part_index = randint(1, len(list(allInputTuple_list[cross_index])) - 1)
                            mutatedInput[index + 1] = list(allInputTuple_list[cross_index])[cross_part_index]
                            if tuple(mutatedInput) not in set(allInputTuple_list):
                                mutatedInput_list.append(mutatedInput)
                                allInputTuple_list.append(tuple([0] + mutatedInput[1:]))
                                crossover_mutation_count -= 1
                            else:
                                miss_crossover_mutation_count += 1
            end_crossover_mutation_count = time.time()
            total_crossover_mutation_count += end_crossover_mutation_count - start_crossover_mutation_count
    #print('elapsed time crossover_mutation_count (sec): ' + str(total_crossover_mutation_count) + ' @ misses = ' + str(miss_crossover_mutation_count))
    return mutatedInput_list

def run_single_input(exeFile, covFile, input_list):
    #covResultBackupFile = covFile.replace('.cov', '.csv.bak')
    mutatedInput_index = input_list[0]
    del input_list[0] # remove mutatedInput_index from input
    singleCovFile = covFile + '_' + str(mutatedInput_index)
    if os.path.exists(singleCovFile):
        os.remove(singleCovFile)
    while True:
        shutil.copy(covFile, singleCovFile)
        if os.path.exists(singleCovFile):
            break
        else:
            print(singleCovFile + ' was not copied! Try again')
    result = None
    cmd_timeout_sec = 5
    cmd_params = str(mutatedInput_index) + '\n'
    for one_input in input_list:
        cmd_params += str(one_input) + '\n'
    #print(cmd_params)
    p2_env = os.environ.copy()
    p2_env["COVFILE"] = singleCovFile
    p2 = subprocess.Popen([exeFile], env=p2_env, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        out, err = p2.communicate(input = bytes(cmd_params, "utf-8"), timeout = cmd_timeout_sec)
        #print(out.decode("utf-8"))
        if 0 == p2.returncode:
            result = 'OK'
        else:
            result = 'CRASH'
    except subprocess.TimeoutExpired:
        p2.kill()
        result = 'HANG'
    return result
        
def run_epoch(exeFile, covFile, crashFile, hangFile, callGraph, testId_list, magicNumber_list, highFunc_list, highInput_list, lowInput_list, priority, result_dict, allInputTuple_list, allInput_list, allUniqueInput_list, allUniqueValidInput_list):
    global mcdc_coverage
    global mcdc_coverage_total
    #print('run_epoch')
    #print(highInput_list)
    #print(lowInput_list)
    epoch_count = 0
    while True:
        epoch_count += 1
        nextHighInput_list = []
        nextLowInput_list = []
        discardInput_list = []
        seedInput_list = []
        if priority == 'BASE':
            seedInput_list = copy.deepcopy(highInput_list)
            seedInput_list.extend(lowInput_list)
        elif priority == 'HIGH':
            seedInput_list = copy.deepcopy(highInput_list)
        elif priority == 'LOW':
            seedInput_list = copy.deepcopy(lowInput_list)
        elif priority == 'UNIQUE':
            seedInput_list = copy.deepcopy(allUniqueInput_list)
        else:
            seedInput_list = copy.deepcopy(allInput_list)
        epochCovFile = covFile + '_epoch_' + str(epoch_count)
        epochCovResultFile = covFile.replace('.cov', '.csv') + '_epoch_' + str(epoch_count)
        covResultBackupFile = covFile.replace('.cov', '.csv.bak')
        #start_seedInput_list = time.time()
        #shuffle(seedInput_list)
        #end_seedInput_list = time.time()
        ##print('elapsed time seedInput_list (sec): ' + str(end_seedInput_list - start_seedInput_list))
        for seedInput_index, seedInput in enumerate(seedInput_list):
            start = time.time()
            start_mutate = time.time()
            if priority == 'BASE':
                if seedInput_index == 0:
                    input_to_mutate_list = seedInput_list
                else:
                    break
            else:
                if seedInput_index == 0:
                    input_to_mutate_list = seedInput_list
                else:
                    break
            mutatedInput_list = []
            for input_to_mutate in tqdm.tqdm(input_to_mutate_list):
                mutatedInput_list.extend(self_mutate(input_to_mutate, magicNumber_list, priority, epoch_count))
            mutatedInput_list.extend(cross_mutate(input_to_mutate_list, magicNumber_list, priority, epoch_count))
            if len(mutatedInput_list) == 0:
                continue
            end_mutate = time.time()
            print('elapsed time mutate (sec): ' + str(end_mutate - start_mutate) + ' to generate inputs = ' + str(len(mutatedInput_list)))
            # Initial call to print 0% progress
            print('epoch_count[' + str(epoch_count) + '] at priority = ' + priority + ', seedInput = ' + str(len(seedInput_list)) + ', mutatedInput = ' + str(len(mutatedInput_list)))
            ProgressLine = 'INPUTS=' + str(len(allInput_list))
            ProgressLine += ' UNIQUE=' + str(len(allUniqueInput_list))
            ProgressLine += ' VALID=' + str(sum(value == 'OK' for value in result_dict.values()))
            ProgressLine += ' CRASH=' + str(sum(value == 'CRASH' for value in result_dict.values()))
            ProgressLine += ' HANGS=' + str(sum(value == 'HANG' for value in result_dict.values()))
            ProgressLine += ' COVERAGE=' + str(mcdc_coverage) + ' out of ' + str(mcdc_coverage_total)
            printProgressBar(0, len(mutatedInput_list), prefix = 'Progress:', suffix = 'Complete ' + ProgressLine, length = 100)
            total_subprocess = 0
            total_coverage_increased = 0

            if len(mutatedInput_list) > 0:
                mutatedInput_list_part_length = 1
                for mutatedInput_list_part_index, mutatedInput_list_part in enumerate(list(chunks(mutatedInput_list, mutatedInput_list_part_length))):

                    start_subprocess = time.time()
                    results = []
                    with multiprocessing.Pool() as pool:
                        for mutatedInput_index in range(len(mutatedInput_list_part)):
                            mutatedInput_list_part[mutatedInput_index].insert(0, mutatedInput_index)
                        #for result in tqdm.tqdm(pool.map(functools.partial(run_single_input, exeFile, covFile), mutatedInput_list_part), total=len(mutatedInput_list_part)):
                        for result in pool.map(functools.partial(run_single_input, exeFile, covFile), mutatedInput_list_part):
                            results.append(result)
                        for mutatedInput_index in range(len(mutatedInput_list_part)):
                            del mutatedInput_list_part[mutatedInput_index][0]

                    end_subprocess = time.time()
                    total_subprocess += end_subprocess - start_subprocess

                    epochCoverageIncreased = True
                    if os.path.exists(epochCovFile):
                        os.remove(epochCovFile)
                    shutil.copy(covFile, epochCovFile)
                    cmd_params = [shutil.which('covmerge'), '-f', epochCovFile, '--no-banner']
                    for mutatedInput_index in range(0, len(mutatedInput_list_part)):
                        cmd_params.append(covFile + '_' + str(mutatedInput_index))
                    try:
                        subprocess.run(cmd_params)
                        subprocess.run([shutil.which('covfn'), '-f', epochCovFile, '--decision', '-c', '--no-banner', '--output', epochCovResultFile])
                        if filecmp.cmp(epochCovResultFile, covResultBackupFile):
                            # coverage did not change
                            epochCoverageIncreased = False
                        else:
                            subprocess.run([shutil.which('covfn'), '-f', epochCovFile, '-c', '--no-banner', '--output', epochCovResultFile + '_mcdc'])
                            lines = []
                            with open(epochCovResultFile + '_mcdc', 'r') as f:
                                lines = f.readlines()
                            for line in lines[-3:]:
                                tokens = line.split(',')
                                if len(tokens) > 0:
                                    if "Total" in tokens[0]:
                                        epochCoverage = int(tokens[-3])
                            checkepochCoverageIncreased = True
                    except:
                        epochCoverageIncreased = True
                        checkepochCoverageIncreased = False
                    os.remove(epochCovFile)

                    for mutatedInput_index, input_list in enumerate(mutatedInput_list_part):
                        #time.sleep(0.001) # seconds
                        allInput_list.append(input_list)
                        if epochCoverageIncreased == True and (checkepochCoverageIncreased == False or epochCoverage > mcdc_coverage):
                            coverageIncreased = False
                            start_coverage_increased = time.time()
                            result_coverage, mcdc_coverage, mcdc_coverage_total = coverage_increased(covFile, mutatedInput_index)
                            if result_coverage == True:
                                coverageIncreased = True
                            end_coverage_increased = time.time()
                            total_coverage_increased += end_coverage_increased - start_coverage_increased
                            #start_python = time.time()
                            # assign mutated input to high, low or discard
                            if coverageIncreased is True:
                                #print(results[mutatedInput_index])
                                if results[mutatedInput_index] == 'OK':
                                    allUniqueValidInput_list.append(input_list)
                                elif results[mutatedInput_index] == 'CRASH':
                                    with open(crashFile, 'a') as f:
                                        line = str(input_list[0])
                                        for input_list_part in input_list[1:]:
                                            line += ', ' + str(input_list_part)
                                        f.write(line + '\n')
                                elif results[mutatedInput_index] == 'HANG':
                                    with open(hangFile, 'a') as f:
                                        line = str(input_list[0])
                                        for input_list_part in input_list[1:]:
                                            line += ', ' + str(input_list_part)
                                        f.write(line + '\n')
                                else:
                                    pass
                                result_dict[tuple(input_list)] = results[mutatedInput_index]
                                allUniqueInput_list.append(input_list)
                                call_dict = read_calls(exeFile, mutatedInput_index)
                                if IsHighInput(call_dict, callGraph, highFunc_list) == True:
                                    nextHighInput_list.append(input_list)
                                else:
                                    nextLowInput_list.append(input_list)
                        if os.path.exists(covFile + '_' + str(mutatedInput_index)):
                            os.remove(covFile + '_' + str(mutatedInput_index))
                        #end_python = time.time()
                        #start_printProgressBar = time.time()
                        # Update Progress Bar
                        ProgressLine = 'INPUTS=' + str(len(allInput_list))
                        ProgressLine += ' UNIQUE=' + str(len(allUniqueInput_list))
                        ProgressLine += ' VALID=' + str(sum(value == 'OK' for value in result_dict.values()))
                        ProgressLine += ' CRASH=' + str(sum(value == 'CRASH' for value in result_dict.values()))
                        ProgressLine += ' HANGS=' + str(sum(value == 'HANG' for value in result_dict.values()))
                        ProgressLine += ' COVERAGE=' + str(mcdc_coverage) + ' out of ' + str(mcdc_coverage_total)
                        printProgressBar((mutatedInput_list_part_index * mutatedInput_list_part_length) + mutatedInput_index + 1, len(mutatedInput_list), prefix = 'Progress:', suffix = 'Complete ' + ProgressLine, length = 100)
                        #end_printProgressBar = time.time()
                        #print('')
                        #print('elapsed time subprocess (sec): ' + str(end_subprocess - start_subprocess))
                        #print('elapsed time coverage (sec): ' + str(end_coverage_increased - start_coverage_increased))
                        #print('elapsed time python (sec): ' + str(end_python - start_python))
                        #print('elapsed time printProgressBar (sec): ' + str(end_printProgressBar - start_printProgressBar))
                        #print('')
                        #print(nextHighInput_list)
                        #print(nextLowInput_list)
            end = time.time()
            print('completed at ' + str(datetime.datetime.now()) + ', elapsed time (sec): ' + str(end - start))
            print('total_subprocess = ' + str(total_subprocess))
            #print('total_coverage_increased = ' + str(total_coverage_increased))
        if priority == 'HIGH':
            lowInput_list.extend(nextLowInput_list)
            highInput_list.clear()
            highInput_list.extend(nextHighInput_list)
            if len(highInput_list) == 0:
                break
        elif priority == 'LOW':
            highInput_list.extend(nextHighInput_list)
            lowInput_list.clear()
            lowInput_list.extend(nextLowInput_list)
            if len(lowInput_list) == 0:
                break
        else:
            highInput_list.extend(nextHighInput_list)
            lowInput_list.extend(nextLowInput_list)
            if priority == 'BASE':
                break
            else:
                if epoch_count == 10 or len(highInput_list) + len(lowInput_list) > 0:
                    break

def fuzz_tests(exeFile, covFile, crashFile, hangFile, callGraph, magicNumber_list, highFunc_list, highInput_list, lowInput_list, result_dict, allInput_list, allUniqueInput_list, allUniqueValidInput_list):
    global testId_list
    global allInputTuple_list
    try:
        run_epoch(exeFile, covFile, crashFile, hangFile, callGraph, testId_list, magicNumber_list, highFunc_list, highInput_list, lowInput_list, 'BASE', result_dict, allInputTuple_list, allInput_list, allUniqueInput_list, allUniqueValidInput_list)
        while True:
            while True:
                run_epoch(exeFile, covFile, crashFile, hangFile, callGraph, testId_list, magicNumber_list, highFunc_list, highInput_list, lowInput_list, 'HIGH', result_dict, allInputTuple_list, allInput_list, allUniqueInput_list, allUniqueValidInput_list)
                run_epoch(exeFile, covFile, crashFile, hangFile, callGraph, testId_list, magicNumber_list, highFunc_list, highInput_list, lowInput_list, 'LOW', result_dict, allInputTuple_list, allInput_list, allUniqueInput_list, allUniqueValidInput_list)
                if len(highInput_list) + len(lowInput_list) == 0:
                    break
            break
    except KeyboardInterrupt:
        pass

def run_tests(exeFile, covFile, crashFile, hangFile, callGraphFile, funcweight_dict, highInput_list, lowInput_list, allInput_list):
    global covResultFile
    global covResultBackupFile
    global testId_list
    global allInputTuple_list
    allInputTuple_list = []
    allUniqueInput_list = []
    allUniqueValidInput_list = []
    highFunc_list = []
    lowFunc_list = []
    testId_list = []
    magicNumber_list = []
    covResultFile = covFile.replace('.cov', '.csv')
    covResultBackupFile = covFile.replace('.cov', '.csv.bak')
    # divide funcweight_dict into high and low weight lists based on their mean
    meanWeight = sum(funcweight_dict.values()) / len(funcweight_dict)
    for key, value in funcweight_dict.items():
        if value > meanWeight:
            highFunc_list.append(key)
        else:
            lowFunc_list.append(key)
    callGraph = build_graph(callGraphFile)
    coverage_reset(covFile)
    result_dict = {}
    print('')
    print('started at ' + str(datetime.datetime.now()))
    p = Thread(target = fuzz_tests, args = [exeFile, covFile, crashFile, hangFile, callGraph, magicNumber_list, highFunc_list, highInput_list, lowInput_list, result_dict, allInput_list, allUniqueInput_list, allUniqueValidInput_list])
    p.daemon = True
    p.start()
    p.join(timeout = 30000) # seconds
    print('')
    print('Total Inputs: ' + str(len(allInput_list)))
    print('Unique Total Inputs: ' + str(len(allUniqueInput_list)))
    print('Unique Valid Inputs: ' + str(sum(value == 'OK' for value in result_dict.values())))
    print('Unique Crashes: ' + str(sum(value == 'CRASH' for value in result_dict.values())))
    print('Unique Hangs: ' + str(sum(value == 'HANG' for value in result_dict.values())))
    return result_dict

def generate_report(result_dict, outFile, category):
    with open(outFile, 'w') as f:
        f.write('testId, {params, ...}\n')
        if result_dict is not None:
            for  key, value in result_dict.items():
                if value == category:
                    line = str(key[0])
                    for key_part in key[1:]:
                        line += ', ' + str(key_part)
                    f.write(line + '\n')

def parse_args(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', action="store", dest="exeFile", required=True)
    parser.add_argument('-c', action="store", dest="covFile", required=True)
    parser.add_argument('-w', action="store", dest="weightFile", required=True)
    parser.add_argument('-g', action="store", dest="callGraphFile", required=True)
    parser.add_argument('--high', action="store", dest="highFile", required=True)
    parser.add_argument('--low', action="store", dest="lowFile", required=True)
    parser.add_argument('--all', action="store", dest="allFile", required=True)
    parser.add_argument('--valid', action="store", dest="validFile", required=True)
    parser.add_argument('--crash', action="store", dest="crashFile", required=True)
    parser.add_argument('--hang', action="store", dest="hangFile", required=True)
    args = parser.parse_args(arg_list)
    print(" - exeFile = " + args.exeFile)
    print(" - covFile = " + args.covFile)
    print(" - weightFile = " + args.weightFile)
    print(" - callGraphFile = " + args.callGraphFile)
    print(" - highFile = " + args.highFile)
    print(" - lowFile = " + args.lowFile)
    print(" - allFile = " + args.allFile)
    print(" - validFile = " + args.validFile)
    print(" - crashFile = " + args.crashFile)
    print(" - hangFile = " + args.hangFile)
    highInput_list = read_inputs(args.highFile)
    lowInput_list = read_inputs(args.lowFile)
    allInput_list = read_inputs(args.allFile)
    funcweight_dict = read_weights(args.weightFile)
    generate_report(None, args.crashFile, 'CRASH')
    generate_report(None, args.hangFile, 'HANG')
    result_dict = run_tests(args.exeFile, args.covFile, args.crashFile, args.hangFile, args.callGraphFile, funcweight_dict, highInput_list, lowInput_list, allInput_list)
    generate_report(result_dict, args.validFile, 'OK')


if __name__ == "__main__":  # pragma: no cover
    parse_args(sys.argv[1:])
