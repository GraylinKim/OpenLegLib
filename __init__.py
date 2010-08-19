import urllib2

# TODO: update/create documentation
# TODO: pull out lucene search mappings into a separate module

################################################################################
# Exceptions

class OpenLegislationError(Exception):
    """
    Exception raised when OpenLegislation classes or functions are given
    invalid input or are being used inappropriately.
    """
    
################################################################################
# Utilities

def fetch(url):

    request = urllib2.urlopen(url,timeout=5)
    if request.getcode() != 200:
        msg = 'Error Code: %i on request'
        raise OpenLegislationError(msg % request.getcode())
    return request

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

#Allow direct import from the package for all relevent items
from client import OpenLegislation
from search import OpenLegislationSearch,OpenLegislationSet,AND,OR,NOT
from models import Bill,Action,Legislator,Vote,Committee,Transcript,senators,committees
