from open_parser import Biorxiv, Nature, PNAS, PLOS
engines ={'biorxiv':Biorxiv, 'nature':Nature, 'pnas':PNAS, 'plos':PLOS}

def search(term, page=1, journals=['nature']):
    for journal in journals:
        jname = journal.lower()
        if jname in engines:
            parser = engines[jname]()
            parser.search(term, page_range=[page,page])
            parser.parse_articles()
            parser.save() # Check #home/.open_parser

