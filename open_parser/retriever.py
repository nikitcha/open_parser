import os
import re
import json
from urllib import request, parse
from bs4 import BeautifulSoup
from tqdm import tqdm

URL_MAP = {
    'rxivist': 'https://api.rxivist.org/v1/papers?q={}&timeframe=alltime&metric=downloads&page_size=100&page={}',
    'biorxiv': 'https://www.biorxiv.org/search/{}%20numresults%3A25%20sort%3Apublication-date%20direction%3Adescending'
}

class Retriever(object):
    def __init__(self, journal:str) -> None:
        super().__init__()
        self.journal = journal
        self.url = URL_MAP[journal]
        self.parser_home = os.path.join(os.environ['HOMEPATH'], '.article_parser')
        if not os.path.exists(self.parser_home):
            os.mkdir(self.parser_home)        
        self.savedir = os.path.join(self.parser_home, journal)
        if not os.path.exists(self.savedir):
            os.mkdir(self.savedir)
        self.articles = []
        self.article_links = []
        self.levels = {0:'h2',1:'h3',2:'h4',3:'h5',4:'p'}
        
    def filename(self, article):
        return re.sub(r'[^a-zA-Z0-9 ]','',article['title'])
       
    def save(self):
        for article in self.articles:
            article_dir = os.path.join(self.savedir, self.filename(article))
            if not os.path.exists(article_dir):
                os.mkdir(article_dir)
            with open(os.path.join(article_dir, 'article.json'), 'w',encoding='utf-8') as f:
                json.dump(article, f, indent=3)
        
    def parse_articles(self):
        self.articles = []
        for article in self.article_links:
            self.articles.append(self.parse_article(article))

    # Each class instance should overwrite those methods
    def search(self, query:str):
        pass

    def parse_article(self, article):
        return article


class Biorxiv(Retriever):
    def __init__(self) -> None:
        super().__init__(journal='biorxiv')
        self.base_url = "https://www.biorxiv.org"
        self.num_pages = 0
        self.page_html = []
        self.page_soup = []
        self.qurl = ""

    def get_num_pages(self):
        page_links = self.page_soup.find_all("li", {"class": "pager-item"})
        num_pages = 0
        if len(page_links) > 0:
            page_possible_last = self.page_soup.find("li", {"class": "pager-last"})
            if page_possible_last is not None:
                num_pages = int(page_possible_last.text)
            else:
                num_pages = int(page_links[-1].text)
        self.num_pages = num_pages
                
    def get_page_links(self, page_soup):
        links = []
        for link in page_soup.find_all(
                "a", {"class": "highwire-cite-linked-title"}):
            uri = link.get('href')
            links.append({'title': link.text, 'url': self.base_url + uri})
        return links

    def search(self, query, page_offset=0):
        papers = []
        self.qurl = self.url.format(parse.quote(query))
        self.page_html = request.urlopen(self.qurl).read().decode("utf-8")
        self.page_soup = BeautifulSoup(self.page_html, "lxml")
        self.get_num_pages()


    def get_articles(self, max_pages=5):
        self.article_links = []
        for i in range(max_pages):
            self.article_links.extend(self.get_page_articles(i))

    def get_page_articles(self, page=0):
        if page==0:
            links = self.get_page_links(self.page_soup)
        else:
            if self.num_pages>0 and page<=self.num_pages:
                page_url = self.qurl + '?page={}'.format(page)
                page_html = request.urlopen(page_url).read().decode("utf-8")
                page_soup = BeautifulSoup(page_html, "lxml")
                links = self.get_page_links(page_soup)
        return links

    def get_date(self, page_soup):
        date = page_soup.find("div", {"class": "pane-1"})
        if date is not None:
            date_str = date.text.split('\xa0')[-1].strip()
        else:
            date_str = ''
        return date_str

    def get_doi(self, page_soup):
        doi = page_soup.find("span", {"class": "highwire-cite-metadata-doi"})
        doi = list(doi.children)[1]
        doi.text.strip() 
        return doi

    def get_authors(self, page_soup):
        names = []
        authors = page_soup.find("span", {"class": "highwire-citation-authors"})
        for author in list(authors.children):
            try:
                fname = author.find("span", {"class": "nlm-given-names"}).text
                lname = author.find("span", {"class": "nlm-surname"}).text
                names.append(' '.join([fname,lname]))
            except:
                print(author)  
        return names

    def parse_article(self, article:dict):
        article_url = article['url'] + '.full'
        page_html = request.urlopen(article_url).read().decode("utf-8")
        page_soup = BeautifulSoup(page_html, "lxml")
        parsed = article.copy()
        parsed.update({'doi':self.get_doi(page_soup), 'authors':self.get_authors(page_soup)})
        parsed.update({'sections':self.get_sections(page_soup)})
        return parsed

    def parse_refs(self):
        print('TO DO')
        return None

    def get_sections(self, soup, level=0):
        sections = soup.find_all(self.levels[level])
        if len(sections)==0 and level<4:
            return self.get_sections(soup, level+1)
        if len(sections)==0:
            return None
        if level==4:
            return [s.text for s in sections]
        else:
            return [{'title':sec.text, 'text':self.get_sections(sec.parent, level+1)} for sec in sections]