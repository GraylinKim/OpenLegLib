import cPickle, urllib2, re, os, pprint
pprint = pprint.PrettyPrinter(indent=2).pprint

from BeautifulSoup import BeautifulSoup

import cPickle,os
openlegdir = os.path.dirname(os.path.abspath(__file__))

def getSenatorInfo():
    failed = list()
    senatorInfo = dict()

    for senator in getSenators():
        website = getWebsite(senator)

        print '------------------------------------'
        print 'Processing Sponsor: '+senator
        print website
        
        #   try:
        home = BeautifulSoup(urllib2.urlopen(website))
        contact = BeautifulSoup(urllib2.urlopen(website+'/contact'))
        senatorInfo[normalizeName(senator)] = {
            'chairships':[], 
            'committees':[], 
            'district':getDistrict(home),
            'email': getEmail(contact),
            'facebook':getSocialLink(home, "facebook"),
            'fullname':senator,
            'lastname':getLastName(senator),
            'offices': getOffices(contact),
            'parties':getParties(home),
            'portrait':getPortrait(home),
            'rss':getSocialLink(home, "rss"),
            'twitter':getSocialLink(home, "twitter"),
            'website': website,
            'youtube':getSocialLink(home, "youtube"),
        }
        pprint(senatorInfo[normalizeName(senator)])
        #   except Exception as e:
        #       failed.append( [senator, website, e] )
        #       print "Error Processing %s (Error: %s)" % (senator, e)

    with open(openlegdir+'/senators.dat', 'w') as f:
        legislators = cPickle.dump(senatorInfo, f)

    print 'Done with %i failures ' % len(failed)
    if failed != []:
        print pprint(failed)
        
def fillCommitteeInfo():
    
    with open(openlegdir+'/senators.dat') as f:
        senatorInfo = cPickle.load(f)
        
    committeeInfo = dict()
    for committee in getCommittees():
        
        print 'Currently filling Comittee: '+committee
        
        #Locate our soup by removing all ',' and joining the locased words with '-'
        cleaned = committee.replace(',','').lower()
        url = 'http://www.nysenate.gov/committee/' + '-'.join(cleaned.split())
        soup = BeautifulSoup(urllib2.urlopen(url).read())
        
        #Get the chair, its held separately from the members
        chair = normalizeName(soup.find('div','committee-chair').findAll('a')[1].text)
        senatorInfo[chair]['chairships'].append(committee)
        committeeInfo[committee] = [chair]
        
        #Get all the members from the embedded list
        members = [normalizeName(x.a.text) for x in soup.find('div','committee-members').findAll('li')]
        [senatorInfo[member]['committees'].append(committee) for member in members]
        committeeInfo[committee].extend(members)
        
    pprint(senatorInfo)
    
    with open(openlegdir+'/senatorsfilled.dat', 'w') as f:
        cPickle.dump((committeeInfo, senatorInfo), f)
        
def getCommittees():
    """Create a list of committees
    [ committeeName, committeeName, ... ]
    """
    url = 'http://open-staging.nysenate.gov/legislation/committees/'
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    committees = [ x.h4.text for x in soup.findAll('div','billSummary') ]
    
    #Return a new list excluding invalid values
    return [c for c in committees if not c in (
        #This is redundant with Social Services and leads to nowhere, might be assembly
        'SOCIAL SERVICES, CHILDREN AND FAMILIES',
        #This is an assembly committee (I think), so we should remove that too for now
        'TOURISM, RECREATION AND SPORTS DEVELOPMENT'
    )]

def normalizeName(name):
    for x, y in {' Jr.':'',  ' Jr':'', 'Sen. ':'', 'Betty':'Elizabeth'}.items():
        name = name.replace(x, y)
    name = (name.strip(' ,').split(' ')[-1]+'+'+name[0]).lower()
    
    if name[:7] in ["johnson"]:
        return name
    #If this isn't johnson, we don't need the first letter
    return name[:-2]

    
def getSenators():
    """Create a list of all the senators and their names
    [ fullName, fullName, fullName ]
    """
    def fixNaming(x):
        """Fix the name ordering to First MI Last Suffix"""
        order = [1,0,2]
        parts = [s.strip() for s in x.split(',')]
        return ' '.join([ parts[i] for i in order[0:len(parts)] ])

    url = 'http://open-staging.nysenate.gov/legislation/senators/'
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    tags = soup.findAll('div','views-field-field-last-name-value')
    return [ fixNaming(x.span.a.text) for x in tags ]

def getWebsite(senator):
    #Clean up some special characters
    cleaned = senator.lower().replace(u'\xe9', 'e').replace('.', '')

    #These guys decided not to use his middle initial
    if cleaned in ['jose p peralta', 'joseph a griffo', 'malcolm a smith']:
        cleaned = ' '.join(cleaned.split()[0:3:2])

    return 'http://www.nysenate.gov/senator/'+'-'.join(cleaned.split())

def getEmail(soup):
    email = soup.find('div','views-field-field-email-email').span.span.text
    return email.replace('[at]','@').replace(' [dot] ','.')
def getChairships(soup):
    comms = soup.find('div',id='block-nyss_blocks-my_committees').findAll('li')
    chairs = [comm.text for comm in comms if comm.find('-Chair Person')]
    return [chair.replace('-Chair Person', '') for chair in chairs]

def getDistrict(soup):
    return soup.find('div', 'district').text.split(') ')[1].split(' ')[0][:-2]

def getSocialLink(soup, type):
    try:
        return soup.find('a',type)['href']
    except TypeError:
        return None

def getPortrait(soup):
    return soup.find('img','imagecache imagecache-senator_teaser')['src']

def getParties(soup):
    partyLookup = dict(
       d="Democrat",            r="Republican",     c="Conservative",
       cnst="Constitution",     g="Green",          ip="Independence Party",
       i="Independent",         ind="Independent",  l="Liberal",
       libt="Libertarian",      nl="Natural Law",   rtl="Right to Life",
       sj="Save Jobs",          sc="School Choice", swp="Socialist Workers",
       wf="Working Families",
    )
    parties = soup.find('div', 'district').text.split('(')[1].split(')')[0].split(', ')
    return [partyLookup[party.lower()] for party in parties]

def getLastName(sponsor):
    return sponsor.replace(' Jr.', '').replace(' Jr', '').split(' ')[-1]

def getOffices(soup):
    #Find Contact info and break it into 1 line segments
    info = soup.find('div','views-field-field-contact-information-value')
    lines = info.findAll('p',text=re.compile(r'[\w^&]+'))
    lines = [line.replace('&nbsp;', ' ') for line in lines]

    #Keep only the pieces we need
    lines = [line for line in lines if not line in (
        'Mailing Information',
        'FOR MORE DISTRICT 20 CONTACTS, CLICK ON "BLOG" TAB ON MAIN PAGE.',
        ' ','',
    )]

    #Find the start and end of each office chunk
    filter = re.compile("(Brooklyn|Plattsburgh|Albany|District|Satellite|Falls|Leader's) office", re.I)
    ends = [i for i in range(0,len(lines))
            if filter.search(lines[i])
                or lines[i].find('Courthouse Corporate Center')!=-1
                or lines[i].find('111 Main Street')!=-1
            ]
    ends.append(len(lines))

    #Zip them together into a dictionary
    return dict( (lines[i],lines[i+1:j]) for i,j in zip(ends[:-1],ends[1:]) )

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) == 1:
        print "Accepted arguments are 'senators', 'committees', and 'both'"
    else:
        for command in sys.argv[1:]:
            if command in ['senators', 'both']:
                getSenatorInfo()
            
            if command in ['committees', 'both']:
                fillCommitteeInfo()
