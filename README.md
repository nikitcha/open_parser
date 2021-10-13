Open Access Papers Parser
===============================

version number: 0.1.0
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

Available Parsers:
------------------
- Biorxiv: Searches on Biorxiv and Medarxiv
- Nature: Searches on Scientific Reports, ISME and Nature Communications
- PLOS
- PNAS 

Example
-------
```
from open_parser import Biorxiv, Nature, PNAS, PLOS
engines = [Biorxiv, Nature, PNAS, PLOS]

for engine in engines:
    parser = engine()
    parser.search("aquatic photoprotection")
    parser.parse_articles()
    parser.save() # Check #home/.open_parser
```
