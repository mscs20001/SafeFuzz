import sys
import os
import matplotlib.pyplot as plt
import numpy as np

lines = []
with open('baseline\metrics\FunctionWeight.txt', 'r') as f:
    lines = f.readlines()

baseline_funcweight_dict = {}
for line in lines[1:]:
    tokens = line.split(',')
    if len(tokens) > 1:
        baseline_funcweight_dict[tokens[0]] = float(tokens[1].split()[0])

lines = []
with open('proposed\metrics\FunctionWeight.txt', 'r') as f:
    lines = f.readlines()

proposed_funcweight_dict = {}
for line in lines[1:]:
    tokens = line.split(',')
    if len(tokens) > 1:
        proposed_funcweight_dict[tokens[0]] = float(tokens[1].split()[0])

common_keys = set(baseline_funcweight_dict).intersection(set(proposed_funcweight_dict))
baseline_values = []
for common_key in common_keys:
    baseline_values.append(baseline_funcweight_dict[common_key])
proposed_values = []
for common_key in common_keys:
    proposed_values.append(proposed_funcweight_dict[common_key])

max_diff = 0
max_diff_key = 0
for common_key in common_keys:
    print(common_key)
    print(baseline_funcweight_dict[common_key])
    print(proposed_funcweight_dict[common_key])
    print("----------------------------------")
    if (abs(proposed_funcweight_dict[common_key] - baseline_funcweight_dict[common_key])) > max_diff:
        max_diff = abs(proposed_funcweight_dict[common_key] - baseline_funcweight_dict[common_key])
        max_diff_key = common_key

print(max_diff_key)
print(max_diff)

xpoints = np.array(list(range(1, len(common_keys) + 1)))

plt.bar(xpoints - 0.2, baseline_values, 0.4, label = 'VulFuzz', color = 'lightgray', hatch = "//")
plt.bar(xpoints + 0.2, proposed_values, 0.4, label = 'SVO Fuzzer', color = 'darkgray')

plt.xticks(xpoints, [])
plt.rcParams.update({'font.size': 16})
plt.xlabel("Functions", fontweight='bold', fontsize = 16)
plt.ylabel("Weights", fontweight='bold', fontsize = 16)
plt.legend()
plt.show()