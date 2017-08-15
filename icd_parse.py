# -*- coding: utf-8 -*-
"""
Created on Tue Aug 08 08:22:55 2017

@author: genuardimv
"""

# Version 1.1
# Functionized
# Uses a pre-processed .out file that gets rid of the ~~~'s (use detilde.py first)

import datetime
import numpy as np
import pandas as pd
import os
import sys


# Input file (.out file result of icd extractor)
path_inf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/Runs-2017-07-27/icd4NT.txt'
outf = 'output4.csv'

print 'Sit tight, I am doing something...\n'

def main():
    badsocs = ["999999999", "000000000", "099999999"]
    
    RetVal = 0 # Counter of studies parsed
    PatVal = 0 # Counter of patients parsed (roughly)
    now_soc = "-111111111"
    
    inf = open(path_inf, 'r')
    
    for line in inf:
        RetVal += 1
        l = line.split('|')
            
        # now_soc is the ID for the "current" patient 
        if l[4] in badsocs:
            line_id = l[1]              #use MRN as current pt ID
        else:
            line_id = l[4]              #use SSN as current pt ID
    
        if RetVal == 1:                 #if it's the FIRST patient
            now_soc = line_id
            df = get_codes(l)
        elif now_soc == line_id:        #if it's NOT a new patient
            df_add = get_codes(l)
            df = df.append(df_add)
        else:                           #if it's a NEW patient
            PatVal += 1
            now_soc = line_id
            
            # add column for internal patient ID (for my QI only)
            df['mgid'] = PatVal
            # organize by index (date), then strip duplicate ICDs leaving earliest
            df.sort_index(inplace=True)
            df.drop_duplicates(subset=['icd'], keep='first', inplace=True)

            # if file does not exist write header 
            if not os.path.isfile(outf):
                df.to_csv(outf,header ='column_names')
            else: # else it exists so append without writing the header
                df.to_csv(outf,mode = 'a',header=False)  
            df = get_codes(l)           #now overwrite df with the new patient's data
            
        if RetVal%1000 == 0:
            sys.stderr.write(str(RetVal))
            sys.stderr.write('\n')       #just an output to console to show it's working
    
    # After loop breaks, still have to handle the last line
    PatVal += 1
    df['mgid'] = PatVal
    # organize by index (date), then strip duplicate ICDs leaving earliest
    df.sort_index(inplace=True)
    df.drop_duplicates(subset=['icd'], keep='first', inplace=True)
    # output this last patient to the csv
    df.to_csv(outf,mode = 'a',header=False)
            
    print '\nTotal records read:    ', RetVal
    inf.close()
    
    return RetVal
    

def get_codes(ln):
    dateis = datetime.datetime.strptime(ln[2], ' %m/%d/%y')
    df1 = pd.DataFrame({'icd': ln[15:39],
                       'source': np.repeat('mpax',39-15),
                       'patient': ln[1].strip()},
                      index=np.repeat(dateis,39-15))
    df2 = pd.DataFrame({'icd': [ln[i] for i in range(40,88,2)],
                       'source': np.repeat('mpax',len(range(40,88,2))),
                       'patient': ln[1].strip(),
                       'date': [ln[i] for i in range(41,89,2)]})
    df1['icd'].replace('', np.nan, inplace=True)
    df2['icd'].replace('', np.nan, inplace=True)
    df2['date'].replace('', np.nan, inplace=True)
    df1.dropna(subset=['icd'], inplace=True)
    df2.dropna(subset=['icd'], inplace=True)
    
    df2.fillna(ln[2], inplace=True) #fill empty dates with admit date (if there are any)
    
    df22 = df2.set_index(pd.to_datetime(df2["date"], errors="coerce"))
    df22.index.name = None
    del df22['date']
    df = df1.append(df22)
    
    df.index.name = 'date'
   
    return df

    
records = main()
    
"""
0072266326226| 100446122 BRH| 01/14/06||182449962|19490101|M|W|O|SV|~~~|GNM|182446862|~~~|~~~|715.90|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|~~~|715.90|DREG|L|7|UN|KOR JOHN

1		      account number
2		      MRN
3		      Last adm date
4		      Last disc date
5	MP0005	SOCSECNUMBER
6	MP0006	BIRTHDATE
7	MP0007	SEX
8	MP0008	RACE
9	MP0021	PROCESSTYPE
10	MP0022	PATIENTTYPE
11	MP0024	DISCHARGEDISPOSITION
12	MP0025	HOSPITALSERVICE
13	MP0030	MEDICALRECORDNUMBER
14	MP0031	DEATHINDICATOR
15	MP0034	CENSUSTRACT
16	MP0302	FINALDIAGNOSIS#1
17	MP0308	FINALDIAGNOSIS#2
18	MP0314	FINALDIAGNOSIS#2
19	MP0320	FINALDIAGNOSIS#4
20	MP0326	FINALDIAGNOSIS#5
21	MP0332	FINALDIAGNOSIS#6
22	MP0338	FINALDIAGNOSIS#7
23	MP0344	FINALDIAGNOSIS#8
24	MP0350	FINALDIAGNOSIS#9
25	MP0356	FINALDIAGNOSIS#10
26	MP0362	FINALDIAGNOSIS#11
27	MP0368	FINALDIAGNOSIS#12
28	MP0374	FINALDIAGNOSIS#13
29	MP0380	FINALDIAGNOSIS#14
30	MP0386	FINALDIAGNOSIS#15
31	MP0392	FINALDIAGNOSIS#16
32	MP0398	FINALDIAGNOSIS#17
33	MP0404	FINALDIAGNOSIS#18
34	MP0410	FINALDIAGNOSIS#19
35	MP0416	FINALDIAGNOSIS#20
36	MP0422	FINALDIAGNOSIS#21
37	MP0428	FINALDIAGNOSIS#22
38	MP0434	FINALDIAGNOSIS#23
39	MP0440	FINALDIAGNOSIS#24
40	MP0446	FINALDIAGNOSIS#25
41	MP0803	PROCEDURE#1PROCEDURECODE-ICD9ORCPT
42	MP0804	PROCEDURE#1PROCEDUREDATE
43	MP0823	PROCEDURE#2PROCEDURECODE-ICD9ORCPT
44	MP0824	PROCEDURE#2PROCEDUREDATE
45	MP0843	PROCEDURE#3PROCEDURECODE-ICD9ORCPT
46	MP0844	PROCEDURE#3PROCEDUREDATE
47	MP0863	PROCEDURE#4PROCEDURECODE-ICD9ORCPT
48	MP0864	PROCEDURE#4PROCEDUREDATE
49	MP0883	PROCEDURE#5PROCEDURECODE-ICD9ORCPT
50	MP0884	PROCEDURE#5PROCEDUREDATE
51	MP0903	PROCEDURE#6PROCEDURECODE-ICD9ORCPT
52	MP0904	PROCEDURE#6PROCEDUREDATE
53	MP0923	PROCEDURE#7PROCEDURECODE-ICD9ORCPT
54	MP0924	PROCEDURE#7PROCEDUREDATE
55	MP0943	PROCEDURE#8PROCEDURECODE-ICD9ORCPT
56	MP0944	PROCEDURE#8PROCEDUREDATE
57	MP0963	PROCEDURE#9PROCEDURECODE-ICD9ORCPT
58	MP0964	PROCEDURE#9PROCEDUREDATE
59	MP0983	PROCEDURE#10PROCEDURECODE-ICD9ORCPT
60	MP0984	PROCEDURE#10PROCEDUREDATE
61	MP1003	PROCEDURE#11PROCEDURECODE-ICD9ORCPT
62	MP1004	PROCEDURE#11PROCEDUREDATE
63	MP1023	PROCEDURE#12PROCEDURECODE-ICD9ORCPT
64	MP1024	PROCEDURE#12PROCEDUREDATE
65	MP1043	PROCEDURE#13PROCEDURECODE-ICD9ORCPT
66	MP1044	PROCEDURE#13PROCEDUREDATE
67	MP1063	PROCEDURE#14PROCEDURECODE-ICD9ORCPT
68	MP1064	PROCEDURE#14PROCEDUREDATE
69	MP1083	PROCEDURE#15PROCEDURECODE-ICD9ORCPT
70	MP1084	PROCEDURE#15PROCEDUREDATE
71	MP1103	PROCEDURE#16PROCEDURECODE-ICD9ORCPT
72	MP1104	PROCEDURE#16PROCEDUREDATE
73	MP1123	PROCEDURE#17PROCEDURECODE-ICD9ORCPT
74	MP1124	PROCEDURE#17PROCEDUREDATE
75	MP1143	PROCEDURE#18PROCEDURECODE-ICD9ORCPT
76	MP1144	PROCEDURE#18PROCEDUREDATE
77	MP1163	PROCEDURE#19PROCEDURECODE-ICD9ORCPT
78	MP1164	PROCEDURE#19PROCEDUREDATE
79	MP1183	PROCEDURE#20PROCEDURECODE-ICD9ORCPT
80	MP1184	PROCEDURE#20PROCEDUREDATE
81	MP1203	PROCEDURE#21PROCEDURECODE-ICD9ORCPT
82	MP1204	PROCEDURE#21PROCEDUREDATE
83	MP1223	PROCEDURE#22PROCEDURECODE-ICD9ORCPT
84	MP1224	PROCEDURE#22PROCEDUREDATE
85	MP1243	PROCEDURE#23PROCEDURECODE-ICD9ORCPT
86	MP1244	PROCEDURE#23PROCEDUREDATE
87	MP1263	PROCEDURE#24PROCEDURECODE-ICD9ORCPT
88	MP1264	PROCEDURE#24PROCEDUREDATE
89	MP1283	PROCEDURE#25PROCEDURECODE-ICD9ORCPT
90	MP1284	PROCEDURE#25PROCEDUREDATE
91	MP1361	DRG-1
92	MP0452	WORKINGDIAGNOSIS#1
93	MP1601	SERVICE-1NURSSTATION
94	MP0028	VISITTYPE
95	MP0029	VISITSOURCE
96	MP0160	FINANCIALCLASS
97	MP0002	PATIENTNAMELASTFIRSTMI

"""