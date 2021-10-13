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
from open_parser import Biorxiv, Nature
biorxiv = Biorxiv()
biorxiv.search("aquatic photoprotection", num_pages=1)
biorxiv.parse_articles()
biorxiv.save() # Check #home/.open_parser/bioarxiv

nature = Nature()
nature.search("aquatic photoprotection", num_pages=1)
nature.parse_articles()
nature.save() # Check #home/.open_parser/nature

```
