import urllib2,urllib

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
    print urllib.unquote_plus(url)
    """
    request = urllib2.urlopen(url,timeout=5)
    if request.getcode() != 200:
        msg = 'Error Code: %i on request'
        raise OpenLegislationError(msg % request.getcode())
    return request
    """
    return open('/home/websites/nyss_floodlight/tester.py')

################################################################################
# Configuration

from v1_0 import v1_0
from v2_0 import v2_0

#Allow direct import from the package for all relevent items
from client import Client
#from search import OpenLegislationSearch,OpenLegislationSet,AND,OR,NOT
#from models import Bill,Action,Legislator,Vote,Committee,Transcript,senators,committees
