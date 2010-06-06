
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
    
Manipulating Bills
-----------------------

.. doctest::

    >>>bill = openleg.bill('S66002')
    >>>print bill.keys()
