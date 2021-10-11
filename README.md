Open Access Papers Parser
===============================

version number: 0.0.1
author: Nikolay Tchakarov

Overview
--------

Parse papers from open journals and store stuctured data

Installation / Usage
--------------------

To install use pip (not plublished yet):

    $ pip install open_parser 


Or clone the repo:

    $ git clone https://github.com/nikitcha/open_parser.git
    $ python setup.py install
    
Contributing
------------

TBD

Example
-------
```
from open_parser.biorxiv import Biorxiv
engine = Biorxiv()
engine.search('uv protection marine habitat', num_pages=1)
biorxiv.parse_articles()
biorxiv.save() # Check #home/.open_parser/bioarxiv
```
