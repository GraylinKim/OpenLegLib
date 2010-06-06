# -*- coding: utf-8 -*-
import urllib
import json
import copy
import re

_baseURL = 'http://open-staging.nysenate.gov/legislation'

def _fetch(url):
    request = urllib.urlopen(url)
    if request.getcode() != 200:
        msg = 'Error Code: %i on request'
        raise OpenLegislationError(msg % request.getcode())
    return request
    
_supportedGetTypes = set(['meeting','transcript','bill'])
_supportedSearchTypes = set(['bill','vote','action','transcript','meeting','calendar'])
_supportedModes = set(['html','xml','json','object'])
_supportedJoins = set(['AND','OR','NOT'])
_supportedVersions = [1.0]
    
class OpenLegislationError(Exception):
    """
    Exception raised when OpenLegislation classes or functions are given
    invalid input or are being used inappropriately.
    """
    
class OpenLegislation:
    """The client for interacting with the OpenLegislation API
    
    A default client can be created with an empty constructor
    
    .. doctest::
    
        >>>openleg = OpenLegislation()
        >>>[openleg.mode, openleg.pagesize, openleg.version]
        ['object', 20, 1.0]
    
    While the default settings for the client are generally recommended, you
    may decide you require different settings.
    
    .. doctest::
    
        >>>openleg = OpenLegislation(mode='json',pagesize=100,version=1.0)
        >>>[openleg.mode, openleg.pagesize, openleg.version]
        ['json', 100, 1.0]
    
    When invalid arguments are given, an OpenLegislationError will be thrown
    
    .. doctest::
    
        >>>OpenLegislation(mode='csv')
        Traceback (most recent call last):
            ...
        OpenLegislationError: Mode csv is not supported. Supported modes are set(['xml', 'json', 'html', 'object']).
        
    """
    
    def __init__(self,mode='object',pagesize=20,version=1.0):
        self.setVersion(version)
        self.setMode(mode)
        self.setPagesize(pagesize)
    
    def setMode(self,mode):
        """Sets the default format of data returned by queries
        
        Modes available are: html, xml, json, and object
        
        Object mode (the default) returns data in the form of a dictionary
        parsed from json data using the json.load from the core library.
        
        Usage:
        
        .. doctest::
        
            >>>openleg.setMode('json')
            >>>openleg.mode
            'json'
            
        When attempting to set an unsupported mode an exception will be thrown:
        
        .. doctest::
        
            >>>openleg.setMode('csv')
            Traceback (most recent call last):
                ...
            OpenLegislationError: Mode csv is not supported. Supported modes are set(['xml', 'json', 'html', 'object']).
            
        """
        if not mode.lower() in _supportedModes:
            msg = 'Mode %s is not supported. Supported modes are %s.'
            raise OpenLegislationError(msg % (mode,_supportedModes))
        self.mode = mode.lower()
        
    def setPagesize(self,pagesize):
        """Sets the default number of results returned on each page for searches
        
        This number must be a positive integer but (as far as I know) has no
        upper bounds (I've tried as high as 10,000). Higher numbers will lead
        to longer response time for many searches.
        
        .. doctest::
        
            >>>openleg.setPagesize(100)
            >>>openleg.pagesize
            100
        
        When attempting to set an invalid pagesize an exception will be thrown
        
        .. doctest::
        
            >>>openleg.setPagesize(-10)
            Traceback (most recent call last):
                ...
            OpenLegislationError: Invalid page size -10. Must be greater than zero.
            
        """
        if not pagesize>0:
            msg = 'Invalid page size %i. Must be greater than zero.'
            raise OpenLegislationError(msg % pagesize)
        self.pagesize = pagesize
    
    def setVersion(self,version):
        """Sets the default version of OpenLegislation for handling requests
        
        The only valid version number right now is 1.0. Just leave this as 
        default. If for some reason you try to set it yourself to something
        different (unsupported) an OpenLegislationError will be raised.
        
        .. doctest::
            
            >>>openleg.setVersion(2.0)
            Traceback (most recent call last):
                ...
            OpenLegislationError: Version 2.0 is not supported. Supported versions are [1.0].
            
        """
        if not float(version) in _supportedVersions:
            msg = 'Version %s is not supported. Supported versions are %s.'
            raise OpenLegislationError(msg % (version,_supportedVersions))
        self.version = str(version)
    
    def bill(self,ID):
        """Fills a request for data on a bill idenfied by its bill number.
        Returns the raw (or processed for object mode) data from the
        OpenLegislation server for the bill identified (by senate bill id).
        
        .. doctest::
            
            >>>openleg.bill('S66002')['title']
            u'Enacts into law major components of legislation necessary for the
            efficient operation of local governments; repealer'
            
        If there is an input error, (input is not a valid bill number), an
        OpenLegislationError is raised indicating a 500 error code was returned
        from the OpenLegislation server. Server errors will get their own type
        of exception in the future to separate server errors and library errors.
        
        .. doctest::
        
            >>>openleg.bill('S022')
            Traceback (most recent call last):
                ...
            OpenLegislationError: Error Code: 500 on request
            
        
        """
        return OpenLegislationGet(self.mode,ID,'bill',self.version).fetch()
        
    def transcript(self,ID):
        """Fills a request for transcript data identified by transcript number.
        Returns the raw (or processed for object mode) data from the 
        OpenLegislation server for the transcript requested.
        
        .. doctest::
        
            >>>openleg.transcript(297)['timestamp']
            u'Sun Feb 07 10:00:00 EST 2010'
            
        If there is an input error, (input is invalid transcript id), an
        OpenLegislationError is raised indicating a 500 error code was returned
        from the OpenLegislation server. Server errors will get their own type
        of exception in the future to separate server errors and library errors.
        
        .. doctest::
        
            >>>openleg.transcript(100)
            Traceback (most recent call last):
                ...
            OpenLegislationError: Error Code: 500 on request
        
        """
        return OpenLegislationGet(self.mode,ID,'transcript',self.version).fetch()        
        
    def search(self,search="",fulltext="",memo=""):
        """Creates an OpenLegislationSearch object for search requests by
        wrapping the supplied keywords in appropriate syntax. These keywords
        are processed by Lucene and can handle the following basic synatx:
        
        -   '*': Your basic wildcard. 'health*' will match healthcare, health, 
            and healthy
        -   '~': Fuzzy searching. Matches things similar to the word input
            #TODO: Find examples of fuzzy searching
        -   'AND','OR','NOT': Logical operators. e.g. 'health* NOT medicare'
            will find all results containing health* words but not pertaining to
            medicare.
        -   '()': Grouping. e.g. (health* NOT medicare) OR medicaid
        
        To search all fields of the bill use:
        
        .. testcode::
            
            >>>openleg.search("search text") #defaults to search
            
        To search the text of the bill only:
        
        .. testcode::
        
            >>>openleg.search(fulltext="search text")
            
        To search the memo of the bill only:
        
        .. testcode::
        
            >>>openleg.search(memo="search text")
            
        To search a combination of things combined by an OR
        
        .. testcode::
        
            >>>openleg.search(fulltext="health*",memo="dollars")
            
        The above code will search for health* in the full bill text OR dollars
        in the memo of the bill
        """
        fulltext = 'full:(%s)' % fulltext if fulltext else fulltext
        memo = 'memo:(%s)' % memo if memo else memo
        search = ' OR '.join(filter(lambda x: x!="",[search,memo,fulltext]))
        return OpenLegislationSearch(self.mode,search,self.pagesize,self.version)
    
class OpenLegislationGet():
    
    def __init__(self,mode,getId,getType,version=1.0):
        if not getType in _supportedGetTypes:
            msg = 'Invalid get type %s. Valid types are %s'
            raise OpenLegislationError(msg % (getType,_supportedGetTypes))
        self.__dict__.update(locals())
    
    def fetch(self):
        request = _fetch(self.url)
        if self.mode == 'object':
            return json.load(request)[0]
        else:
            return request.read()
            
    @property
    def url(self):
        mode = 'json' if self.mode == 'object' else self.mode
        getId = urllib.quote(str(self.getId))
        return '/'.join( [_baseURL,'api',self.version,mode,self.getType,getId] )

class OpenLegislationSearch():
    """The search request class for the OpenLegislation Library.
    
    Should not be instanciated outside of the OpenLegislation class. Instead,
    use the search method of the OpenLegislation class:
    
    .. doctest::
        
        >>>openleg.search('health*')
        <openleg.api.OpenLegislationSearch instance at 0xa1c2dcc>
        
    See :ref:`searching` for more details on using openleg.search(...)
    
    When searches are modified with filters and logical operations, new objects
    are created such that the original objects remain unchanged.
    """
    
    def __init__(self,mode,search="",pagesize=20,version=1.0):
        self.__dict__.update(locals())
        self.__dict__.update({
            'qsponsors':None,
            'qtypes':None,
            'qcommittees':None,
            'qlocations':list()
        })
        
    def fetch(self,page=1):
        """Retrieves a results page from OpenLegislation.
        
        Returns raw (processed when in object mode) data from the server
        """
        request = _fetch(self.url)
        if self.mode == 'object':
            return json.load(request)
        else:
            return request.read()
             
    @property
    def url(self,page=1):
        """The request URL, constructed from the search arguments provided"""
        if not page>0:
            msg = 'Invalid page number %i. Must be greater than zero.'
            raise OpenLegislationError(msg % page)
        if not set(self.qtypes if self.qtypes else []).issubset(_supportedSearchTypes):
            msg = "Invalid type %s. Valid types are %s."
            raise OpenLegislationError(msg % (self.qtypes,_supportedSearchTypes))
        mode = 'json' if self.mode == 'object' else self.mode

        return '/'.join([
            _baseURL,'search',
            '?'+'&'.join([
                key+'='+str(value) for key,value in {
                    'term':urllib.quote_plus(self._buildString()),
                    'pageIdx':page,
                    'pageSize':self.pagesize,
                    'format':mode
                }.iteritems()
            ]),
        ])
    
    def __getattr__(self,name):
        if name in ['type','committee','sponsor']:
            def stringFunc(value):
                return getattr(self,name+'s')([value])
            return stringFunc
        elif name in ['types','committees','sponsors']:
            def listFunc(values):
                new = copy.deepcopy(self)
                setattr(new,'q'+name,values)
                return new
            return listFunc
        raise AttributeError(name)

    def _buildString(self):
        """Builds the full search string from all specified options"""
        prefix = ""
        if self.qcommittees:
            committee = ' OR '.join(['committee:'+committee for committee in self.qcommittees])
            prefix = prefix+' AND '+committee if prefix else committee
        if self.qsponsors:
            sponsor = ' OR '.join(['sponsor:'+sponsor for sponsor in self.qsponsors])
            prefix = prefix+' AND '+sponsor if prefix else sponsor
        if self.qtypes:
            otypes = ' OR '.join(['otype:'+object for object in self.qtypes])
            prefix = prefix+' AND ('+otypes+')' if prefix else '('+otypes+')'
        if self.search:
            return prefix+' AND ('+self.search+')' if prefix else self.search
        else:
            return prefix
        
class OpenLegislationSet(OpenLegislationSearch):
    """Class returned by all logical operations (AND,OR,NOT). Behaves in an
    identical mannor to an OpenLegislationSearch object and gets its attribute
    values from the first Seach object passed to the operations.
    """
    def __init__(self,query1,query2,join):
        if not join in _supportedJoins:
           msg = "Invalid join %s. Valid joins are %s"
           raise OpenLegislationError(msg % (join,_supportedJoins))
        if not (isinstance(query1,OpenLegislationSearch) and isinstance(query2,OpenLegislationSearch)):
           msg = "%s(...) can only be performed on OpenLegislationSearch objects"
           raise OpenLegislationError(msg % join)
        self.__dict__.update(locals())
        
    def __getattr__(self,name):
        return getattr(self.query1,name)
    
    def _buildString(self):
        return (' '+self.join+' ').join([
            '('+x._buildString()+')' for x in [self.query1, self.query2]
        ])

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
    
if __name__ == '__main__':
    
    openLeg = OpenLegislation(mode='object')
    finds = [
        openLeg.bill('S66002'),
        openLeg.transcript(297),
    ]
    
    searches = [        
        openLeg.search('health*').type('bill').committee('AGING'),
        openLeg.search().committee('health'),
        NOT( openLeg.search(fulltext='medicare OR medicaid'),openLeg.search().committee('health') ),
    ]
    
    for query in searches:
        print urllib.unquote_plus(query.url)
