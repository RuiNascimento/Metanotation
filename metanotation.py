'''
This file is not close to be done, just a place holder for the main script.
I'm working on the kegg_parser, lipidmaps_parser and common function first.
'''
import pandas as pd
import json
import re
from collections import namedtuple
from utilities import update_cache
from kegg_parser import Kegg
from lipidmaps_parser import lipidmaps

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
