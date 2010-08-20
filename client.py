import json
import urllib
from copy import deepcopy

from . import OpenLegislationError,fetch
from decorators import validate
from search import OpenLegislationSearch

#TODO: Make configuration a pass in

################################################################################
# OpenLegislation

class Client:

    def __init__(self,config,**options):
        config.__dict__.update(options)
        self.config = config
        self.__dict__.update(self.config.__dict__)
    
    def __getattr__(self,name):
        print self.__dict__.keys()
        if name not in self.getTypes:
            raise AttributeError(name)
            
        def func(self,ID):
            return self.get(name,ID)
            
        func.__name__ = name
        return func
   
    def search(self,search=None,**options):
        return OpenLegislationSearch(self.config,search,**options)
    
    def get(self,otype,ID):
        oid = urllib.quote(str(ID))
        format = 'json' if self.mode == 'object' else self.mode
        response = fetch( self.baseurl + self.getpath.format(format=format,otype=otype,oid=oid) ).read()
        if self.mode == 'object':
            return json.loads(response)[0]
        else:
            return response
                
################################################################################
# Test Code

if __name__ == '__main__':

    import pprint
    pp = pprint.PrettyPrinter(indent=2)

    OpenLegislation().transcript(1031)


    openleg = OpenLegislation(mode='json',pagesize=50)
    bill = openleg.bill('S66002')
    query = openleg.search()

    query2 = query.type('transcript').search("hello there")

    query3 = AND( query2, query.sessiontype('regular') )
    print urllib.unquote_plus(query3.url())
