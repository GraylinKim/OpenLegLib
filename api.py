# -*- coding: utf-8 -*-
import urllib
import re

class OpenLegislation:
    
    #Note: Calendars are not supported because they are not yet stable
    supportedGetTypes = set(['meeting','transcript','bill'])
    supportedSearchTypes = set(['bill','vote','action','transcript','meeting','calendar'])
    supportedModes = set(['html','xml','csv','json','object'])
    supportedVersions = [1.0]
    objectDataType = 'json'
    
    def __init__(self,version='1.0',mode='json',pagesize=20):
        """Provide defaults for ease of use"""
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
        
    def search(self,string="",types=[],sponsor=None,committee=None):
        return OpenLegislationQuery('search',self.mode,string,types,sponsor,committee,self.pagesize,self.version)
        
    def searchFullText(self,string="",types=[],sponsor=None,committee=None):
        string = 'full:('+string+')'
        return OpenLegislationQuery('search',self.mode,string,types,sponsor,committee,self.pagesize,self.version)
    
    def searchMemo(self,string="",types=[],sponsor=None,committee=None):
        string = 'memo:('+string+')'
        return OpenLegislationQuery('search',self.mode,string,types,sponsor,committee,self.pagesize,self.version)
    
    def setPageSize(self,pagesize):
        """Assert Valid Page size before setting"""
        assert pagesize>0 and pagesize<100,'Pagesize ('+str(pagesize)+') must be between 1 and 100'
        self.pagesize = pagesize
    
    def setMode(self,mode):
        """Assert supported mode before setting"""
        assert mode.lower() in self.supportedModes,'Mode '+mode+' is not supported'
        self.mode = mode.lower()
        
    def setVersion(self,version):
        """Assert supported version before setting"""
        assert float(version) in self.supportedVersions,'Version '+str(version)+' is not supported'
        self.version = version.lower()

class OpenLegislationQueryBase:
    
    baseURL = 'http://open-staging.nysenate.gov/legislation'
    supportedGetTypes = set(['meeting','transcript','bill'])
    supportedSearchTypes = set(['bill','vote','action','transcript','meeting','calendar'])
    
    def fetch(page=1):
        request = urllib.urlopen(self.url(page))
        assert request.getcode() == 200, 'Error Code '+str(request.getcode())
        
        data = request.read()
        if name == 'object':
            return data
        else:
            return data
    
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
            return '/'.join( [self.baseURL,'search','?'+args] )
            
        elif self.qtype == 'get':    
            string = urllib.quote_plus(self.string)
            return '/'.join( [self.baseURL,'api',self.version,mode,self.type,string] )
        
class OpenLegislationQuerySet(OpenLegislationQueryBase):

    def __init__(self,query1,query2,join):
        assert query1.qtype == 'search', "only search queries can be joined"
        assert query2.qtype == 'search', "only search queries can be joined"
        self.query1 = query1
        self.query2 = query2
        self.join = join
        
    def __getattr__(self,name):
        return getattr(self.query1,name)
    
    def _buildString(self):
        halves = ['('+x._buildString()+')' for x in [self.query1, self.query2]]
        return (' '+self.join+' ').join(halves)

class OpenLegislationQuery(OpenLegislationQueryBase):
    
    def __init__(self,qtype,mode,string="",types=[],sponsor=None,committee=None,pagesize=20,version=1.0):
        qtype = qtype.lower()
        assert qtype=='get' or qtype=='search',"Invalid query type ("+qtype+"). Use 'get' or 'set'"
        assert qtype=='search' or not types==[],"Get requests must have a type specified"
        
        self.qtype = qtype
        self.string = str(string)
        self.type = str(types) if qtype == 'get' else set(types)
        self.sponsor = sponsor
        self.committee = committee
        self.pagesize = pagesize
        self.version = version
        self.mode = mode
        
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
            return self.string if not prefix else prefix+' AND ('+self.string+')'
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
