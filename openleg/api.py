# -*- coding: utf-8 -*-
import urllib
import json
import re

_supportedGetTypes = set(['meeting','transcript','bill'])
_supportedSearchTypes = set(['bill','vote','action','transcript',
                             'meeting','calendar'])
_supportedModes = set(['html','xml','csv','json','object'])
_supportedVersions = [1.0]
_baseURL = 'http://open-staging.nysenate.gov/legislation'

class OpenLegislationError(Exception):
    pass
    
class OpenLegislation:
    
    def __init__(self,version='1.0',mode='object',pagesize=20):
        self.setVersion(version)
        self.setMode(mode)
        self.setPageSize(pagesize)
    
    def setPageSize(self,pagesize):
        if not pagesize>0:
            msg = 'Invalid page size %i. Must be greater than zero.'
            raise OpenLegislationError(msg % pagesize)
            
        self.pagesize = pagesize
    
    def setMode(self,mode):
        if not mode.lower() in _supportedModes:
            msg = 'Mode %s is not supported. Supported modes are %s.'
            raise OpenLegislationError(msg % (mode,_supportedModes))
            
        self.mode = mode.lower()
        
    def setVersion(self,version):
        if not float(version) in _supportedVersions:
            msg = 'Version %s is not supported. Supported versions are %s.'
            raise OpenLegislationError(msg % (version,_supportedVersions))
            
        self.version = version.lower()
    
    def bill(self,bill):
        return OpenLegislationFind(
            self.mode,bill,'bill',self.version
        )
        
    def transcript(self,transcript):
        return OpenLegislationFind(
            self.mode,transcript,'transcript',self.version
        )
        
    def meeting(self,committee,number,session):
        if not number>0:
            msg = 'Invalid meeting number %i. Must be greater than zero.'
            raise OpenLegislationError(msg % number)
        if not re.match('\d{4}',session):
            msg = 'Invalid session %s. Must match ####.'
            raise OpenLegislationError(msg % number)
            
        meeting = '-'.join(['meeting',str(committee),str(number),str(session)])
        return OpenLegislationFind(
            self.mode,meeting,'meeting',self.version
        )
        
    def search(self,search="",fulltext="",memo=""):
        fulltext = 'full:(%s)' % fulltext if fulltext else fulltext
        memo = 'memo:(%s)' % memo if memo else memo
        search = ' OR '.join(filter(lambda x: x!="",[search,memo,fulltext]))
        return OpenLegislationSearch(self.mode,search,self.pagesize,self.version)

class OpenLegislationBase:
    
    def fetch(self,page=1):
        request = urllib.urlopen(self.url(page))
        if request.getcode() != 200:
            msg = 'Error Code: %i on request'
            raise OpenLegislationError(msg % request.getcode())
        
        if self.mode == 'object':
            data = json.load(request)
            return data[0] if len(data)==0 else data
        else:
            return request.read()

class OpenLegislationFind(OpenLegislationBase):
    
    def __init__(self,mode,objid,objtype,version=1.0):
        if not objtype in _supportedGetTypes:
            msg = 'Invalid get type %s. Valid types are %s'
            raise OpenLegislationError(msg % (objtype,_supportedGetTypes))
            
        self.__dict__.update(locals())
    
    def url(self,page=1):
        if not page>0:
            msg = 'Invalid page number %i. Must be greater than zero.'
            raise OpenLegislationError(msg % page)            
        mode = 'json' if self.mode == 'object' else self.mode
        
        objid = urllib.quote_plus(str(self.objid))
        return '/'.join( [_baseURL,'api',self.version,mode,self.objtype,objid] )

class OpenLegislationSearch(OpenLegislationBase):
    
    def __init__(self,mode,search="",pagesize=20,version=1.0):
        self.__dict__.update(locals())
        self.__dict__.update({
            'qsponsors':None,
            'qtypes':None,
            'qcommittees':None,
            'qlocations':list()
        })
        
    def url(self,page=1):
        if not page>0:
            msg = 'Invalid page number %i. Must be greater than zero.'
            raise OpenLegislationError(msg % page)
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
        
    def AND(self,query2):
        return OpenLegislationSet(self,query2,'AND')
        
    def OR(self,query2):
        return OpenLegislationSet(self,query2,'OR')
        
    def NOT(self,query2):
        return OpenLegislationSet(self,query2,'NOT')
    
    def type(self,type):
        return self.types([type])
    def types(self,types):
        if not set(types).issubset(_supportedSearchTypes):
            msg = "Invalid type %s. Valid types are %s."
            raise OpenLegislationError(msg % (types,_supportedSearchTypes))
        self.qtypes = types
        return self
        
    def committee(self,committee):
        return self.committees([committee])
    def committees(self,committees):
        self.qcommittees = committees
        return self
        
    def sponsor(self,sponsor):
        self.sponsors([sponsor])
    def sponsors(self,sponsors):
        self.qsponsors = sponsors
        return self
        
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

    def __init__(self,query1,query2,join):
        self.__dict__.update(locals())
        
    def __getattr__(self,name):
        return getattr(self.query1,name)
    
    def _buildString(self):
        return (' '+self.join+' ').join([
            '('+x._buildString()+')' for x in [self.query1, self.query2]
        ])

if __name__ == '__main__':
    
    openLeg = OpenLegislation(mode='object')
    
    queries = [
        openLeg.bill('S66002'),
        #openLeg.meeting('AGING',11,'2009-2010'),
        openLeg.transcript(297),
        
        openLeg.search('health*').type('bill').committee('AGING'),
        openLeg.search().committee('health'),
        openLeg.search(fulltext='medicare OR medicaid').NOT(openLeg.search().committee('health')),
    ]
    
    for query in queries:
        print urllib.unquote_plus(query.url())
