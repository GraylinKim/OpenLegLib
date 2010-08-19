import pprint
pprint = pprint.PrettyPrinter(indent=2).pprint

import cPickle,sys,os
openlegdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append('/'.join(openlegdir.split('/')[:-1]))
from openleg import api

"""
for arg in sys.argv:
    if arg[:8] == "pagesize":
        pagesize = int(arg.split('=')[1])
"""

openleg = api.OpenLegislation(pagesize=100)
