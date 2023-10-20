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

class FuncDefVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.funcs = []
        self.generator = c_generator.CGenerator()
    def visit_FuncDef(self, node):
        self.funcs.append(node.decl.name)
        
def get_funcnames(filename):
    funckey_list = []
    ast = parse_file(filename, use_cpp=True)
    v = FuncDefVisitor()
    v.visit(ast)
    for func in v.funcs:
        #print(func)
        funckey_list.append(filename.split('\\')[-1].split(".pp")[0] + ':' + func)
    return funckey_list

def read_files(srcDir):
    funckey_list = []
    for dirpath, dirnames, filenames in os.walk(srcDir):
        for filename in filenames:
            if filename.endswith(".c.pp"):
                print('Processing ' + filename)
                funckey_list += get_funcnames(os.path.join(dirpath, filename))
    return funckey_list

def read_metrices(inFile, funckey_list):
    violation_dict = {}
    lines = []
    with open(inFile, 'r') as f:
        lines = f.readlines()
    for key in funckey_list:
        filename = key.split(":")[0]
        func = key.split(":")[1].split(',')[0]
        violation = 0
        for line in lines:
            if filename + ';' in line and ';' + func + ';' in line:
                if 'METRICS.W.' not in line:
                    violation += 1
        violation_dict[key] = violation
    return violation_dict
    
def generate_report(violation_dict, outFile):
    with open(outFile, 'w') as f:
        f.write('filename_function, violation\n')
        for key, value in violation_dict.items():
            f.write(key + ', ' + str(value) + '\n')

def parse_args(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', action="store", dest="srcDir", required=True)
    parser.add_argument('-i', action="store", dest="inFile", required=True)
    parser.add_argument('-o', action="store", dest="outFile", required=True)
    args = parser.parse_args(arg_list)
    outFile = args.outFile
    print(" - srcDir = " + args.srcDir)
    print(" - inFile = " + args.inFile)
    print(" - outFile = " + args.outFile)
    funckey_list = read_files(args.srcDir)
    violation_dict = read_metrices(args.inFile, funckey_list)
    generate_report(violation_dict, args.outFile)

if __name__ == "__main__":  # pragma: no cover
    parse_args(sys.argv[1:])

