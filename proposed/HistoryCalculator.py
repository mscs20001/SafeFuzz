# Based on https://github.com/eliben/pycparser/blob/master/examples/func_calls.py

from __future__ import print_function
from difflib import SequenceMatcher
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
        
def get_func_code(filename):
    code_dict = {}
    ast = parse_file(filename, use_cpp=True)
    v = FuncDefVisitor()
    v.visit(ast)
    for body in v.bodies:
        func, code = body
        #print(func)
        #print(filename.split('\\')[-1].split(".pp")[0])
        code_dict[filename.split('\\')[-1].split(".pp")[0] + ':' + func] = code
        #print(code)
    return code_dict

def read_calls(srcDir):
    code_dict = {}
    for dirpath, dirnames, filenames in os.walk(srcDir):
        for filename in filenames:
            if filename.endswith(".c.pp"):
                print('Processing ' + os.path.join(dirpath, filename))
                code_dict.update(get_func_code(os.path.join(dirpath, filename)))
    return code_dict

def calc_history_weights(code_dict, codeLast_dict, codeLastLast_dict):
    weight_dict = {}
    for key, value in code_dict.items():
        weighted = False
        weight = 0
        # The range of the similarity ratio lies between 0 and 1 
        # where having a value of 1 indicates exact match or maximum similarity.
        # A value of 0 indicates totally unique objects.
        for keyLast, valueLast in codeLast_dict.items():
            if key == keyLast:
                sm = SequenceMatcher(None, value, valueLast)
                #print (sm.ratio())
                weight = 1 - sm.ratio() # This should be inverse for weightage
                weighted = True
                if weight > 0:
                    break
                else:
                    # in case of exact match (weight == 0) make sure there were no changes between last->lastLast
                    for keyLastLast, valueLastLast in codeLastLast_dict.items():
                        if key == keyLastLast:
                            sm = SequenceMatcher(None, value, valueLastLast)
                            #print (sm.ratio())
                            weight = 0.5 * (1 - sm.ratio()) # This should be inverse for weightage reduced by 50%
                            weighted = True
                            break
        # if case no match was found then it is a new function and should be assigned high weight
        if weighted == False:
            weight = 1
        weight_dict[key] = weight
    return weight_dict

def generate_report(weight_dict, outFile):
    with open(outFile, 'w') as f:
        f.write('filename:func, history_weight\n')
        for key, value in weight_dict.items():
            f.write(key + ', ' + str(value) + '\n')

def parse_args(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', action="store", dest="srcDir", required=True)
    parser.add_argument('--last', action="store", dest="lastDir", required=True)
    parser.add_argument('--lastlast', action="store", dest="lastLastDir", required=True)
    parser.add_argument('-o', action="store", dest="outFile", required=True)
    args = parser.parse_args(arg_list)
    outFile = args.outFile
    print(" - srcDir = " + args.srcDir)
    print(" - lastDir = " + args.lastDir)
    print(" - lastLastDir = " + args.lastLastDir)
    print(" - outFile = " + args.outFile)
    code_dict = read_calls(args.srcDir)
    codeLast_dict = read_calls(args.lastDir)
    codeLastLast_dict = read_calls(args.lastLastDir)
    weight_dict = calc_history_weights(code_dict, codeLast_dict, codeLastLast_dict)
    generate_report(weight_dict, args.outFile)

if __name__ == "__main__":  # pragma: no cover
    parse_args(sys.argv[1:])

