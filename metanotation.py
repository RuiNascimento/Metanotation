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
import requests

kegg2lipidmaps = kegg_2_lipidmaps()
hmdb2kegg = hmdb_2_kegg()
kegg2knapsack = kegg_2_knapsack()

kegg2knapsack['C10861']

ks_id = 'C00007223'
r = requests.post('http://kanaya.naist.jp/knapsack_jsp/information.jsp?sname=C_ID&word=' + ks_id)
    if 'Plantae' in r.text:
        print ('Plantae')

def kegg_2_lipidmaps():
    r = requests.get('http://rest.genome.jp/link/lipidmaps/cpd')
    d = {}
    for line in r.text.splitlines():
        if len(line) == 0:
            continue
        cpd, lipidmaps, equiv = line.split('\t')
        lipidmaps = lipidmaps.split(':')[1].strip()
        cpd = cpd.split(':')[1].strip()
        d[cpd] = lipidmaps
    return d

def hmdb_2_kegg():
    r = requests.get('http://rest.genome.jp/link/hmdb/cpd')
    d = {}
    for line in r.text.splitlines():
        if len(line) == 0:
            continue
        cpd, hmdb, equiv = line.split('\t')
        hmdb = hmdb.split(':')[1].strip()
        cpd = cpd.split(':')[1].strip()
        d[cpd] = hmdb
    return d

def kegg_2_knapsack():
    r = requests.get('http://rest.genome.jp/link/knapsack/cpd')
    d = {}
    for line in r.text.splitlines():
        if len(line) == 0:
            continue
        cpd, knapsack, equiv = line.split('\t')
        knapsack = knapsack.split(':')[1].strip()
        cpd = cpd.split(':')[1].strip()
        d[cpd] = knapsack
    return d

# Function to check id convertion and choose the appropriate id for annotation
def annotate(id):
    if id.startswith('C'):
        # if id in kegg2lipidmaps
        #   return(lipidmaps(kegg2lipidmaps[CXXXXXX]))
        # else:
        #   return Kegg(id).get_classes()
        pass
    elif id.startswith('H'):
        # if id in HMDB2Kegg
        #   return(Kegg(HMDB2kegg[CXXXXXX]).get_classes)
        # else:
        #   pass
        pass
    elif id.startswith('L'):
        return(lipidmaps(id))

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


C00050 = Kegg('C00050')

C00050.parse()
C00050.get_classes()

C00050.dict

C00050.dict['DBLINKS']
