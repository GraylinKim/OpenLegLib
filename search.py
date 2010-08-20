import urllib
import json
from copy import deepcopy

from . import OpenLegislationError,fetch
from decorators import validate

################################################################################
# Search

def isiter(arg):
    try: return iter(arg) != None
    except TypeError: return false

class OpenLegislationSearch():

    def __init__(self,config,search=None,type=None,**options):
        config.__dict__.update(options.items())
        self.config = config
        
        self.otype = []
        self.options = dict()
        self.__dict__.update(self.config.__dict__)
        
        if type:
            self.type = type if (isiter(type) and not isinstance(type,basestring)) else [type]
            if set(self.type).issubset(set(self.filtermap.keys())):
                self.options['type']=' OR '.join(self.type)
            else:
                raise OpenLegislationError(self.type)
            
        if search: self.options['search']=search

    def fetch(self,page=1):
        request = fetch(self.url(page))
        if self.mode == 'object':
            return json.load(request)
        else:
            return request.read()
    
    def type(self,*args):
        if set(args).issubset(set(self.filtermap.keys())):
            new = deepcopy(self)
            new.options['type']=' OR '.join(args)
            new.otype = args
            return new
        else:
            raise OpenLegislationError(args)
    
    
    @validate('page','>',0,method=True)
    def url(self,page=1):
        """The request URL, constructed from the search arguments provided"""
        return self.baseurl + self.searchpath.format(
            query=urllib.quote_plus(self._buildString()),
            format= 'json' if self.mode == 'object' else self.mode)+''.join([
                '&'+key+'='+str(value) for key,value in {
                    'pageIdx':page,
                    'pageSize':self.pagesize,
                }.iteritems()])

    @property
    def filters(self):
        try:
            return set.union(*[set(self.filtermap[x]) for x in self.otype])
        except TypeError:
            return self.fields.keys()

    def __getattr__(self,name):
        if name in self.filters:
            def process(text):
                new = deepcopy(self)
                new.options[name] = text
                return new
            return process
        else:
            msg = "%s is not a valid filter for the current type(s): %s"
            raise AttributeError( msg % (name,', '.join(self.otype)) )

    def __deepcopy__(self,memo):
        new = OpenLegislationSearch(self.config,type=list(self.otype))
        new.options = dict(self.options)
        return new

    def _buildString(self):
        options = list()
        for alias,value in self.options.iteritems():
            options.append("%s:(%s)" % (self.fields[alias],value))
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

