# Version 2.51 7/11/17
# Make VAD identification more robust.
# Added columns for manual entrys
# extract ptyp, the I/O designation
# First spyder version!
# Fixed problem with capital letters in valve section

from datetime import datetime
startTime = datetime.now()

import re
import sys
import numpy as np


## FOR REAL USE:
# Input file (usually a MARS .out file). Text of all echo reports. **BAR formatted**
path_inf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/RAW/07-07_all_cksms.out'
# Output file (no need to create in advance)
path_outf = 'P:/SleepMedicine/PatelSanjayResearch/Research/ECHOforMike/MARS_sync/out/RAW/07-07_all_cksms_parsed.txt'


severity = ['mild', 'moderate', 'severe', 'Mild', 'Moderate', 'Severe']

# Dictionaries
subtypes_cvis = {
    'CECHO': 'TTE',
    'DOBSTRS': 'Stress',
    'ECCOM': 'TTE',
    'ECCOMBUND': 'TTE',
    'ECCOMBUNDP': 'TTE',
    'ECCOMP': 'TTE',
    'ECCOMW': 'TTE',
    'ECCOMWP': 'TTE',
    'ECHO': 'RESOLVE', # TTE or TEE
    'ECLTD': 'TTE',
    'ECLTDP': 'TTE',
    'ECLTDW': 'TTE',
    'ECSTRCMDB': 'Stress',
    'ECSTRCMDBC': 'Stress',
    'ECSTRCMDD': 'Stress',
    'ECSTRCMDT': 'Stress',
    'ECSTRCMDTC': 'Stress',
    'ECSTROMDPC': 'Stress',
    'ECSTRSRPTT': 'Stress',
    'ECSTRSXWPD': 'Stress',
    'ECSTRSXWPT': 'Stress',
    'ECTEE': 'TEE',
    'ECTEEC': 'TEE',
    'ECTEEW': 'TEE',
    'EXSTRSBIKE': 'Stress',
    'EXSTRSTRD': 'RESOLVE', # Stress or TTE
    'TTE': 'TTE',
    'TEE': 'TEE',
    'USECCOMBUN': 'TTE',
    'USECCOMBUP': 'TTE',
}

def GetOut(inf, outf, path_inf):
    RetVal = 0 # Counter of studies parsed
    
    # Header for the output file
    outf.write(str('no|cksm|ACID|styp|site|mno|ptyp|RVSP|TR Jet|EF|AS|AI|MS|MR|VAD|TDS|Protocol|flag|addendYN|addendum|'))
    outf.write(str('m_review|m_RVSP|m_TR Jet|m_EF|m_AS|m_AI|m_MS|m_MR|m_VAD|m_TDS|m_Protocol|m_exclude') +  '\n')

    
    # Initialize things
    report = ''
    report_nl = ''
    
    r_no = []
    r_cksm = []
    r_acid = []
    r_typ = []
    r_ptyp = []
    r_styp = []
    r_site = []
    r_mno = []
    r_addYN = []
    
    r_rvsp = []
    r_trj = []
    r_ef = []
    r_vad = []
    r_tds = []
    r_proto = []
    r_flag = []
    
    r_AS = []
    r_AI = []
    r_MS = []
    r_MR = []
    
    report_add = ''

    for line in inf:


        if line.startswith('S_O_H'):
            # Break the header into components that are used to define the study
            headerLine = next(inf)
            h = headerLine.split('|')
            
            r_no.append(str(RetVal))
            r_cksm.append(h[0])
            r_typ.append(str(h[4]))
            r_styp.append(str(h[9]))
            r_acid.append(str(h[11])[:9])
            r_site.append(str(h[33]))
            r_mno.append(str(h[35]))
            r_ptyp.append(str(h[45]))
            r_addYN.append(str(h[70]))
        
        elif line.startswith('REFERRING DIAGNOSIS'):
            pass
        
        elif not line.startswith('E_O_R'):
            # report, running string of current study
            # report_nl, version containing line breaks, used only to identify conclusions in FINAL IMPRESSIONS section later on
            report_nl += line
            report += line.rstrip('\n')
            
        else:
            # If end of report reached
            report_nl += line
            report += line.rstrip('\n')
            

            if r_mno[-1] == 'CVIS':    #so far, only parsing CVIS studies
    
                # Set flag to empty, change if there is a problem
                r_flag.append('')    
            
                # Protocols
                r_proto.append(subtypes_cvis[r_styp[-1]])
                        
                if r_proto[-1] == 'RESOLVE':
                    if re.match(r'.*Transesophageal Echocardiogram\s{3,}.*', report, re.M|re.I):
                        r_proto[-1] = 'TEE'
                    elif re.match(r'.*STRESS TWO-DIMENSIONAL.*', report, re.M|re.I):
                        r_proto[-1] = 'Stress'
                    elif re.match(r'.*Transthoracic Echocardiogram\s{3,}.*', report, re.M|re.I):
                        r_proto[-1] = 'TTE'
                    else:
                        r_flag[-1] += 'unknownprotocol^'
                        
                # If study is a stress, will need to strip out the stress portion before parsing PA pressures
                if r_proto[-1] == 'Stress':
                    if re.match(r'.*STRESS TWO-DIMENSIONAL(?:\s|\S)*?$', report, re.M|re.I):
                        report_PA = re.sub(r'STRESS TWO-DIMENSIONAL(?:\s|\S)*?$', '', report)
                    else:
                        r_flag[-1] += 'stressfmtunusual^'
                else:
                    report_PA = report                 
            
                # Create a section for FINAL IMPRESSIONS
                IMP = re.search(r'^FINAL IMPRESSIONS:(.*)$', report_nl, re.M|re.I|re.DOTALL)
                if IMP:
                    report_IMP = IMP.group(1)
                    report_IMP = re.sub('\\n\d\d\)', '%%%%%%', report_IMP) # using %%%%%% to replace numbering
                    report_IMP = re.sub('\\n', '', report_IMP) # line breaks are no longer needed
                else:
                    r_flag[-1] += 'impressionfmtunusual^'

                # Create a section for *** Addendum ***                
                if r_addYN[-1] == 'ADDENDED':
                    ADD = re.search(r'.*Addendum(.*?)\d{1,2}\/\d{1,2}\/\d{1,4}.*', report, re.M|re.I|re.DOTALL)
                             # Match text between 'addendum' and date in signature
                    if ADD:
                        report_add = ADD.group(1)
                    else:
                        pass
                
                # RVSP, using report_PA
                RVSP = re.match(r'.*(?:pulmonary artery|right ventricular) systolic pressure is (\d+).*', report_PA, re.M|re.I)
                if RVSP:
                    r_rvsp.append(int(RVSP.group(1)))
                else:
                    RVSP = re.match(r'.*(No) tricuspid regurgitant spectral velocity was obtainable.*', report_PA, re.M|re.I)
                    if RVSP:
                        r_rvsp.append(-8888)
                    else:
                        RVSP = re.match(r'.*SPECTRAL DOPPLER:\s*Doppler interrogation was (normal).*', report_PA, re.M|re.I)
                        if RVSP:
                            r_rvsp.append(-1111)
                        else:
                            r_rvsp.append(-9999)
            
                # TR jet, using report_PA
                TRJ = re.match(r'.*tricuspid regurgitant velocity is (\d\.{0,1}\d{0,2}).*', report_PA, re.M|re.I)
                if TRJ:
                    r_trj.append(float(TRJ.group(1)))
                else:
                    r_trj.append(-9999)
                
                # EF
                EF = re.match(r'.*(?:EF%:\s+(?:<|>){0,1}\s{0,2}|ejection fraction of (?:<|>){0,1}\s{0,2}|ejection fraction is (?:<|>){0,1}\s{0,2})(\d+).*', report, re.M|re.I)
                if EF:
                    r_ef.append(int(EF.group(1)))
                elif re.match(r'.*(diffuse severe hypokinesis. Cannot estimate the overall left|left ventricular function is severely decreased.).*', report, re.M|re.I):
                    r_ef.append(int(10))
                else:
                    r_ef.append(int(-9999))
                                                
                # LVAD/ECMO/Impella studies
                if re.match(r'.*(LVAD|ventricular assist device|ECMO|impella).*', report, re.M|re.I):
                    r_vad.append('1')
                else:
                    r_vad.append('0')
                
                # Technically difficult or otherwise limited studies
                if re.match(r'.*(Measurements Not Obtainable|FINAL IMPRESSIONS:.*limited study).*', report, re.M|re.I):
                    r_tds.append('1')
                else:
                    r_tds.append('0')
                
                # Valve disease section... use just FINAL IMPRESSIONS
                r_AS.append('')
                r_AI.append('')
                r_MS.append('')
                r_MR.append('')
                
                fis    = report_IMP.split('%%%%%%') # fis[0] will be empty
                del fis[0]
                
                # counters to warn if it appears we are double counting
                # syntax here is [AS, AI, MS, MR, two_diseases_on_same_impressions_line]
                dubs = [-1, -1, -1, -1, -1]
                
                for i in fis[0:]:
                    dubs[4] = -1
                    if i.startswith(' As compared to'):
                        continue
                    if re.search(r'(aortic.*steno|steno.*aortic)', i, re.M|re.I):
                        dubs[0] += 1
                        dubs[4] += 1
                        howbad =  {x for x in severity if x in i}
                        r_AS[-1] += ' '.join([x.lower() for x in howbad])
                    if re.search(r'(aortic.*regurg|regurg.*aortic|aortic.*insuf|insuf.*aortic)', i, re.M|re.I):
                        dubs[1] += 1
                        dubs[4] += 1
                        howbad =  {x for x in severity if x in i}
                        r_AI[-1] += ' '.join([x.lower() for x in howbad])
                    if re.search(r'(mitral.*steno|steno.*mitral)', i, re.M|re.I):
                        dubs[2] += 1
                        dubs[4] += 1
                        howbad =  {x for x in severity if x in i}
                        r_MS[-1] += ' '.join([x.lower() for x in howbad])
                    if re.search(r'(mitral.*regurg|regurg.*mitral)', i, re.M|re.I):
                        dubs[3] += 1
                        dubs[4] += 1
                        howbad =  {x for x in severity if x in i}
                        r_MR[-1] += ' '.join([x.lower() for x in howbad])
                    if dubs[4] > 0:
                        r_flag[-1] += 'combinedimp^' # warning that a single impression combines comments on two different valve pathologies
                        
                if any(j > 0 for j in dubs[:3]):
                    r_flag[-1] += 'multiline^' # warning that a valve pathology is mentioned in more than one impression line

            else: # -2222 is NOT CVIS
                r_rvsp.append(-2222)
                r_trj.append(-2222)
                r_ef.append(-2222)
                r_vad.append('-2222')
                r_tds.append('-2222')
                r_proto.append('-2222')
                r_flag.append('')
                r_AS.append('-2222')
                r_AI.append('-2222')
                r_MS.append('-2222')
                r_MR.append('-2222')
                

            demos = '|'.join([r_no[-1], r_cksm[-1], r_acid[-1], r_styp[-1], r_site[-1], r_mno[-1], r_ptyp[-1]])
            values = '|'.join([str(r_rvsp[-1]), str(r_trj[-1]), str(r_ef[-1])])
            valves = '|'.join([r_AS[-1], r_AI[-1], r_MS[-1], r_MR[-1]])
            checks = '|'.join([r_vad[-1], r_tds[-1], r_proto[-1], r_flag[-1], r_addYN[-1], report_add])
            
            outf.write(demos + '|' + values + '|' + valves + '|' + checks + '\n')
            
            # Done this study; reset variables; increment record counter; print progress to consule
            report = ''
            report_nl = ''
            report_PA = ''
            report_IMP = ''
            report_add = ''
            RetVal += 1
            
            #if RetVal%2500 == 0:
            #    sys.stderr.write(str(RetVal) + '  ')
            
            if RetVal%300 == 0:
                sys.stderr.write('|')
            
            else:
                pass
    
    np_my_data = np.matrix([r_no, r_cksm, r_styp, r_site, r_mno, r_rvsp, r_ef])


    return RetVal, np_my_data
    # Number of reports read; and the actual return of the function

print 'Sit tight, I am doing something...\nRecords read:  '
    
with open(path_inf, 'r') as inf, open(path_outf, 'wb') as outf:
    RecordCount, np_dataout = GetOut(inf, outf, path_inf)
print '\nTotal records read:    ', RecordCount
print 'File creation time:    ', datetime.now() - startTime
