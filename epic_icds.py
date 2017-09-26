# -*- coding: utf-8 -*-
"""***************************************************************************
* Created on Sat Sep 16 21:39:41 2017
* @author: genuardimv
* 
* This will parse EPIC .out data and create list of ICDs for each patient,
* similar to icd_parse.py for MPAX.
* 
* Version 1.3
***************************************************************************"""
# Added way to ignore bad headers and patients with ssn='', and will WARN user on sys screen
# Added log file support


import datetime, os, sys, re, logging
import numpy as np
import pandas as pd


"""***************************************************************************
* Make sure to set input/output file paths below before running on new data
***************************************************************************"""
path_inf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/Runs-2017-07-31/epic.out'
#path_inf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/Runs-2017-09-06/epic4.out'
outf = 'epicout_TEST.csv'



def main(log):
    
    RetVal = 0 # Counter of studies parsed
    PatVal = 0 # Counter of patients parsed (roughly)
    last_soc = -111111111
    patreport = ''
    df_empt = pd.DataFrame(columns=['ICD','SOURCE','PATIENT','DATE','DOB'])
    df_pat = df_empt
    
    inf = open(path_inf, 'r')
    log.info('Start parse')
    
    for line in inf:
            
        if line.startswith('S_O_H'):        # Break the header
            headerok = 1
            headerLine = next(inf)
            h = headerLine.split('|')
            if len(h) != 72:                # If bad header!
                log.warning('There is a bad header at: ' + str(RetVal))
                headerok = 0
            else:
                this_soc = h[61]
                date = h[3][0:8]    #some EPIC dates have 0000 at end
                pat = h[2].strip()
                dob = h[24]
                if this_soc == '':
                    log.warning('There is a missing SSN at: ' + str(RetVal))
                else:
                    pass
                if last_soc != this_soc:        # if this header is new pt
                    df_pat = trim(df_pat, PatVal)
                    sendtofile(df_pat, outf)
                    PatVal += 1
                    df_pat = df_empt
                    last_soc = this_soc
                else:
                    pass
        elif line.startswith('\n'):         # Ignore blank lines for speed
            pass
        elif line.startswith('E_O_R'):      # Process at end of report
            RetVal += 1
            if headerok:
                dficds = process(patreport, pat, dob, date)
                df_pat = df_pat.append(dficds)  # add to df for this patient
            else:
                pass
            patreport = ''
            if RetVal%1000 == 0:
                sys.stderr.write(str(RetVal) + '\t\t')
            else:
                pass
        else:
            patreport += line               # generate report
                   
        
    # After loop breaks, still have to handle the last line
    PatVal += 1
    df_pat = trim(df_pat, PatVal)
    sendtofile(df_pat, outf)                 
    inf.close()

    return RetVal, PatVal
            
    
def trim(df, PatVal): #remove duplicate ICDs for same patient            
    # add column for internal patient ID (for my QI only)
    df['MGID'] = PatVal
    # organize by index (date), then strip duplicate ICDs leaving earliest
    df.sort_index(inplace=True)
    df.drop_duplicates(subset=['ICD'], keep='first', inplace=True)
    return df
    

def process(report, pat, dob, date): #take the report and output a dataframe of ICDs from the report
    ex = re.compile(r'.*(V\d{2}\.\d{1,2})|\D(\d{3}\.\d{1,2})\D(?!\s*(ml|kg|lb|kilo|gram|poun|hours|hr|mg|fl|\(b))|(E\d{3}\.\d).*')    
    icds = ex.findall(report, re.M)
    dateis = datetime.datetime.strptime(date, '%Y%m%d')
    if icds:
        icd_list = flatten(icds)
        ln = len(icd_list)
        df = pd.DataFrame({'ICD': icd_list,
                           'SOURCE': np.repeat('EPIC',ln),
                           'PATIENT': np.repeat(pat,ln),
                           'DATE': np.repeat(date,ln),
                           'DOB': np.repeat(dob,ln)},
                           index=np.repeat(dateis,ln))
    else:
        df = pd.DataFrame(columns=['ICD','SOURCE','PATIENT','DATE','DOB'])     
    return df

    
def sendtofile(df, outf):
        # if file does not exist write header 
    if not os.path.isfile(outf):
        df.to_csv(outf,header =False)
    else: # else it exists so append without writing the header
        df.to_csv(outf,mode = 'a',header=False)  
    return 0
    

def flatten(lt):   # take a list of lists and remove blanks and flatten
    flat_list = [item for sublist in lt for item in sublist]
    flat_list[:] = [item for item in flat_list if item != '']
    return flat_list

# Config the logger file
LOG_FILENAME = outf[:-4] + '.log'
log = logging.getLogger()
fh = logging.FileHandler(filename=LOG_FILENAME)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
log.addHandler(fh)

# Run main
print 'Sit tight, I am doing something...\n' 
records, patients = main(log)

log.info('Total records read:     ' + str(records))
log.info('Total patients read:     ' + str(patients))
print '\nTotal records read:     ', records
print 'Total patients read:    ', patients

# Close the logger file
log.info('End parse')
log.removeHandler(fh)
del log,fh



