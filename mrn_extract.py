# run P:\SleepMedicine\PatelSanjayResearch\Research\ECHOforMike\Code\mrn_extract.py

# Version 1.0 7/10/17
# This script will parse a .out file resulting from query of the PAT database

import re


## FOR REAL USE:
# Input file (usually a MARS .out file)
path_inf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/Runs-2017-07-17/MRNgrab-last.out'
# Output file (no need to create in advance)
path_outf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/Runs-2017-07-17/MRNgrab-last.txt'

inf = open(path_inf, 'r')
outf = open(path_outf, 'wb')

no = 800000

print "I am doing something\n"

for line in inf:

    if "DEMOGRAPHICS" in line:
        no += 1
    else:
        pass
	
    HIT = re.match(r'\s+\d+\.\s+(.+)\s*(\d{9})\s(\D{3})\s*(\d{2}\/\d{2}\/\d{4})', line, re.M|re.I)
    if HIT:
        name = HIT.group(1)
        name2 = re.match(r'^(\D+\S)\s+$', name, re.M|re.I)
        name3 = name2.group(1)
		
        mrn = HIT.group(2)
        hosp = HIT.group(3)
        dob = HIT.group(4)
        patient = '|'.join([str(no), name3, mrn, hosp, dob])
        outf.write(patient + "\n")
    else:
        pass

outf.close()
