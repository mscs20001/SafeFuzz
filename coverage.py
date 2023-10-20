import sys
import os
import datetime
import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, date2num


lines = []
with open('baseline_fuzzer/final_nomagic_all_6000sec.txt', 'r') as f:
    lines = f.readlines()

baseline_start = 0
baseline_end = []
baseline_unique = [0]
for index, line in enumerate(lines):
    if 'started at ' in line:
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
with open('proposed_fuzzer/final_nomagic_all_6000sec.txt', 'r') as f:
    lines = f.readlines()

proposed_start = 0
proposed_end = []
proposed_unique = [0]
for index, line in enumerate(lines):
    if 'started at ' in line:
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

plt.plot(baseline_time, baseline_unique, label = 'VulFuzz', color = 'black', linestyle='dashed') # plotting t, a separately 
plt.plot(proposed_time, proposed_unique, label = 'SVO Fuzzer', color = 'black') # plotting t, b separately 
plt.xlabel("Time (sec)", fontweight='bold')
plt.ylabel("Covered Conditions", fontweight='bold')
plt.legend()
plt.rcParams.update({'font.size': 22})
plt.show()

