# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 09:51:33 2017

@author: genuardimv

EKG Parser
Version 1.0
"""

import sys, re, logging
import pandas as pd

from funfunctions import getCSCOR

"""*************************************************************************
* 0 ::: process EKG cksm returns
*************************************************************************"""
# v1.0 10/26/2017
socfiles = ['raw/ekggetheader-s1.out', 'raw/ekggetheader-s2.out', 'raw/ekggetheader-s3.out', 'raw/ekggetheader-s4.out']
mrnfiles = ['raw/ekggetheader-mh1.out', 'raw/ekggetheader-mh2.out', 'raw/ekggetheader-mh3.out']

def cleanline(x):
    m = re.match(r'^(.*)\|.*', x, re.M|re.I)
    return m.group(1)

ekgsoc = pd.DataFrame()
for filename in socfiles:
    ekg_k = pd.read_csv(filename, sep=',', header=None, names=['CKSM'], index_col=False, dtype=str)
    ekg_k['CKSM'] = ekg_k['CKSM'].apply(lambda x: cleanline(x))
    ekgsoc = ekgsoc.append(ekg_k)

ekgmrn = pd.DataFrame()
for filename in mrnfiles:
    ekg_k = pd.read_csv(filename, sep=',', header=None, names=['CKSM'], index_col=False, dtype=str)
    ekg_k['CKSM'] = ekg_k['CKSM'].apply(lambda x: cleanline(x))
    ekgmrn = ekgmrn.append(ekg_k)

ekgsoc.drop_duplicates(inplace=True)
ekgmrn.drop_duplicates(inplace=True)

both = ekgsoc.append(ekgmrn)
both.drop_duplicates(inplace=True)
    
# On first run of EKG (10/26/2017):
    # len(ekgsoc) =         295848
    # len(ekgmrn) =         293202
    # NOTE no 'internal' dulicates in either list
    # len(both.drop_dups) = 302481

both['CKSM'] = both['CKSM'].apply(lambda x: 'cksm:' + x)
both.to_csv('output/EKGcksms.who', index=False, header=False)



"""*************************************************************************
* 1 ::: EKG Parsing
*************************************************************************"""

inf = ['ekg5.out', 'ekg6.out']
infpath = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/Runs-2017-10-28/'
outf = [x[:-4]+'-p.csv' for x in inf]

def attackfile(infl, f, log):
    log.info('Start parse of file: ' + f)

    report = ''
    df = pd.DataFrame()
    records = 0

    for line in infl:
        if line.startswith('S_O_H'):
            # Break the header into components that are used to define the study
            headerLine = next(infl)
            h = headerLine.split('|')
            
            thisekg = pd.DataFrame({'cksm': [h[0]],
                                    'MRNHOSP': [h[1][-12:]],
                                    'name': [h[2]],
                                    'DOS': [str(h[3])[:8]],
                                    'DOB': [h[24]],
                                    'SITE': [h[33]],
                                    'QRS': [-9999],
                                    'QT': [-9999],
                                    'QTc': [-9999],
                                    'RHYM': [''],
                                    'FMTERR': [0]
                                    })
            
        elif not line.startswith('E_O_R'):
            # report, running string of current study
            report += line
            
        else:
            # If end of report reached
            report += line
            records += 1
            qrs = re.search(r'QRS\sDuration\s+(\d{2,3})', report, re.M|re.I)
            if qrs:
                thisekg.loc[0, 'QRS'] = qrs.group(1)
            qt = re.search(r'QT:?\s+(\d{2,3})', report, re.M|re.I)
            if qt:
                thisekg.loc[0, 'QT'] = qt.group(1)
            qtc = re.search(r'QTc:?\s+(\d{2,3})', report, re.M|re.I)
            if qtc:
                thisekg.loc[0, 'QTc'] = qtc.group(1)
            af = re.search(r'\s(AF)\s|(a(?!l)\w*[ .]?(fib[\w]*|flutter))', report, re.M|re.I)
            if af:
                for x in [1,2]:
                    if af.group(x):
                        thisekg.loc[0, 'RHYM'] = af.group(x)

            if not(qrs or qt or qtc):
                thisekg.loc[0, 'FMTERR'] = 1
                log.warning('Unusal format detected at report: ' + h[0])
                
            df = df.append(thisekg)
            report = ''
            if records%1000 == 0:
                sys.stderr.write('|')
    
    df.to_csv('output/' + f[:-4]+'-p.csv', index=False)
    log.info('Done file: ' + f)
    log.info('Total records read:     ' + str(records))
    return 0

# Config the logger file
LOG_FILENAME = outf[-1][:-4] + '5and6.log'
log = logging.getLogger()
fh = logging.FileHandler(filename=LOG_FILENAME)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
log.addHandler(fh)
log.setLevel(logging.INFO)

# Run main
print 'Sit tight, I am doing something...\n' 
log.info('Start parse')

for f in inf:
    print f
    with open(infpath + f, 'r') as thisfile:
        attackfile(thisfile, f, log)

# Close the logger file
log.info('End parse')
log.removeHandler(fh)
del log,fh




"""*************************************************************************
* 2 ::: EKG processing (and a matching function for CSCOR_IDs)
*************************************************************************"""
# v1.0 11/1/2017
# Taking output of #1 ^^ and looking at trends

e1 = pd.read_csv('output/ekg1-p.csv', header='infer', index_col=False, dtype=str)
e1 = e1.append(pd.read_csv('output/ekg2-p.csv', header='infer', index_col=False, dtype=str))
e1 = e1.append(pd.read_csv('output/ekg3-p.csv', header='infer', index_col=False, dtype=str))
e1 = e1.append(pd.read_csv('output/ekg4-p.csv', header='infer', index_col=False, dtype=str))
e1 = e1.append(pd.read_csv('output/ekg5-p.csv', header='infer', index_col=False, dtype=str))
e1 = e1.append(pd.read_csv('output/ekg6-p.csv', header='infer', index_col=False, dtype=str))

e1['year'] = e1.DOS.str[:4].astype(int)
e1['DOB'] = pd.to_datetime(e1.DOB)
e1.rename(columns={'name': 'NAME'}, inplace=True)
   
ekg_ID = getCSCOR(e1)
ekg_ID.to_csv('output/EKG_with_CSCORID.csv', index=False, header=True)



"""*************************************************************************
* APPNDX ::: FUNCTIONS NEEDED
*************************************************************************
1. getCSCOR

"""