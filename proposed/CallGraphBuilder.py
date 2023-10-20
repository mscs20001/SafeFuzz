import os
import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from subprocess import check_output
        
addresses2funcnames_dict = {}

def read_calls(traceDir, exeDir):
    global addresses2funcnames_dict
    exeFiles = []
    traceFiles = []
    trace2exeFile_dict = {}
    for dirpath, dirnames, filenames in os.walk(exeDir):
        for filename in filenames:
            if filename.endswith('test.exe'):
                exeFiles.append(os.path.join(dirpath, filename))
    #print(exeFiles)
    for dirpath, dirnames, filenames in os.walk(traceDir):
        for filename in filenames:
            if filename.endswith('_trace.out'):
                traceFiles.append(os.path.join(dirpath, filename))
    for traceFile in traceFiles:
        testgroup_name = os.path.basename(traceFile).split('_trace.out')[0]
        for exeFile in exeFiles:
            if testgroup_name in exeFile:
                trace2exeFile_dict[traceFile] = exeFile
                break
    #print(trace2exeFile_dict)
    # ENTER: makes a new node and EXIT: terminates it.
    call_dict = {}
    for traceFile, exeFile in trace2exeFile_dict.items():
        addresses2funcnames_dict.clear()
        lines = []
        currentFunc = None
        callerFunc = None
        calleeFunc = None
        HistoryList = []
        with open(traceFile, "r") as f:
            lines = f.readlines()
        for index, line in enumerate(lines):
            tokens = line.split(',')
            if len(tokens) > 0:
                func_address = tokens[0].split()[0]
                caller_address = tokens[1].split()[0]
                if func_address in addresses2funcnames_dict.keys():
                    func_name = addresses2funcnames_dict[func_address]
                else:
                    try:
                        out = check_output(["addr2line.exe", "-f", "-e" + exeFile, func_address], universal_newlines=True)
                    except:
                        print("Unexpected error:", sys.exc_info())
                    func_name = out.split('\n')[0].split()[0]
                    addresses2funcnames_dict[func_address] = func_name
                    if caller_address in addresses2funcnames_dict.keys():
                        caller_name = addresses2funcnames_dict[caller_address]
                    else:
                        try:
                            out = check_output(["addr2line.exe", "-f", "-e" + exeFile, caller_address], universal_newlines=True)
                        except:
                            print("Unexpected error:", sys.exc_info())
                        caller_name = out.split('\n')[0].split()[0]
                        addresses2funcnames_dict[caller_address] = caller_name
                        if caller_name not in call_dict.keys():
                            call_dict[caller_name] = []
                        if func_name not in call_dict.keys():
                            call_dict[func_name] = []
                        call_dict[caller_name].append(func_name)
    return call_dict

def build_graph(call_dict, outFile):
    G = nx.DiGraph()
    G.add_nodes_from(list(call_dict.keys()))
    for key, value_list in call_dict.items():
        for value in value_list:
            G.add_edge(key, value)
    nx.draw(G, with_labels = True, pos = nx.spring_layout(G, scale=3))
    #plt.show()
    plt.savefig(outFile + '.png')

def generate_report(call_dict, outFile):
    with open(outFile, 'w') as f:
        f.write('caller_function, callee_function\n')
        for key, value_list in call_dict.items():
            line = key
            for value in value_list:
                line += ', ' + value
            line += '\n'
            f.write(line)

def parse_args(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', action="store", dest="traceDir", required=True)
    parser.add_argument('-e', action="store", dest="exeDir", required=True)
    parser.add_argument('-o', action="store", dest="outFile", required=True)
    args = parser.parse_args(arg_list)
    outFile = args.outFile
    print(" - traceDir = " + args.traceDir)
    print(" - exeDir = " + args.exeDir)
    print(" - outFile = " + args.outFile)
    call_dict = read_calls(args.traceDir, args.exeDir)
    build_graph(call_dict, args.outFile)
    generate_report(call_dict, args.outFile)

if __name__ == "__main__":  # pragma: no cover
    parse_args(sys.argv[1:])


