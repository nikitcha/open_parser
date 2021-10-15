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
    $ pip install open_parser
    
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
In command line:
```
python -m open_parser.search nature "structural white color"
```
