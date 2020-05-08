'''
This file is not close to be done, just a place holder for the main script.
I'm working on the parsers first
'''
import os
import pandas as pd
import json
import re
from collections import namedtuple
from utilities import *
from kegg_parser import Kegg
from lipidmaps_parser import lipidmaps
from knapsack_parser import knapsack_plants
import requests
from io import StringIO


def make_cache_dirs():
    if not os.path.exists('cache') : os.mkdir('cache')
    if not os.path.exists('cache/kegg') : os.mkdir('cache/kegg')
    if not os.path.exists('cache/lipidmaps') : os.mkdir('cache/lipidmaps')
    if not os.path.exists('cache/knapsack') : os.mkdir('cache/knapsack')
    if not os.path.exists('cache/dblink') : os.mkdir('cache/dblink')

def kegg_2_lipidmaps():
    try:
        r = requests.get('http://rest.genome.jp/link/lipidmaps/cpd')
        d = {}
        for line in r.text.splitlines():
            if len(line) == 0:
                continue
            cpd, lipidmaps, equiv = line.split('\t')
            lipidmaps = lipidmaps.split(':')[1].strip()
            cpd = cpd.split(':')[1].strip()
            d[cpd] = lipidmaps
        # Save dictionary for use offline
        with open('cache/dblink/kegg2lipidmaps', 'w') as f:
            json.dump(d, f)
        return d
    except:
        with open('cache/dblink/kegg2lipidmaps') as f:
            d = json.load(f)
        return d

def hmdb_2_kegg():
    try:
        r = requests.get('http://rest.genome.jp/link/hmdb/cpd')
        d = {}
        for line in r.text.splitlines():
            if len(line) == 0:
                continue
            cpd, hmdb, equiv = line.split('\t')
            hmdb = hmdb.split(':')[1].strip()
            cpd = cpd.split(':')[1].strip()
            d[hmdb] = cpd
        # Save dictionary for use offline
        with open('cache/dblink/hmdb2kegg', 'w') as f:
            json.dump(d, f)
        return d
    except:
        with open('cache/dblink/hmdb2kegg') as f:
            d = json.load(f)
        return d

def kegg_2_knapsack():
    try:
        r = requests.get('http://rest.genome.jp/link/knapsack/cpd')
        d = {}
        for line in r.text.splitlines():
            if len(line) == 0:
                continue
            cpd, knapsack, equiv = line.split('\t')
            knapsack = knapsack.split(':')[1].strip()
            cpd = cpd.split(':')[1].strip()
            d[cpd] = knapsack
        # Save dictionary for use offline
        with open('cache/dblink/kegg2knapsack', 'w') as f:
            json.dump(d, f)
        return d
    except:
        with open('cache/dblink/kegg2knapsack') as f:
            d = json.load(f)
        return d

# Function to check id convertion and choose the appropriate id for annotation
# Retirar os return dos if e apenas ter um return no final ??
def annotate(id):
    '''
    Annotate an id based on database and relation to other databases
    Check from with database the compound is from, check if there are any other convertion to other databases (if necessary)
    Annotate the compound acordingly to the database
    '''
    MC, C, SC, KS = '','','',''
    if id.startswith('C'):
        if id in kegg2knapsack:
            KS = knapsack_plants(kegg2knapsack[id])
        if id in kegg2lipidmaps:
          MC, C, SC, TC = lipidmaps(kegg2lipidmaps[id])
        else:
          MC, C, SC = Kegg(id, blacklist=blacklist).get_classes()
    elif id.startswith('H'):
        if id in hmdb2kegg:
          MC, C, SC = (Kegg(hmdb2kegg[id], blacklist=blacklist).get_classes())
        else:
          pass
    elif id.startswith('L'):
        MC, C, SC, TC = lipidmaps(id)
    return (MC, C, SC, KS)


def annotate_cell(cell, progress=Progress(1)):
    cell = list(cell.split("#"))
    MC,C,SC,KS = [],[],[],[]
    for code in cell:
        result = annotate(code)
        MC.append(result[0])
        C.append(result[1])
        SC.append(result[2])
        KS.append(result[3])
    for x in range(0,len(MC),1):
        if type(MC[x]) == list:
            MC[x] = "#".join(MC[x])
    for x in range(0,len(C),1):
        if type(C[x]) == list:
            C[x] = "#".join(C[x])
    for x in range(0,len(SC),1):
        if type(SC[x]) == list:
            SC[x] = "#".join(SC[x])
    for x in range(0,len(KS),1):
        if type(KS[x]) == list:
            KS[x] = "#".join(KS[x])
    MC = "#".join(set(MC)).lstrip('#')
    C = "#".join(set(C)).lstrip('#')
    SC = "#".join(set(SC)).lstrip('#')
    KS = "#".join(set(KS)).lstrip('#')
    col_names = ['Major Class',
                 'Class',
                 'Secondary Class',
                 'KNApSAcK']
    progress.tick()
    return pd.Series((MC,C,SC,KS), index=col_names)

def masstrix_tsv(file):
    tsv=[]
    with open(file) as f:
        for line in f.readlines():
            tsv.append(line)
    new_tsv = [tsv[-1]]
    new_tsv.extend(tsv[:-1])
    new_tsv = "\n".join(new_tsv)
    df = pd.read_csv(StringIO(new_tsv), sep = '\t')
    return df

def cleanup_cols(df, isotopes=True, uniqueID=True, columns=None):
    """Removes the 'uniqueID' and the 'isotope presence' columns."""
    col_names = []
    if uniqueID:
        col_names.append('uniqueID')
    if isotopes:
        iso_names = ('C13','O18','N15', 'S34', 'Mg25', 'Mg26', 'Fe54',
                     'Fe57', 'Ca44', 'Cl37', 'K41')
        col_names.extend(iso_names)
    if columns is not None:
        col_names.extend(columns)
    return df.drop(col_names, axis=1)

kegg2lipidmaps = kegg_2_lipidmaps()
hmdb2kegg = hmdb_2_kegg()
kegg2knapsack = kegg_2_knapsack()


if __name__ == "__main__":
    #### Run this section to create cache folder and necessary dictionary for convertion ####
    # Create local cache folders if they dont exist
    make_cache_dirs()
    # Get the most recent 'id' convertions or use local cache (if no internet for example)
    kegg2lipidmaps = kegg_2_lipidmaps()
    hmdb2kegg = hmdb_2_kegg()
    kegg2knapsack = kegg_2_knapsack()
    #########################################################################################

    file = 'test_files/masses.annotated.reformat.tsv'
    output = 'test_files/annotated.tsv'

    blacklist=[]
    with open('blacklist.txt', 'r') as f:
        x = f.read()
        x = x.split('\n')
        for y in x:
            blacklist.append(y)

    df = masstrix_tsv(file)
    df = cleanup_cols(df)
    progress = Progress(len(df['KEGG_cid']))
    df2 = df['KEGG_cid'].apply(annotate_cell)

    final_df = pd.concat([df, df2], axis=1, sort=False)

    final_df.to_csv(output, index=False, sep='\t')
