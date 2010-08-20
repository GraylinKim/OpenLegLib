class v2_0_Configuration(object):
    
    def __init__(self):
        
        self.mode = 'json'
        
        self.pagesize = 20
        
        #Root access URL
        self.baseurl = 'http://open.nysenate.gov/legislation'
        
        #Path (appended to baseurl) for get requests
        self.getpath = '/2.0/{otype}/{oid}.{format}'
        
        #Path (appended to baseurl) for search requests
        self.searchpath = '/search.{format}?term={query}'
        
        #The available data dump modes
        self.modes = ['html','xml','json','object']
        
        #The object types available through the get API
        self.getTypes = ['bill','calendar','meeting','transcript']
        
        #List the filters available to all objects
        self.globalFilters = ['id','type','search','title','summary','modified']
        
        #Map different available search filters to their corresponding objects
        self.objectFilters = dict(
                action=['when','bill','sponsor','cosponsor'],
                bill=['sponsor','cosponsor','year','sameas','memo','fulltext','committee'],
                calendar=['ctype','when'],
                meeting=['committee','chair','location','notes','when'],
                transcript=['fulltext','when','location','sessiontype'],
                vote=['bill','committee','when','excused','abstain','aye','nay'],
            )
        
        #Map the open legislation names to more friendly names for internal use
        self.fields = dict(
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
            
        #Combine the global and object filters to get an overall filters dict
        self.filtermap = dict(
            [key, value+self.globalFilters]
            for key, value in self.objectFilters.items()
        )
    
#The config file to be used for the Client and the Search Object
v2_0 = v2_0_Configuration()
