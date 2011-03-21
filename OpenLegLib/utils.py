################################################################################
# Exceptions

class OpenLegislationError(Exception):
    """
    Exception raised when OpenLegislation classes or functions are given
    invalid input or are being used inappropriately.
    """
    
################################################################################
# Utility Functions

import urllib2

def fetch(url):
    print url
    request = urllib2.urlopen(url,timeout=5)
    if request.getcode() != 200:
        msg = 'Error Code: %i on request'
        raise OpenLegislationError(msg % request.getcode())
    return request

#I find myself often requiring data returned converted with defaults
def getType(d,key,type,default=None):
    return type(d.get(key,default)) if d.get(key,default) else default


################################################################################
# Decorators

import inspect
from decorator import decorator

def validate(arg,op,valid,method=False):

    operations = {
        '>': ( lambda x: x > valid, " %s must be > %s" % (arg,valid) ),
        'in': ( lambda x: x in valid, " %s must be in %s" % (arg,valid) ),
        'instance': ( lambda x: isinstance(x,valid), " %s must be instance of %s " % (arg,valid) )
    }

    try:
        (validator,errormsg) = operations[op]
    except KeyError:
        msg = "Invalid method %s. Value methods are %s"
        raise ValueError( msg % (op,operation.keys()) )

    @decorator
    def wrapper(func,*args,**kwargs):
        if method:
            self = args[0]
            args = args[1:] #remove 'self'

        #Validate differently for each arg type
        argspec = inspect.getargspec(func)
        if argspec.varargs and arg == '*'+argspec.varargs:
            for value in args:
                if not validator(value):
                    msg = "Invalid value %s for %s. %s"
                    raise ValueError( msg % (value,arg,errormsg) )
        elif argspec.keywords and arg == '**'+argspec.keywords:
            for key,value in kwargs.iteritems():
                if not validator(value):
                    msg = "Invalid value %s for keyword %s. %s"
                    raise ValueError( msg % (value,arg,errormsg) )
        elif argspec.args and arg in argspec.args:
            if method:
                value = args[argspec.args.index(arg)-1]
            else:
                value = args[argspec.args.index(arg)]

            if not validator(value):
                msg = "Invalid value %s for %s. %s"
                raise ValueError( msg % (value,arg,errormsg) )
        else:
            raise ValueError("Invalid arg value %s in validate(...)." % arg)

        if method:
            return func(self,*args,**kwargs)
        else:
            return func(*args,**kwargs)

    return wrapper
