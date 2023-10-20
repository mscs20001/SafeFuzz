import sys
import os
import datetime
import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, date2num


lines = []
with open('baseline_fuzzer/multiple_10000sec.txt', 'r') as f:
    lines = f.readlines()

baseline_start = None
baseline_end = []
baseline_unique = [0]
baseline_end_all = []
baseline_unique_all = []
for index, line in enumerate(lines):
    if 'started at ' in line:
        date_time_str = ' '.join(line.split('started at ')[-1].split())
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        if baseline_start is not None:
            baseline_end_all.append(baseline_end)
            baseline_unique_all.append(baseline_unique)
            baseline_end = []
            baseline_unique = [0]
        baseline_start = date_time_obj
        baseline_end.append(baseline_start - baseline_start)
    if 'completed at ' in line:
        date_time_str = line.split('completed at ')[1].split(',')[0]
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        baseline_end.append(date_time_obj - baseline_start)
        baseline_unique.append(int(lines[index - 1].split('COVERAGE=')[1].split()[0]))
baseline_end_all.append(baseline_end)
baseline_unique_all.append(baseline_unique)
    

lines = []
with open('proposed_fuzzer/multiple_10000sec.txt', 'r') as f:
    lines = f.readlines()

proposed_start = None
proposed_end = []
proposed_unique = [0]
proposed_end_all = []
proposed_unique_all = []
for index, line in enumerate(lines):
    if 'started at ' in line:
        date_time_str = ' '.join(line.split('started at ')[-1].split())
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        if proposed_start is not None:
            proposed_end_all.append(proposed_end)
            proposed_unique_all.append(proposed_unique)
            proposed_end = []
            proposed_unique = [0]
        proposed_start = date_time_obj
        proposed_end.append(proposed_start - proposed_start)
    if 'completed at ' in line:
        date_time_str = line.split('completed at ')[1].split(',')[0]
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        proposed_end.append(date_time_obj - proposed_start)
        proposed_unique.append(int(lines[index - 1].split('COVERAGE=')[1].split()[0]))
proposed_end_all.append(proposed_end)
proposed_unique_all.append(proposed_unique)

#print(baseline_end)
#print(proposed_end)
#print(baseline_unique)
#print(proposed_unique)

baseline_time_all = []
for baseline_end in baseline_end_all:
    baseline_time = []
    for end in baseline_end:
        baseline_time.append(end.total_seconds())
    baseline_time_all.append(baseline_time)

proposed_time_all = []
for proposed_end in proposed_end_all:
    proposed_time = []
    for end in proposed_end:
        proposed_time.append(end.total_seconds())
    proposed_time_all.append(proposed_time)

for i in range(0, len(baseline_unique_all)):
    print('baseline coverage = ' + str(baseline_unique_all[i][-1]))
    print('proposed coverage = ' + str(proposed_unique_all[i][-1]))
    plt.plot(baseline_time_all[i], baseline_unique_all[i], label = 'VulFuzz', color = 'black', linestyle='dashed') # plotting t, a separately 
    plt.plot(proposed_time_all[i], proposed_unique_all[i], label = 'SVO Fuzzer', color = 'black') # plotting t, b separately 
    plt.xlabel("Time (sec)", fontweight='bold')
    plt.ylabel("Covered Conditions " + str(i), fontweight='bold')
    plt.legend()
    plt.rcParams.update({'font.size': 22})
    plt.show()

