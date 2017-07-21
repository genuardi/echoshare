# run P:\SleepMedicine\PatelSanjayResearch\Research\ECHOforMike\Code\log_parse.py

# Version 1.0 7/18/17
# This takes a MARS log file and repeats the input line once for each hit found
# ... why? because I fotgot to write the input MRN to my .out file on 7/17/17 runs

import re

# Input file (usually a MARS .log file)
path_inf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/Runs-2017-07-17/get19-2.log'
# Output file (no need to create in advance)
path_outf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/Runs-2017-07-17/get19-2-logrep.txt'

inf = open(path_inf, 'r')
outf = open(path_outf, 'wb')

print "\n.\n...\n.....I am doing something\n.....\n...\n."

for line in inf:
    
    ID = re.match(r'.*(\d{9})([A-Za-z]{0,3})$', line, re.M|re.I) #\D matches 0 to 3 in case there is no HOSP code
    if ID:
        ident = str(ID.group(1))
        hosp = ID.group(2)
    else:
        pass
        
    RECS = re.match(r'.*\s(\d{1,2})\n', line, re.M|re.I)
    if RECS:
        records = int(RECS.group(1))
        
        for i in range(0,records):
            outf.write(ident + '\n')

    else:
        pass
    

        
outf.close()
