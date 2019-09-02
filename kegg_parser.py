'''Parse kegg record from local cache. To add an option to get new record from rest.kegg or update local cache if too old'''

import re
import requests
from collections import namedtuple
from utilities import update_cache

class Kegg:
    def __init__(self,kegg_id):
        self.name = kegg_id
        raw = []
        if update_cache('cache/kegg/'+kegg_id, days=30):
            self.update(self.name)
        with open('cache/kegg/'+self.name) as f:
            raw = f.readlines()
            f.close()
        self.raw = raw[:-1]
        splited = re.split(r'(^[A-Z_]+)',"".join(self.raw),flags = re.M)[1:]
        # Build the dictionary
        self.raw_dict = {}
        for x in range(0, len(splited)-1, 2):
            self.raw_dict[splited[x]] = splited[x+1]
        self.dict = {}
        self.classes = {}

    def update(self,kegg_id):
        times = 0
        while times<3:
            try:
                f = requests.get('http://rest.kegg.jp/get/' + kegg_id)
                # Testar se guarda o ficheiro
                with open('cache/kegg/'+kegg_id ,'wb') as file:
                    file.write(f.content)
                break
            except:
                times+=1
                pass

    #Functions for brite parsing
    LineData = namedtuple('LineData', 'indent text')
    def yield_linedata(self, text):
        yield self.LineData(indent=-1, text='')
        for line in text.split('\n'):
            if line.strip() != '':
                yield self.LineData(indent=len(line)-len(line.lstrip()), text=line.strip())
        yield self.LineData(indent=-1, text='')
    def create_dict(self, cur_ld, line_yielder):
        next_ld = next(line_yielder)
        if cur_ld.indent >= next_ld.indent:
            return cur_ld.text.split("  ")[0], next_ld
        d = {}
        while cur_ld.indent < next_ld.indent:
            d[next_ld.text], next_ld = self.create_dict(next_ld, line_yielder)
        return d, next_ld

    def parse(self):
        '''Parse all parameters from kegg (rest) raw file into self.dict'''
        try:
            self.dict['ENTRY'] = re.findall('^[A-Z0-9]+',self.raw_dict['ENTRY'].strip())[0]
        except KeyError:
            pass
        try:
            self.dict['NAME'] = re.split(r'\s\s+',self.raw_dict['NAME'].strip().replace(';',''))
        except KeyError:
            pass
        try:
            self.dict['FORMULA'] = self.raw_dict['FORMULA'].strip()
        except KeyError:
            pass
        try:
            self.dict['EXACT_MASS'] = self.raw_dict['EXACT_MASS'].strip()
        except KeyError:
            pass
        try:
            self.dict['MOL_WEIGHT'] = self.raw_dict['MOL_WEIGHT'].strip()
        except KeyError:
            pass
        try:
            self.dict['REMARK'] = self.raw_dict['REMARK'].strip()
        except KeyError:
            pass
        try:
            self.dict['REACTION'] = re.split(r'\s+',self.raw_dict['REACTION'])[1:-1]
        except KeyError:
            pass
        try:
            self.dict['PATHWAY'] = re.split(r'\s\s\s+',self.raw_dict['PATHWAY'].strip())
        except KeyError:
            pass
        try:
            self.dict['MODULE'] = re.split(r'\s\s\s+',self.raw_dict['MODULE'].strip())
        except KeyError:
            pass
        try:
            self.dict['ENZYME'] = re.split(r'\s+',self.raw_dict['ENZYME'])[1:-1]
        except KeyError:
            pass
        try:
            temp = re.split(r'\s\s+',self.raw_dict['DBLINKS'].strip())
            self.dict['DBLINKS'] = {}
            for iten in temp:
                self.dict['DBLINKS'][iten.split(" ")[0]] = iten.split(" ")[1]
        except KeyError:
            pass
        try:
            self.dict['ATOM'] = re.split(r'\s\s\s\s\s\s+',self.raw_dict['ATOM'].strip())
        except KeyError:
            pass
        try:
            self.dict['BOND'] = re.split(r'\s\s\s\s\s\s+',self.raw_dict['BOND'].strip())
        except KeyError:
            pass

        if 'Brite' in self.raw_dict.keys():
            #############BRITE PARSER####################
            # Remove excess identantion from orifinal brite file, and prep string for recursive operation
            brite = ('     '+self.raw_dict['BRITE']).splitlines()
            new_brite = []
            for line in brite:
                new_brite.append(line.split('            ')[1])
            str = "\n".join(new_brite)
            # Get brite recursively
            line_yielder = self.yield_linedata(str)
            cur_ld = next(line_yielder)
            result, next_line = self.create_dict(cur_ld, line_yielder)
            self.dict['BRITE'] = result

    def brite(self, verbose=False):
        '''
        Parse only brite parameter
        verbose - True/False, if True returns the BRITE as a nested dictionary, default False (only parse result into self.dict)
        '''
        if 'BRITE' in self.raw_dict.keys():
            #############BRITE PARSER####################
            # Remove excess identantion from orifinal brite file, and prep string for recursive operation
            brite = ('     '+self.raw_dict['BRITE']).splitlines()
            new_brite = []
            for line in brite:
                new_brite.append(line.split('            ')[1])
            str = "\n".join(new_brite)
            # Get brite recursively
            line_yielder = self.yield_linedata(str)
            cur_ld = next(line_yielder)
            result, next_line = self.create_dict(cur_ld, line_yielder)
            self.dict['BRITE'] = result
        if verbose:
            return self.dict['BRITE']

    def get_classes(self):
        '''
        Get Major class (MC), Class (C) and Secondary Class (SC) from Kegg BRITE
        Return a tuple of lists with the result (MC, C, SC) if exists
        '''
        if 'BRITE' in self.raw_dict.keys():
            if 'BRITE' not in self.dict.keys():
                self.brite()
            k1=[]
            k2=[]
            k3=[]
            for key in self.dict['BRITE']:
                k1.append(key)
                for key2 in self.dict['BRITE'][key]:
                    k2.append(key2)
                    for key3 in self.dict['BRITE'][key][key2]:
                        k3.append(key3)
            self.classes['k1'] = k1
            self.classes['k2'] = k2
            self.classes['k3'] = k3
            return (k1,k2,k3)
        return ('','','')


# ############## test area 2 ##############
# C00044 = Kegg('C00044')
# if 'BRITE' in C00044.raw_dict.keys():
#     print(True)
# C00044.dict.keys()
#
# C00044.brite(verbose=True)
# C00044.get_classes()
# C00044.dict
# C00044.classes





###### TEST AREA ######

# C00033 = Kegg('C00033')
# C00033.name
# Kegg.parse(C00033)
# C00033.dict['ATOM']
# Kegg.get_classes(C00033)
# C00033.classes['k1']

############ ORIGINAL CODE #############

# # Test kegg id
# kegg_cid = "C00033"
# # kegg_cid = "C05571"
#
# # Directory location
# kegg_compounds = "kegg/compounds/"
# lipidmaps = "kegg/lipidmaps"
#
# # Get raw data from file
# def kegg_parser(cid):
#     raw = []
#     with open(kegg_compounds+cid) as f:
#         raw = f.readlines()
#         f.close()
#     raw
#     return raw[:-1]
#
# # Get raw data in a list, one entry per line
# parsed = kegg_parser(kegg_cid)
#
# # Split string by lines that start with a letter [A-Z], also supports MULTILINE (re.M)
# splited = re.split(r'(^[A-Z_]+)',"".join(parsed),flags = re.M)[1:]
#
# # Build the dictionary
# test_dict = {}
# for x in range(0, len(splited)-1, 2):
#     test_dict[splited[x]] = splited[x+1]
#
# # Clean entries from the rest.kegg.jp compound page
# test_dict['ENTRY'] = re.findall('^[A-Z0-9]+',test_dict['ENTRY'].strip())[0]
# test_dict['NAME'] = re.split(r'\s\s+',test_dict['NAME'].strip().replace(';',''))
# test_dict['FORMULA'] = test_dict['FORMULA'].strip()
# test_dict['EXACT_MASS'] = test_dict['EXACT_MASS'].strip()
# test_dict['MOL_WEIGHT'] = test_dict['MOL_WEIGHT'].strip()
# test_dict['REMARK'] = test_dict['REMARK'].strip()
# test_dict['REACTION'] = re.split(r'\s+',test_dict['REACTION'])[1:-1]
# test_dict['PATHWAY'] = re.split(r'\s\s\s+',test_dict['PATHWAY'].strip())
# test_dict['MODULE'] = re.split(r'\s\s\s+',test_dict['MODULE'].strip())
# test_dict['ENZYME'] = re.split(r'\s+',test_dict['ENZYME'])[1:-1]
# # Brite its a bit more complex, brite parser its down bellow
# test_dict['DBLINKS'] = re.split(r'\s\s+',test_dict['DBLINKS'].strip())
# test_dict['ATOM'] = re.split(r'\s\s\s\s\s\s+',test_dict['ATOM'].strip())
# test_dict['BOND'] = re.split(r'\s\s\s\s\s\s+',test_dict['BOND'].strip())
#
# #############BRITE PARSER####################
# # Remove excess identantion from orifinal brite file, and prep string for recursive operation
# brite = ('     '+test_dict['BRITE']).splitlines()
# new_brite = []
# for line in brite:
#     new_brite.append(line.split('            ')[1])
# str = "\n".join(new_brite)
#
# # Build a dictionary with recursion
# # Ty stackoverflow user zehnpaard, addapted from http://stackoverflow.com/revisions/33207024/3
# # from collections import namedtuple
# LineData = namedtuple('LineData', 'indent text')
# def yield_linedata(text):
#     yield LineData(indent=-1, text='')
#     for line in text.split('\n'):
#         if line.strip() != '':
#             yield LineData(indent=len(line)-len(line.lstrip()), text=line.strip())
#     yield LineData(indent=-1, text='')
# def create_dict(cur_ld, line_yielder):
#     next_ld = next(line_yielder)
#     if cur_ld.indent >= next_ld.indent:
#         return cur_ld.text.split("  ")[0], next_ld
#     d = {}
#     while cur_ld.indent < next_ld.indent:
#         d[next_ld.text], next_ld = create_dict(next_ld, line_yielder)
#     return d, next_ld
# line_yielder = yield_linedata(str)
# cur_ld = next(line_yielder)
# result, next_line = create_dict(cur_ld, line_yielder)
#
# #Add the recursive-build nested dictionary to the main dictionary
# test_dict['BRITE'] = result
#
# #keys from identation levels 1, 2 and 3 after BRITE
# k1=[]
# k2=[]
# k3=[]
# for key in test_dict['BRITE']:
#     k1.append(key)
#     for key2 in test_dict['BRITE'][key]:
#         k2.append(key2)
#         for key3 in test_dict['BRITE'][key][key2]:
#             k3.append(key3)
