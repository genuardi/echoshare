# -*- coding: utf-8 -*-
"""
Created on Wed Aug 09 14:10:04 2017

@author: genuardimv
"""

# Version 1.0

# Takes a .out file and replaces all "~~~" with ""

path_inf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/Runs-2017-07-27/icd4.out'
# Output file (no need to create in advance)
path_outf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/Runs-2017-07-27/icd4NT.txt'
print 'Sit tight, I am doing something...\nRecords read:  '

def main():
    
    RetVal = 0 # Counter of studies parsed
    inf = open(path_inf, 'r')
    outf = open(path_outf, 'wb')
    
    for line in inf:
        RetVal += 1
        
        newline = line.replace('~~~', '')
        
        outf.write(newline)
        
    outf.close()
    inf.close()
    
    return RetVal
    
records = main()

print(records)

