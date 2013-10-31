import re

import pandas as pds

def creatingDataFrames(file_name, total_cols=30, index_col='Formula',
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
             skiprows=2
             ):
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