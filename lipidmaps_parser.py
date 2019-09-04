'''Get lipidmaps record from the internet or the local cache'''
import json
import requests
import os
from utilities import update_cache


def lipidmaps(id):
    # Check if file is in local cache and if it needs update
    if id in os.listdir('cache/lipidmaps/') and not update_cache('cache/lipidmaps/'+id, days=30) :
        #acrescentar um if para se o ficheiro estiver em branco, caso seja necessário no futuro
        with open('cache/lipidmaps/'+id) as lm:
            s = json.load(lm)
    else:
        times = 0
        while times<3:
            try:
                f = requests.get('http://www.lipidmaps.org/rest/compound/lm_id/' + id + '/all/json')
                # Testar se guarda o ficheiro
                with open('cache/lipidmaps/'+id ,'wb') as file:
                    file.write(f.content)
                s = json.loads(f.text)
                break
            except:
                times+=1
                pass

    if s == []:
        mm = 'null'
        cc = 'null'
        ss = 'null'
        tt = 'null'
        return (mm, cc, ss, tt)
    if s['core'] != None:
        mm = 'Lipids [LM]'
        cc = s['core']
    else:
        mm = 'Lipids [LM]'
        cc = 'null'
    if s['main_class'] != None:
        ss = s['main_class']
    else:
        ss = 'null'
    if 'sub_class' in s:
        if s['sub_class'] != None:
            tt = s['sub_class']
        else:
            tt = 'null'
    else:
            tt= 'null'
    return (mm, cc, ss, tt)
