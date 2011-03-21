import pprint

from OpenLegLib import Client
from OpenLegLib.search import AND

pp = pprint.PrettyPrinter(indent=2)

openleg = Client(mode='json',pagesize=50)
bill = openleg.bill('S66002')
query = openleg.search()

query2 = query.type('transcript').search("hello there")

query3 = AND( query2, query.sessiontype('regular') )
print urllib.unquote_plus(query3.url())
