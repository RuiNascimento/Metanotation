''' Get information from knapsack database if compound is already discribed in plants '''

import requests
from utilities import update_cache


def knapsack_plants(ks_id):
    ''' Check if conpound is in Plantae kingdom, also update local cache if necessary '''
    if update_cache('cache/knapsack/'+ks_id, days=30):
        ks_update(ks_id)
    with open('cache/knapsack/'+ks_id) as f:
        knapsack = f.read()
        f.close()
    if 'Plantae' in knapsack: return 'Plantae'
    else: return ''

def ks_update(ks_id):
    times = 0
    while times<3:
        try:
            f = requests.get('http://kanaya.naist.jp/knapsack_jsp/information.jsp?sname=C_ID&word=' + ks_id)
            # Testar se guarda o ficheiro
            with open('cache/knapsack/'+ks_id ,'wb') as file:
                file.write(f.content)
            break
        except:
            times+=1
            pass

# ### Test Area ###
# # knapsack wth Plantae
# ks_id = 'C00007223'
# # knapsack without Plantae
# ks_id = 'C00042391'
# knapsack_plants(ks_id)
