'''
This file is not close to be done, just a place holder for the main script.
I'm working on the kegg_parser, lipidmaps_parser and common function first.
'''
import os
import pandas as pd
import json
import re
from collections import namedtuple
from utilities import update_cache
from kegg_parser import Kegg
from lipidmaps_parser import lipidmaps
from knapsack_parser import knapsack_plants
import requests


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
    MC, C, SC, KS = '','','',''
    if id.startswith('C'):
        if id in kegg2knapsack:
            KS = knapsack_plants(id)
        if id in kegg2lipidmaps:
          MC, C, SC, TC = lipidmaps(kegg2lipidmaps[id])
        else:
          MC, C, SC = Kegg(id).get_classes()
    elif id.startswith('H'):
        if id in hmdb2kegg:
          MC, C, SC = (Kegg(hmdb2kegg[id]).get_classes())
        else:
          pass
    elif id.startswith('L'):
        MC, C, SC, TC = lipidmaps(id)
    return (MC, C, SC, KS)


annotate('HMDB02111')

# Run in main script!
# Get the most recent 'id' convertions or use local cache (if no internet for example)
kegg2lipidmaps = kegg_2_lipidmaps()
hmdb2kegg = hmdb_2_kegg()
kegg2knapsack = kegg_2_knapsack()

# check if update is necessary for local cache
update_cache('cache/kegg/C00033', days=30)

file = pd.read_excel("test_files/positive.xlsx")
file.head(20)
test = file.KEGG_cid[3]
test
test = list(test.split("#"))
test


for id in test:
    if id.startswith('C'):
        id = Kegg(id)
        print(id.name)
        id.get_classes()
        print(id.dict)

id = Kegg('C14175')
id.parse()
id.get_classes()
id.dict


C00050 = Kegg('C00044')

C00050.parse()
C00050.get_classes()
a, b, c = C00050.get_classes()
"#".join(set(a))

C00050.dict

C00050.dict['DBLINKS']
