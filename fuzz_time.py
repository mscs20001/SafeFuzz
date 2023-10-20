import sys
import os
import datetime
import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, date2num


lines = []
with open('baseline_fuzzer/08122022_1.txt', 'r') as f:
#with open('baseline_fuzzer/29072022_1.txt', 'r') as f:
    lines = f.readlines()

baseline_start = 0
baseline_end = []
baseline_unique = [0]
for index, line in enumerate(lines):
    if 'started at ' in line:
        if baseline_start != 0:
            break
        date_time_str = ' '.join(line.split('started at ')[-1].split())
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        baseline_start = date_time_obj
        baseline_end.append(baseline_start - baseline_start)
    if 'completed at ' in line:
        date_time_str = line.split('completed at ')[1].split(',')[0]
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        baseline_end.append(date_time_obj - baseline_start)
        baseline_unique.append(int(lines[index - 1].split('COVERAGE=')[1].split()[0]))
    

lines = []
with open('proposed_fuzzer/29072022_1.txt', 'r') as f:
    lines = f.readlines()

proposed_start = 0
proposed_end = []
proposed_unique = [0]
for index, line in enumerate(lines):
    if 'started at ' in line:
        if proposed_start != 0:
            break
        date_time_str = ' '.join(line.split('started at ')[-1].split())
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        proposed_start = date_time_obj
        proposed_end.append(proposed_start - proposed_start)
    if 'completed at ' in line:
        date_time_str = line.split('completed at ')[1].split(',')[0]
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        proposed_end.append(date_time_obj - proposed_start)
        proposed_unique.append(int(lines[index - 1].split('COVERAGE=')[1].split()[0]))

#print(baseline_end)
#print(proposed_end)
#print(baseline_unique)
#print(proposed_unique)
baseline_time = []
for end in baseline_end:
    baseline_time.append(end.total_seconds())
proposed_time = []
for end in proposed_end:
    proposed_time.append(end.total_seconds())

xtend = list(range(len(baseline_unique), len(baseline_time)))
last = baseline_unique[-1]
for i in xtend:
    baseline_unique.append(last)

xtend = list(range(len(proposed_unique), len(proposed_time)))
last = proposed_unique[-1]
for i in xtend:
    proposed_unique.append(last)
print(len(baseline_time))
print(len(baseline_unique))
print(baseline_time)
print(baseline_unique)
print(len(proposed_time))
print(len(proposed_unique))
plt.plot(baseline_time, baseline_unique, marker='o', markevery = [len(baseline_unique) - 1], label = 'VulFuzz', color = 'red', linestyle='dashed') # plotting t, a separately 
plt.plot(proposed_time, proposed_unique, marker='o', markevery = [len(proposed_unique) - 1], label = 'SafeFuzz', color = 'black') # plotting t, b separately 
plt.xlabel("Time (sec)")
plt.ylabel("Coverage")
plt.legend()
plt.rcParams.update({'font.size': 18})
plt.show()

