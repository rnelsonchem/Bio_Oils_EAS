import re

import numpy as np
import pandas as pds

elements = { 'H': 1.00794, 'C': 12.0107, 'O': 15.9994 }

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

def creatingDataFrames2(file_name, total_cols=30, index_col='Formula',
                       formula_col='Formula', 
                       ratiolist=[('O', 'C'), ('H', 'C')]
                       ):
    csv = open(file_name)
    
    new_list = []
    header = None

    for line in csv:
        # Skip comment lines
        if line[0] == '#': 
            continue
        # Skip blank lines
        elif line.isspace(): 
            continue
        # Make a header list from the very first line
        elif header == None:
            header = line.split(',')
            continue                  
        # Process the rest of the data
        sp = line.split(',')
        new_list.append( sp[:total_cols] )
    
    header = header[:total_cols]

    df = pds.DataFrame(new_list, columns=header) 
    if formula_col != None:
        table = pds.DataFrame( ratiocalc(df[formula_col], ratiolist) )    
        df = df.join(table)

    return df.set_index(index_col)
    
def createDF(file_name, total_cols=30, index_col='Formula',
             formula_col='Formula', ratiolist=[('O', 'C'), ('H', 'C')], 
             skiprows=2):
    df = pds.read_csv(file_name, skiprows=skiprows, 
                      usecols=range(total_cols) ) 
                      
    df = df.dropna( subset=[index_col] ) 
    
    if formula_col != None:
        table = pds.DataFrame( ratiocalc(df[formula_col], ratiolist) )    
        df = df.join(table)

    return df.set_index(index_col)
                 
def ratiocalc(formulas, ratiolist):
    expression = r'([A-Za-z]{1,2})(\d{0,2})'
    regex = re.compile( expression )
    
    ratios = []    
    for line in formulas:
        match_dict = {}
        
        if pds.isnull(line):
            ratios.append(match_dict)
            continue
        
        match = regex.findall(line)
        
        for atom, num in match:
            if num == '':
                match_dict[atom] = 1.
            else:
                match_dict[atom] = float(num)
                
        for atomA, atomB in ratiolist:        
            if atomA in match_dict and atomB in match_dict:
                column_name = atomA + atomB + ' ratio'
                ratio = match_dict[atomA]/match_dict[atomB]
                match_dict[column_name] = ratio
        
        ratios.append(match_dict)
        
    return ratios

def df_comp(df1, df2, tols={'Mass': 0.05,'RT': 0.1}, 
        extra_cols=['Vol %', 'HC ratio', 'OC ratio']):

    matches = {}
    count = 1
    
    all_cols = tols.keys() + extra_cols
    
    for cpd in df1.index:
        mask = np.ones( len(df2), dtype=bool )
        
        for label in tols:
            tol = tols[label]
            mask *= (df2[label] > df1[label][cpd]-tol) & \
                    (df2[label] < df1[label][cpd]+tol)

        for i in list(df2[mask].index):
            df1_vals = [cpd] + list(df1[all_cols].ix[cpd])
            df2_vals = [i] + list(df2[all_cols].ix[i])
            matches['Match {:d}'.format(count)] = df1_vals + df2_vals
            count += 1
    
    columns = ['df1'] + [i+' df1' for i in all_cols] + \
            ['df2'] + [i+' df2' for i in all_cols]

    df = pds.DataFrame.from_dict(matches, orient='index')
    df.columns = columns
    
    return df

