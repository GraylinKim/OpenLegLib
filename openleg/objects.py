from datetime import date

#I find myself often requiring data returned converted with defaults
def getType(d,key,type,default=None):
    return type(d.get(key,default)) if d.get(key,default) else default

################################################################################

class Bill():
    def __init__(self,d):

        self.year = getType(d,'year',int)

        #More complications due to different names in different places
        self.id = getType(d, 'senateId', str) if 'senateId' in d else getType(d, 'id', str)

        self.title = getType(d, 'title', str)
        self.summary = getType(d, 'summary', str)
        self.sponsor = getType(d, 'sponsor', str)
        self.votes = [Vote(vote, billno=self.senateId) for vote in d.get('votes', [])]
        self.actions = sorted([Action(action) for action in d.get('actions',[])], cmp=lambda x, y:x.timestamp-y.timestamp)

        #Some complications because cosponsors is not a list if there is only one
        cosponsors = d.get('cosponsors', [])
        if isinstance(cosponsors, str) or isinstance(cosponsors, unicode):
            self.cosponsors = [str(cosponsors)]
        else:
            self.cosponsors = [Legislator(co.get('cosponsor')) for co in cosponsors]

    def __getattr__(self, name):
        if name == 'lastaction':
            return None if self.actions == [] else self.actions[-1].timestamp

        if name == 'passed':
            return 'PASSED SENATE' in [action.action for action in self.actions]

        if name == 'introduced':
            return None if self.actions == [] else self.actions[0].timestamp

    def __str__(self):
        return 'Bill %s' % self.id

    def __repr__(self):
        return str(self)

class Action():
    def __init__(self,d):
        #The last section of an action is the date, split that off from the right
        self.action = str(d['action']).rsplit(' - ', 1)[0]
        self.timestamp = int(getType(d,'timestamp',int)/1000) if 'timestamp' in d else None

    def __getattr__(self, name):
        if name == 'date':
            if self.timestamp:
                return date.fromtimestamp(self.timestamp).strftime("%b %d, %Y")
            else:
                return None

    def __str__(self):
        return "%s: %s" % (self.date,self.action)

    def __repr__(self):
        return str(self)

class Vote():
    """
        #TODO: Support Ayes W/R somehow
    """
    _voteTypes = ['abstains','ayes','nays','excused']

    def __init__(self,d, billno=None):
        self.bill = billno if billno else getType(d, 'billno', str)
        self.votedata = dict([voter.get('name'),voter.get('vote')] for voter in d.get('voters',[]))
        #Currently no indication of vote type, this is a hack, I think its accurate
        self.type = "floor" if len(self.votedata.keys()) > 40 else "committee"
        self.timestamp =  getType(d,'timestamp',int)/1000 if 'timestamp' in d else None

    def __getattr__(self, name):
        names = ['votes', 'ayes', 'nays', 'excused', 'abstains']

        if name[0:3] == 'num' and name[3:] in names:
            return len(getattr(self, name[3:]))

        if name in names:
            if name == 'votes':
                return self.votedata
            else:
                return [person for person, vote in self.votedata.iteritems() if str(vote)==name.rstrip('s')]

        if name == 'date':
            if self.timestamp:
                return date.fromtimestamp(self.timestamp).strftime("%b %d, %Y")
            else:
                return None

        if name == 'passed':
            return True if (self.numayes > self.numvotes/2) else False

        raise AttributeError("Invalid attribute %s" % name)

    def __str__(self):
        results = dict([vote,getattr(self,"num"+vote)] for vote in self._voteTypes)
        return "%s: %s " % (self.date,results)

    def __repr__(self):
        return str(self)

class Legislator():
    def __init__(self,lastname):
        self.name = str(lastname) if lastname else None

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

class Transcript():
    def __init__(self,d):
        self.timestamp = getType(d,'timestamp',str)
        parts = self.timestamp.split(' ')
        self.date = "%s %s, %s" % (parts[1],parts[2],parts[5])
        self.session = getType(d,'session',str)
        if self.session:
            parts = self.session.split(' - ')
            self.type = parts[-1].split(' ')[0]
            if len(parts) == 3:
                self.session = '%s - %s' % (parts[2],parts[1])
        else:
            self.type = None
        self.text = getType(d,'text',str)

    def __str__(self):
        return "%s: %s" % (self.session,self.date)

    def __repr__(self):
        return str(self)
