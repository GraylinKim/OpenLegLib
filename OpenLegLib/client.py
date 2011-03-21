import json
import urllib

from OpenLegLib.config import config
from OpenLegLib.search import OpenLegislationSearch
from OpenLegLib.utils import validate,fetch,OpenLegislationError

################################################################################
# OpenLegislation

class OpenLegClient(object):

    def __init__(self,mode='object',pagesize=20):
        self.configure(mode=mode,pagesize=pagesize)

    def configure(self,mode=None,pagesize=None):
        if mode: self.setMode(mode)
        if pagesize: self.setPagesize(pagesize)
        return self

    def bill(self,ID):
        return self.get(ID,'bill')

    def transcript(self,ID):
        return self.get(ID,'transcript')

    def meeting(self,committee,number,session):
        ID = 'meeting-%s-%i-%i' % (committee,number,session)
        return self.get(ID,'meeting')

    def calendar(self,caltype,number,session):
        number = ''.join('0' for i in range(0,5-len(str(number))))+str(number)

        ID = 'cal-%s-%s-%i' % (caltype, number, session)
        return self.get(ID,'calendar')

    def search(self,search=None):
        return OpenLegislationSearch(search,self.mode,self.pagesize)

    @validate('mode','in',config.modes,method=True)
    def setMode(self,mode):
        self.mode = mode
        return self

    @validate('pagesize','>',0,method=True)
    def setPagesize(self,pagesize):
        self.pagesize = pagesize
        return self

    @validate('otype','in',config.getTypes,method=True)
    def get(self,ID,otype):
        getId = urllib.quote(str(ID))
        mode = 'json' if self.mode == 'object' else self.mode
        request = fetch( config.url+'/'.join(['api/1.0',mode,otype,getId]) )
        response = request.read()
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
