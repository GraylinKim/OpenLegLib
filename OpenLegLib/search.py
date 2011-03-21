import copy, urllib, json

from OpenLegLib.config import config
from OpenLegLib.utils import validate,fetch

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
        request = fetch(self.url(page))
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

