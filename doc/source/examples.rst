
Learn By Example!
===================

Getting Started
---------------------

To get us started we'll import the API and create an instance of the default
client. This will allow us to work with native python dictionaries and put a
reasonable limit on the number of search results on each page.

.. doctest::

    >>>from openleg import api
    >>>openleg = api.OpenLegislation()
    
Additionally, we'll create a pretty printer to allow us to more easily examine
our results

.. doctest::

    >>>import pprint
    >>>pp = pprint.PrettyPrinter(indent=4)

Manipulating Results
-----------------------

When working with any results in object mode, its important to note that they
are really just dictionaries and can/should be worked with as such.

.. doctest::

    >>>bill = openleg.bill('S66002')
    >>>pp.pprint(bill)
    {   u'actions': [   {   u'action': u'SIGNED CHAP.494 - Nov 12, 2009',
                            u'timestamp': u'1258002000000'},
                            ...]
        u'cosponsors': [],
        u'senateId': u'S66002',
        u'sponsor': u'STEWART-COUSINS',
        u'summary': u'Enacts into law major components of legislation necessary for the efficient operation of local governments. ',
        u'title': u'Enacts into law major components of legislation necessary for the efficient operation of local governments; repealer',
        u'votes': [   {   u'abstains': u'0',
                          u'ayes': u'59',
                          u'excused': u'1',
                          u'nays': u'2',
                          u'timestamp': u'1257829200000',
                          u'voters': [   {   u'name': u'ADAMS', u'vote': u'aye'},
                                         ...]},
                      {   u'ayes': u'20',
                          u'excused': u'1',
                          u'nays': u'3',
                          u'timestamp': u'1257829200000',
                          u'voters': [   {   u'name': u'SMITH', u'vote': u'aye'},
                                         ...]},
        u'year': 2009}
        
From this you can see the organization of information within a bill. Lets try
to print out a list of all the actions taken in chronological order. We'll 
reformat the string for ease of reading while we're at it.

.. doctest::

    >>> for action in reversed(bill['actions']):
    ... 	print ' - '.join(reversed(action['action'].split('-')))
    ... 
     Nov 10, 2009 - substituted for a40002 
     Nov 10, 2009 - ruling of chair on point of order 
     Nov 10, 2009 - returned to senate 
     Nov 10, 2009 - referred to codes 
     Nov 10, 2009 - passed assembly 
     Nov 10, 2009 - ordered to third reading rules cal.679 
     Nov 10, 2009 - REFERRED TO RULES 
     Nov 10, 2009 - PASSED SENATE 
     Nov 10, 2009 - ORDERED TO THIRD READING CAL.1 
     Nov 10, 2009 - 3 DAY MESSAGE 
     Nov 10, 2009 - DELIVERED TO GOVERNOR 
     Nov 10, 2009 - DELIVERED TO ASSEMBLY 
     Nov 12, 2009 - SIGNED CHAP.494 
    
Searching
--------------------------------

Searching has two steps. First is query construction using the OpenLegislation
client. Second is fetching a page of the results from the server.

.. doctest::
    
    >>>query = openleg.search('health*')
    >>>results = query.fetch()
        
Lets take a look at what kind of results we got.

.. doctest::

    >>> for result in results:
    ...     #truncate long titles
    ...     title = result['title'][0:77]+'...' if (result['title'] and len(result['title'])>80) else result['title']
    ...     #format the output
    ...     print '(%s) %s' % (result['type'],title)
    ... 
    (transcript) REGULAR SESSION - Jul 9, 2009 3:30 AM
    (transcript) REGULAR SESSION - Jul 15, 2009 7:58 AM
    (transcript) REGULAR SESSION - Jul 16, 2009 12:56 PM
    (transcript) REGULAR SESSION - Sep 10, 2009 3:37 AM
    (transcript) EXTRAORDINARY SESSION - Nov 10, 2009 12:19 PM
    (transcript) EXTRAORDINARY SESSION - Nov 24, 2009 12:19 PM
    (transcript) EXTRAORDINARY SESSION - Dec 2, 2009 10:46 AM
    (transcript) Select Committee - Monserrate Investigation - Executive Session - Nov 23, 200...
    (transcript) Select Committee - Monserrate Investigation - Executive Session - Dec 14, 200...
    (transcript) Select Committee - Monserrate Investigation - Executive Session - Dec 29, 200...
    (transcript) REGULAR SESSION - Jan 20, 2010 12:22 PM
    (transcript) None
    (transcript) None
    (transcript) REGULAR SESSION - Feb 1, 2010 3:39 AM
    (meeting) Health - Jan 12, 2010 12:00 PM
    (meeting) Health - Jan 20, 2010 12:00 PM
    (meeting) Health - Feb 2, 2010 12:00 PM
    (meeting) Health - Feb 23, 2010 12:00 PM
    (meeting) Mental Health and Developmental Disabilities - Feb 24, 2010 9:30 AM
    (bill) Establishes a special enrollment period for employees and members with expire...
        
Because searching can often produce a large number of results, pagination 
typically occurs (default number of results per page is 20). Unfortunately
responses (in JSON) don't currently pass back the total number of results, its
being worked on though. Lets check to see what is on the second page of results.

.. doctest::

    >>>results = query.fetch(2) #gets the second page
    >>> for result in results:
    ...     #truncate long titles
    ...     title = result['title'][0:77]+'...' if (result['title'] and len(result['title'])>80) else result['title']
    ...     #format the output
    ...     print '(%s) %s' % (result['type'],title)
    ... 
    (bill) Authorizes the purchase of coverage under family health plus by voluntary emp...
    (bill) Provides for the extension of health insurance coverage to the unmarried chil...
    (bill) Establishes a special enrollment period for employees and members with expire...
    (bill) Establishes a special enrollment period for employees and members with expire...
    (bill) Makes technical corrections to provisions of law relating to rates of payment...
    (bill) Provides for the continuation of health insurance benefits for public employe...
    (bill) Relates to referrals of patients for health related items or services
    (bill) Relates to the N.Y. State Health Care Consumer and Provider Protection and Eq...
    (bill) Amends the education law relating to school based health and mental health cl...
    (bill) Enacts the "minority mental health act" to establish the division of minority...
    (bill) Authorizes health care professionals licensed in other jurisdictions and appo...
    (bill) Enacts the "healthcare rule-making reform act"
    (bill) Authorizes the commissioner of health to establish procedures providing infor...
    (bill) Requires hospitals to disclose any hospital service or health related service...
    (bill) Requires certain health and casualty insurers to provide coverage for prenata...
    (bill) Relates to the rights of health care providers under managed care contracts
    (bill) Relates to overpayments to health care providers when fraud or other intentio...
    (bill) Relates to standards for prompt, fair and equitable settlement of claims for ...
    (bill) Relates to direct access to school-based health centers under child health plus
    (bill) Enacts into law major components of legislation necessary to implement the he...
    
Filters
------------

There will be times when we only want to pull down a specific type of result
in our search. For this we can apply filters to our queries and produce a new
more defined search.

Lets limit the results of our 'health*' search to only bills.

.. doctest::

    >>>#we can start with the query from above
    >>>billquery = query.types('bill') #this does not alter *query*
    >>>results = billquery.fetch()
    >>> for result in results:
    ...     #truncate long titles
    ...     title = result['title'][0:77]+'...' if (result['title'] and len(result['title'])>80) else result['title']
    ...     #format the output
    ...     print '(%s - %s) %s' % (result['type'],result['id'],title)
    (bill - S66006) Establishes a special enrollment period for employees and members with expire...
    (bill - S53301) Authorizes the purchase of coverage under family health plus by voluntary emp...
    (bill - S51104) Provides for the extension of health insurance coverage to the unmarried chil...
    (bill - A40006) Establishes a special enrollment period for employees and members with expire...
    (bill - A40000) Establishes a special enrollment period for employees and members with expire...
    (bill - A9944) Makes technical corrections to provisions of law relating to rates of payment...
    (bill - A9943) Provides for the continuation of health insurance benefits for public employe...
    (bill - A9933) Relates to referrals of patients for health related items or services
    (bill - A9871) Relates to the N.Y. State Health Care Consumer and Provider Protection and Eq...
    (bill - A9860) Amends the education law relating to school based health and mental health cl...
    (bill - A9833) Enacts the "minority mental health act" to establish the division of minority...
    (bill - A9829) Authorizes health care professionals licensed in other jurisdictions and appo...
    (bill - A9822) Enacts the "healthcare rule-making reform act"
    (bill - A9797) Authorizes the commissioner of health to establish procedures providing infor...
    (bill - A9792) Requires hospitals to disclose any hospital service or health related service...
    (bill - A9787) Requires certain health and casualty insurers to provide coverage for prenata...
    (bill - A9769) Relates to the rights of health care providers under managed care contracts
    (bill - A9720) Relates to overpayments to health care providers when fraud or other intentio...
    (bill - A9718) Relates to standards for prompt, fair and equitable settlement of claims for ...
    (bill - A9717) Relates to direct access to school-based health centers under child health plus
    
Additional filters exist for filtering by committee (*committees(...)*) and by
sponsor (*sponsors(...)*). Lets filter the remaining bills down to those under
the Aging and Health committees.

.. testcode::

    >>> #notice that multiple values (case insensitive) are wrapped in a list
    >>> commquery = billquery.committees('Aging','Health')
    >>> #results not included
    
If we were starting from scratch and we wanted this query, we could take
advantage of chaining.

.. testcode::
    
    >>> query = openleg.search('health*').types('bill').committees('Aging','Health')
    
Logical Manipulation
------------------------

Now what if we wanted to get all the bills matching 'health*' that were not in
the Aging or Health committees? We could use the NOT operator.

.. doctest::

    >>> query = NOT(
    ...     openleg.search('health*').types('bill'),
    ...     openleg.search().committees('Aging','Health')
    ... )
    
See the :doc:`full documentation <index>` for more details.
