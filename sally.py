import re
import pandas as pds
#import numpy as np

def creatingDataFrames(file_name, total_cols=30):
    csv = open(file_name)
    csv.next()
    csv.next()

    header = csv.next()
    header = header.split(',')

    new_list = []
    formulas = []
    #total_cols  = 30

    for line in csv:
        if line.strip() == '': continue
        sp = line.split(',')
        if sp[4] == '': continue
        formulas.append(sp.pop(4))
        new_list.append(sp[:total_cols])
        
    header = header[:total_cols]

    df = pds.DataFrame(new_list, index = formulas, columns = header)
    
    Ratios = []
    
    for line in formulas:
        expression = r'([A-Za-z]{1,2})(\d{0,2})'
        match = re.findall(expression, line)
        
        match_dict = {}
        for atom, num in match:
            if num == '':
                match_dict[atom] = 1.
            else:
                match_dict[atom] = float(num)
        if 'O' in match_dict and 'C' in match_dict:
            match_dict['OCratio'] = match_dict['O'] / match_dict ['C']
        if 'H' in match_dict and 'C' in match_dict:
            match_dict['HCratio'] = match_dict['H'] / match_dict['C']
        Ratios.append(match_dict)

    Table = pds.DataFrame(Ratios, index = formulas)

    df = df.join(Table)

    return df
    
    #x = df['OCratio']
    #y = df['HCratio']
    #z1 = df['Volume']
    #z = array(z1, dtype=float)
    
    #plt.scatter(x,y,s=z*50,c=z)
    #plt.colorbar()