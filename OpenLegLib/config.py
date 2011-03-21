class Configuration():

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

config = Configuration()
