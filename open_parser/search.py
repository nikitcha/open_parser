import sys
from open_parser import Biorxiv, Nature, PNAS, PLOS, RoyalSociety
engines ={'biorxiv':Biorxiv, 'nature':Nature, 'pnas':PNAS, 'plos':PLOS, 'royal_society':RoyalSociety}

def search(term, journal):
    jname = journal.lower()
    if jname in engines:
        parser = engines[jname]()
        parser.search(term)
        parser.parse_articles()
        parser.save() # Check #home/.open_parser

if __name__=='__main__':
    journal, term = sys.argv[1:]
    search(term, journal)