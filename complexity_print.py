import sys
import os
import matplotlib.pyplot as plt
import numpy as np

lines = []
with open('baseline\metrics\Complexity.txt', 'r') as f:
    lines = f.readlines()

values = []
for index, line in enumerate(lines[1:]):
    tokens = line.split(',')
    if len(tokens) > 1:
        values.append(str(index) + ' & ' + ' & '.join(tokens[1:]))

for value in values:
    print(value.replace('\n', ' \\\\ \hline'))