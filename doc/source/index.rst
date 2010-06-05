.. NYSS Open Legislation Python Library documentation master file, created by
   sphinx-quickstart on Fri Jun  4 11:40:43 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. currentmodule::  api
.. moduleauthor::   Graylin Kim <graylin.kim@gmail.com>

.. _overview:

Welcome to NYSS Open Legislation Python Library's documentation!
===================================================================

OpenLegislation is an legislative information service run by the New York
State Senate. This is a library to allow developers to quickly and effectively
search through the available information and pull down specific documents.

This is a guide to the proper use of the library and should serve as a 
tutorial for some of Open Legislations advanced search features. All examples
assume that default client settings have been preserved.

.. _exceptions:

Catching Exceptions
^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: OpenLegislationError

Before we get started, you should know what happens when things go wrong. All
OpenLegislation classes and functions will through a *OpenLegislationError*
when they are given bad input, are being used inappropriately, or (currently)
get a bad response from the server (working on something better for this).

.. _create:

Creating the Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The OpenLegislation class acts as the gateway class to the API and serves two
purposes. First, it holds various default parameters for request construction.
See :ref:`defaults` for detailed information. Second, it acts as a generator
for OpenLegislation :ref:`getting` and :ref:`searching`.
        
.. autoclass:: OpenLegislation

While the settings for your client can later be changed, the changes will not
be reflected in queries you have already instanciated

.. _defaults:

Customizing Defaults
^^^^^^^^^^^^^^^^^^^^^^^
These functions are used in the class constructor to create the initial state
for the client. If you find you need to change its settings after creation
you can call upon the following functions to do so.

Mode
""""""
.. automethod:: OpenLegislation.setMode

Pagesize
""""""""""
.. automethod:: OpenLegislation.setPagesize

Version (API)
"""""""""""""""
.. automethod:: OpenLegislation.setVersion

As stated above, while the settings for your client can be changed, the
changes you make will not be reflected in search queries you have already
created.

.. _getting:

*Get* Requests
^^^^^^^^^^^^^^^^

Get requests are automatically evaluated by the client and will return data
in the form specified by the current client state. In the case that you don't
know the unique ID for what you are looking for, please see :ref:`searching`.

.. automethod:: OpenLegislation.bill

.. automethod:: OpenLegislation.transcript

Meetings and Calendars in OpenLegislation are currently broken across the
different return types. Their corresponding *Get* Requests will be renabled
when they become safe and stable.

.. _searching:

*Search* Requests
^^^^^^^^^^^^^^^^^^

When you make a search request with your OpenLegislation client it passes back
an OpenLegislationSearch object (:ref:`advanced` for more details) instead of
evaluating immediately (like the :ref:`getting`)

.. automethod:: OpenLegislation.search

In order to evaluate the request you must call the fetch method and specify
the page to be fetched.

.. automethod:: OpenLegislationSearch.fetch

.. _advanced:

Advanced Searching
^^^^^^^^^^^^^^^^^^^^^

The OpenLegislationSearch object can also be used to perform advanced searches
in OpenLegislation through the use of filters.

    
.. autoclass:: OpenLegislationSearch

.. autoattribute:: OpenLegislationSearch.url
    
.. method:: OpenLegislationSearch.types(typelist)

    Filters results to results of the listed types. Supported types include:     
    - ['bill','vote','action','transcript','meeting','calendar']
    
    .. testcode::
    
        >>>openleg.search().types(['bills','votes'])
        
.. method:: OpenLegislationSearch.sponsors(sponsorlist)    
    
    Filters results to those (co)sponsored by the listed sponsors
    
    .. testcode::
    
        >>>openleg.search().sponsors(['Alesi','Adams'])
        
.. method:: OpenLegislationSearch.committees(committeelist)

    Filters results to results overseen by any of the listed committees
    
    .. testcode::

        >>>openleg.search().committees(['Aging','Health'])
            
In addition to the above methods there are also special methods for 
filtering with one item by passing a string instead of a list.

.. testcode::

    >>>openleg.search().type('bill')
    >>>openleg.search().committee('Aging').type('bill')
    >>>openleg.search().sponsor('Kruger').committee('Aging')
        
These advanced searches can then be logically manipulated using the following
logical operatations. 

.. autofunction:: AND

.. autofunction:: OR

.. autofunction:: NOT

All logical operations return an OpenLegislationSet.

.. autoclass:: OpenLegislationSet
    
Indices and tables
==================

* :ref:`genindex`

