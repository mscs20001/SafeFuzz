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
        self.bodies = []
        self.generator = c_generator.CGenerator()
    def visit_FuncDef(self, node):
        self.bodies.append((node.decl.name, self.generator.visit(node)))
        
def get_func_lines_of_code(filename):
    count_dict = {}
    ast = parse_file(filename, use_cpp=True)
    v = FuncDefVisitor()
    v.visit(ast)
    for body in v.bodies:
        func, code = body
        #print(func)
        # remove empty lines
        lines = code.split('\n')
        newlines = []
        for line in lines:
            if len(line.split()) > 0:
                newlines.append(line)
        print(' - ' + func + ' = ' + str(len(newlines)))
        #print(filename.split('\\')[-1].split(".pp")[0])
        count_dict[filename.split('\\')[-1].split(".pp")[0] + ':' + func] = str(len(newlines))
        #print(code)
    return count_dict

def read_calls(srcDir):
    count_dict = {}
    for dirpath, dirnames, filenames in os.walk(srcDir):
        for filename in filenames:
            if filename.endswith(".c.pp"):
                print('Processing ' + filename)
                count_dict.update(get_func_lines_of_code(os.path.join(dirpath, filename)))
    return count_dict

def read_metrices(inFile, count_dict):
    complexity_dict = {}
    lines = []
    with open(inFile, 'r') as f:
        lines = f.readlines()
    for key, value in count_dict.items():
        filename = key.split(":")[0]
        func = key.split(":")[1].split(',')[0]
        lines_of_code = value
        cyclomatic_complexity = 0
        number_of_statements = 0
        for line in lines:
            if filename + ';' in line and ';' + func + ';' in line:
                if 'METRICS.W.Cyclomatic_complexity' in line:
                    cyclomatic_complexity = line.split(';')[11].split()[-1].split(">=0")[0]
                if 'METRICS.W.Number_of_statements' in line:
                    number_of_statements = line.split(';')[11].split()[-1].split(">=0")[0]
                else:
                    pass
        complexity_dict[key] = (lines_of_code, cyclomatic_complexity, number_of_statements)
    return complexity_dict
    
def generate_report(count_dict, outFile):
    with open(outFile, 'w') as f:
        f.write('filename:func, lines_of_code, cyclomatic_complexity, number_of_statements\n')
        for key, value in count_dict.items():
            lines_of_code, cyclomatic_complexity, number_of_statements = value
            f.write(key + ', ' + str(lines_of_code) + ', ' + str(cyclomatic_complexity) + ', ' + str(number_of_statements) + '\n')

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
    count_dict = read_calls(args.srcDir)
    complexity_dict = read_metrices(args.inFile, count_dict)
    generate_report(complexity_dict, args.outFile)

if __name__ == "__main__":  # pragma: no cover
    parse_args(sys.argv[1:])

