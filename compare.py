
import sys
import os

baseline_Total_Inputs = 0
baseline_Unique_Total_Inputs = 0
baseline_Unique_Valid_Inputs = 0
baseline_Unique_Crashes = 0
baseline_Unique_Hangs = 0

with open('baseline_fuzzer\log2 - Copy.txt', 'r') as f:
    lines = f.readlines()
for line in lines:
    if 'Total Inputs:' in line:
        baseline_Total_Inputs += int(line.split()[-1])
    if 'Unique Total Inputs:' in line:
        baseline_Unique_Total_Inputs += int(line.split()[-1])
    if 'Unique Valid Inputs:' in line:
        baseline_Unique_Valid_Inputs += int(line.split()[-1])
    if 'Unique Crashes:' in line:
        baseline_Unique_Crashes += int(line.split()[-1])
    if 'Unique Hangs:' in line:
        baseline_Unique_Hangs += int(line.split()[-1])
print('baseline:')
print('baseline_Total_Inputs = ' + str(baseline_Total_Inputs))
print('baseline_Unique_Total_Inputs = ' + str(baseline_Unique_Total_Inputs))
print('baseline_Unique_Valid_Inputs = ' + str(baseline_Unique_Valid_Inputs))
print('baseline_Unique_Crashes = ' + str(baseline_Unique_Crashes))
print('baseline_Unique_Hangs = ' + str(baseline_Unique_Hangs))


proposed_Total_Inputs = 0
proposed_Unique_Total_Inputs = 0
proposed_Unique_Valid_Inputs = 0
proposed_Unique_Crashes = 0
proposed_Unique_Hangs = 0

with open('proposed_fuzzer\log2 - Copy.txt', 'r') as f:
    lines = f.readlines()
for line in lines:
    if 'Total Inputs:' in line:
        proposed_Total_Inputs += int(line.split()[-1])
    if 'Unique Total Inputs:' in line:
        proposed_Unique_Total_Inputs += int(line.split()[-1])
    if 'Unique Valid Inputs:' in line:
        proposed_Unique_Valid_Inputs += int(line.split()[-1])
    if 'Unique Crashes:' in line:
        proposed_Unique_Crashes += int(line.split()[-1])
    if 'Unique Hangs:' in line:
        proposed_Unique_Hangs += int(line.split()[-1])
print('proposed:')
print('proposed_Total_Inputs = ' + str(proposed_Total_Inputs))
print('proposed_Unique_Total_Inputs = ' + str(proposed_Unique_Total_Inputs))
print('proposed_Unique_Valid_Inputs = ' + str(proposed_Unique_Valid_Inputs))
print('proposed_Unique_Crashes = ' + str(proposed_Unique_Crashes))
print('proposed_Unique_Hangs = ' + str(proposed_Unique_Hangs))

