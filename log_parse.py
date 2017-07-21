# run P:\SleepMedicine\PatelSanjayResearch\Research\ECHOforMike\Code\log_parse.py

# Version 1.0 7/10/17
# This takes a MARS log file and creates a bar delim'd file showing how many
## matches each query got

import re

## FOR REAL USE:
# Input file (usually a MARS .log file)
path_inf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/Runs-2017-07-17/MRNgrab-last.log'
# Output file (no need to create in advance)
path_outf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/Runs-2017-07-17/MRNgrab-last-log.txt'

inf = open(path_inf, 'r')
outf = open(path_outf, 'wb')

print "I am doing something\n"

for line in inf:
    
    ID = re.match(r'.*(\d{9})([A-Za-z]{0,3})$', line, re.M|re.I) #\D matches 0 to 3 in case there is no HOSP code
    if ID:
        id = ID.group(1)
        hosp = ID.group(2)
        patient = '|'.join([str(id), hosp])
        outf.write(patient)
    else:
        pass
        
    RECS = re.match(r'.*\s(\d{1,2})\n', line, re.M|re.I)
    if RECS:
        records = str(RECS.group(1))
        outf.write('|' + records + '\n')
    else:
        pass
    

        
outf.close()
