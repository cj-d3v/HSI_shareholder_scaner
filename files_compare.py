import os
import re
import requests
import pandas as pd
import timeit



def compare(fpath, file_name1, file_name2):
    file1 = pd.read_csv('{}/{}'.format(fpath, file_name1))
    file2 = pd.read_csv('{}/{}'.format(fpath, file_name2))
    file1 = file1.set_index('Name of CCASS Participant(* for Consenting Investor Participants )')
    file2 = file2.set_index('Name of CCASS Participant(* for Consenting Investor Participants )')
    
    outputs = []
    for holder_name in file1.index:
        str1 = str(file1.loc[holder_name,['Shareholding']])
        if holder_name in file2.index:
            str2 = str(file2.loc[holder_name,['Shareholding']])
            if str1 != str2:
                date = os.path.basename(file_name2)[:10]
                output0 = 'As of {}, '.format(date)+ holder_name +' holding change from ' + str(file1.loc[holder_name,['Shareholding']])+' to'+str(file2.loc[holder_name,['Shareholding']])
                output = output0.replace('Shareholding ','').replace('Name: {}, dtype: object'.format(holder_name),'').replace('\n','')
                #output = output + '\n'
                #print(output)
                outputs.append(output)
                
        else:
            output = 'As of {}, '.format(date) + holder_name + ' removed from the list. Its holding at last date is ' + str(file1.loc[holder_name,['Shareholding']])
            output = output.replace('Shareholding ','').replace('\nName: SUCCESS SECURITIES LTD, dtype: object','')
            #print(output)
            outputs.append(output)
    print(outputs)
    return outputs

def read_files():
    link = "https://warrants-hk.credit-suisse.com/en/underlying/hsi_e.cgi"
    f = requests.get(link)
    symbolslist0 = re.findall(r'<td.*?><a.*?>(\d+)(?=</a></td>)', f.text, re.MULTILINE)
    symbolslist = symbolslist0[:50]
    
    for symbol in symbolslist:
        fpath = '{}_hist_sharehold'.format(symbol)
        fileslist = os.listdir(fpath)
        fileslist.sort()
        for filename in fileslist:
            if 'file1' in locals():
                file2 = filename
            else:
                file1 = filename
            if 'file2' in locals():
                compare(fpath, file1, file2)
                file1 = file2

#def read_files():
    link = "https://warrants-hk.credit-suisse.com/en/underlying/hsi_e.cgi"
    f = requests.get(link)
    symbolslist0 = re.findall(r'<td.*?><a.*?>(\d+)(?=</a></td>)', f.text, re.MULTILINE)
    symbolslist = symbolslist0[:50]
    
    for symbol in symbolslist:
        fileslist = os.listdir('{}_hist_sharehold'.format(symbol))
        fileslist.sort()
        files_dif = pd.DataFrame()
        for filename in fileslist:
            if 'file1' in locals():
                file2 = filename
            else:
                file1 = filename
            if 'file2' in locals():
                files_dif.append(compare(file1, file2))
                file1 = file2
        files_dif.to_csv('{}_hist_sharehold/{}_dif'.format(symbol, symbol))

if __name__=="__main__":
    start = timeit.default_timer()
    read_files()
    stop = timeit.default_timer()
    print('Files compare time cost:{}'.format((stop - start)))