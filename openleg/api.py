# -*- coding: utf-8 -*-
import urllib
import json
import re

_supportedGetTypes = set(['meeting','transcript','bill'])
_supportedSearchTypes = set(['bill','vote','action','transcript','meeting','calendar'])
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
    
    def bill(self,billId):
        return OpenLegislationQuery('get',self.mode,billId,'bill',None,None,self.pagesize,self.version)
        
    def meeting(self,committee,number,session):
        assert number>0, 'Meeting number must be natural number (integer > 0)'
        assert re.match('\d{4}-\d{4}',session), 'Invalid session '+str(session)
        meetingid = '-'.join(['meeting',str(committee),str(number),str(session)])
        return OpenLegislationQuery('get',self.mode,meetingid,'meeting',None,None,self.pagesize,self.version)
        
    def transcript(self,transcriptId):
        return OpenLegislationQuery('get',self.mode,transcriptId,'transcript',None,None,self.pagesize,self.version)
        
    def search(self,search="",types=[],sponsor=None,committee=None):
        return OpenLegislationQuery('search',self.mode,search,types,sponsor,committee,self.pagesize,self.version)
        
    def searchFullText(self,search="",types=[],sponsor=None,committee=None):
        return OpenLegislationQuery('search',self.mode,'full:('+search+')',types,sponsor,committee,self.pagesize,self.version)
    
    def searchMemo(self,search="",types=[],sponsor=None,committee=None):
        return OpenLegislationQuery('search',self.mode,'memo:('+search+')',types,sponsor,committee,self.pagesize,self.version)
    
    def setPageSize(self,pagesize):
        if pagesize<=0:
            msg = 'Pagesize (%i) must be positive natural numbers.'
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

class OpenLegislationQueryBase:
    
    def fetch(self,page=1):
        request = urllib.urlopen(self.url(page))
        if request.getcode() != 200:
            msg = 'Error Code: %i on request'
            raise OpenLegislationError(msg % request.getcode())
        
        if self.mode == 'object':
            return json.load(request)[0]
        else:
            return request.read()
    
    def AND(self,query2):
        return OpenLegislationQuerySet(self,query2,'AND')
        
    def OR(self,query2):
        return OpenLegislationQuerySet(self,query2,'OR')
        
    def NOT(self,query2):
        return OpenLegislationQuerySet(self,query2,'NOT')
    
    def url(self,page=1):
        #Adjust mode when objects are being returned
        mode = 'json' if self.mode == 'object' else self.mode
        assert page>0, 'Page number must be greater than zero'
        
        if self.qtype == 'search':
            term = self._buildString()
            args = '&'.join([
                key+'='+str(value) for key,value in {
                    'term':urllib.quote_plus(term),
                    'pageIdx':page,
                    'pageSize':self.pagesize,
                    'format':mode
                }.iteritems()
            ])
            return '/'.join( [_baseURL,'search','?'+args] )
            
        elif self.qtype == 'get':    
            string = urllib.quote_plus(self.string)
            return '/'.join( [_baseURL,'api',self.version,mode,self.type,string] )
        
class OpenLegislationQuerySet(OpenLegislationQueryBase):

    def __init__(self,query1,query2,join):
        if query1.qtype != 'search' or query1.qtype != 'search':
            msg = "Cannot join a %s and a %s query. Only searches can be joined"
            raise OpenLegislationError(msg % (query1.qtype,query2.qtype))
        self.__dict__.update(locals())
        
    def __getattr__(self,name):
        return getattr(self.query1,name)
    
    def _buildString(self):
        return (' '+self.join+' ').join([
            '('+x._buildString()+')' for x in [self.query1, self.query2]
        ])

class OpenLegislationQuery(OpenLegislationQueryBase):
    
    def __init__(self,qtype,mode,string="",types=[],sponsor=None,committee=None,pagesize=20,version=1.0):
        qtype = qtype.lower()
        string = str(string)
        assert qtype=='get' or qtype=='search',"Invalid query type ("+qtype+"). Use 'get' or 'set'"
        assert qtype=='search' or not types==[],"Get requests must have a type specified"
        self.type = str(types) if qtype == 'get' else set(types)
        self.__dict__.update(locals())
        
    def _buildString(self):
        """Builds the full search string from all specified options"""
        if self.qtype == 'get':
            return self.string
            
        prefix = ""
        if self.committee:
            committee = 'committee:'+self.committee
            prefix = prefix+' AND '+committee if prefix else committee
        if self.sponsor:
            sponsor = 'sponsor:'+self.sponsor
            prefix = prefix+' AND '+sponsor if prefix else sponsor
        if self.type:
            otypes = ' OR '.join(['otype:'+object for object in self.type])
            prefix = prefix+' AND ('+otypes+')' if prefix else '('+otypes+')'
        if self.string:
            return prefix+' AND ('+self.string+')' if prefix else self.string
        else:
            return prefix


if __name__ == '__main__':
    
    openLeg = OpenLegislation()
    queries = [
        openLeg.bill('S66002'),
        openLeg.meeting('AGING',11,'2009-2010'),
        openLeg.transcript(350),
        openLeg.search('health*',types=['bill'],committee='AGING'),
        openLeg.search(committee='health'),
        openLeg.searchFullText('medicare OR medicaid').NOT(openLeg.search(committee='health')),
    ]
    
    for query in queries:
        print urllib.unquote_plus(query.url())
