import os
from datetime import datetime, timedelta

def update_cache(path, days=30):
    date_limit = datetime.now() - timedelta(days=days)
    file_date = datetime.fromtimestamp(os.path.getmtime(path))
    if file_date < date_limit:
        return True
    else:
        return False

class Progress:
    """A progress reporter of % done for a maximum (int) of self.total
    Define total when calling progress, e.g. progress = Progress(total=len(df['raw_mass']))
    Parameters:
        total - (int) maximum/total
    """
    def __init__(self, total=1):
        self.count = 0
        self.total = total
    def tick(self):
        self.count +=1
        print(str(round((1-((self.total-self.count)/self.total))*100)) + "% done")
    def reset(self):
        self.count = 0
