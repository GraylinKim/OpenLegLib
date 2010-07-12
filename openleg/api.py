import copy
import urllib
import urllib2
import json

from objects import *
from decorators import *
from exceptions import *

################################################################################
# Configuration

class OpenLegislationConfiguration():

    url = 'http://open.nysenate.gov/legislation/'

    modes = ['html','xml','json','object']

    getTypes = ['bill','calendar','meeting','transcript']

    globalFilters = ['id','type','search','title','summary','modified']

    objectFilters = dict(
        action=['when','bill','sponsor','cosponsor'],
        bill=['sponsor','cosponsor','year','sameas','memo','fulltext','committee'],
        calendar=['ctype','when'],
        meeting=['committee','chair','location','notes','when'],
        transcript=['fulltext','when','location','sessiontype'],
        vote=['bill','committee','when','excused','abstain','aye','nay'],
        )

    fields = dict(
        id='oid',                     type='otype',
        search='osearch',             title='title',
        summary='summary',            modified='modified',
        sponsor='sponsor',            cosponsor='cosponsors',
        year='year',                  sameas='sameas',
        memo='memo',                  fulltext='full',
        committee='committee',        ctype='ctype',
        when='when',                  chair='chair',
        location='location',          notes='notes',
        sessiontype='session-type',   bill='billno',
        abstain='abstain',            excused='excused',
        aye='aye',                    nay='nay',
    )

    def __init__(self):
        self.filters = dict(
            [key, value+self.globalFilters]
            for key, value in self.objectFilters.items()
        )

config = OpenLegislationConfiguration()
################################################################################
# Utilities

def _fetch(url):

    request = urllib2.urlopen(url,timeout=5)
    if request.getcode() != 200:
        msg = 'Error Code: %i on request'
        raise OpenLegislationError(msg % request.getcode())
    return request

################################################################################
# OpenLegislation

class OpenLegislation:

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
        request = _fetch( config.url+'/'.join(['api/1.0',mode,otype,getId]) )
        response = request.read()
        if self.mode == 'object':
            return json.loads(response)[0]
        else:
            return response


################################################################################
# Search

class OpenLegislationSearch():

    def __init__(self,search=None,mode='object',pagesize=20):
        self.options = dict()
        self.mode=mode
        self.pagesize=pagesize
        self._type = []
        if search: self.options['search']=search

    def fetch(self,page=1):
        request = _fetch(self.url(page))
        if self.mode == 'object':
            return json.load(request)
        else:
            return request.read()

    @validate('*args','in',config.filters.keys(),method=True)
    def type(self,*args):
        new = copy.deepcopy(self)
        new.options['type']=' OR '.join(args)
        new._type = args
        return new

    @validate('page','>',0,method=True)
    def url(self,page=1):
        """The request URL, constructed from the search arguments provided"""
        return config.url+'search?' + '&'.join([
                key+'='+str(value) for key,value in {
                    'term':urllib.quote_plus(self._buildString()),
                    'pageIdx':page,
                    'pageSize':self.pagesize,
                    'format': 'json' if self.mode == 'object' else self.mode
                }.iteritems()])

    @property
    def filters(self):
        try:
            return set.union(*[set(config.filters[x]) for x in self._type])
        except TypeError:
            return config.fields.keys()

    def __getattr__(self,name):
        if name in self.filters:
            def process(text):
                new = copy.deepcopy(self)
                new.options[name] = text
                return new
            return process
        else:
            msg = "%s is not a valid filter for the current type(s): %s"
            raise AttributeError( msg % (name,', '.join(self._type)) )

    def __deepcopy__(self,memo):
        new = OpenLegislationSearch(mode=self.mode, pagesize=self.pagesize)
        new.options = dict(self.options)
        new._type = self._type
        return new

    def _buildString(self):
        options = list()
        for alias,value in self.options.iteritems():
            options.append("%s:(%s)" % (config.fields[alias],value))
        return ' AND '.join(options)

################################################################################
# Search Sets

class OpenLegislationSet(OpenLegislationSearch):
    """Class returned by all logical operations (AND,OR,NOT). Behaves in an
    identical mannor to an OpenLegislationSearch object and gets its attribute
    values from the first Seach object passed to the operations.
    """

    @validate('join','in',['AND','OR','NOT'],method=True)
    @validate('query1','instance',OpenLegislationSearch,method=True)
    @validate('query2','instance',OpenLegislationSearch,method=True)
    def __init__(self,query1,query2,join):
        self.__dict__.update(locals())

    def __getattr__(self,name):
        if name in ['pagesize','mode']:
            return getattr(self.query1,name)
        else:
            raise AttributeError("Invalid attribute %s" % name)

    def _buildString(self):
        return (' '+self.join+' ').join([
            '('+x._buildString()+')' for x in [self.query1,self.query2]
        ])


################################################################################
# Set Operators

def AND(q1,q2):
    """Returns a request representing the intersection of two result sets"""
    return OpenLegislationSet(q1,q2,'AND')

def OR(q1,q2):
    """Returns a request representing the union of the two result sets"""
    return OpenLegislationSet(q1,q2,'OR')

def NOT(q1,q2):
    """Returns a request representing the first result minus the items in
    the second result"""
    return OpenLegislationSet(q1,q2,'NOT')


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
