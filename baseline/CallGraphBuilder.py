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

from pycparser import c_ast, parse_file

class FuncCallVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.callees = []  
    def visit_FuncCall(self, node):
        if node.name.name not in self.callees:
            self.callees.append(node.name.name)
        # nested funccall
        if node.args:
            self.visit(node.args)

class FuncDefVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.calls = []
    def visit_FuncDef(self, node):
        fcv = FuncCallVisitor()
        fcv.visit(node)
        self.calls.append((node.decl.name, fcv.callees))
        #print('%s at %s' % (node.decl.name, node.decl.coord))
        #print(fcv.callees) # calles has all funccall in this funcdef
        
def get_func_calls(filename):
    ast = parse_file(filename, use_cpp=True)
    v = FuncDefVisitor()
    v.visit(ast)
    return v

def read_calls(srcDir):
    call_dict = {}
    for dirpath, dirnames, filenames in os.walk(srcDir):
        for filename in filenames:
            if filename.endswith(".c.pp"):
                #print("=======================================")
                print('Processing ' + filename)
                node = get_func_calls(os.path.join(dirpath, filename))
                for call in node.calls:
                    key, value = call
                    call_dict[key] = value
    # remove any values with are not actually a key i.e. not a function themselves
    # this is to remove function pointers since they don't work in static mode
    for key, value_list in call_dict.items():
        temp_value_list = copy.deepcopy(value_list)
        for value in temp_value_list:
            if value not in call_dict.keys():
                call_dict[key].remove(value)
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
    parser.add_argument('-s', action="store", dest="srcDir", required=True)
    parser.add_argument('-o', action="store", dest="outFile", required=True)
    args = parser.parse_args(arg_list)
    outFile = args.outFile
    print(" - srcDir = " + args.srcDir)
    print(" - outFile = " + args.outFile)
    call_dict = read_calls(args.srcDir)
    build_graph(call_dict, args.outFile)
    generate_report(call_dict, args.outFile)

if __name__ == "__main__":  # pragma: no cover
    parse_args(sys.argv[1:])

