import os
import json
import re
from dataclasses import dataclass, field
from tqdm import tqdm
from urllib import request, parse

from bs4 import BeautifulSoup

@dataclass
class Meta:
    author:list[str]
    doi:str
    link:str
    citation_date:str
    publication_date:str
    journal:str=""
    publisher:str=""
    pdf:str=""
    access:str="open"
    article_type:str='article'

@dataclass
class Reference:
    author:list[str]
    year:int
    title:str
    publisher:str=""
    link:str=""
    doi:str=""

@dataclass
class ArticleLink(object):
    title:str
    url:str
    doi:str

@dataclass
class Article(object):
    meta:Meta
    title:str
    sections:list
    refs:list[Reference] = field(default_factory=Reference)

    def to_dict(self):
        refs = [r.__dict__ for r in self.refs]
        return {'meta':self.meta.__dict__, 'title':self.title, 'sections':self.sections, 'refs':refs}    

    def save(self, loc):
        with open(os.path.join(loc, 'article.json'), 'w',encoding='utf-8') as f:
            print(loc)
            json.dump(self.to_dict(), f, indent=3)        

class Retriever(object):
    def __init__(self, journal:str, base_url:str,search_url:str, articles:list[Article]=[], article_links:list[ArticleLink]=[],  env:str='dropbox') -> None:
        super().__init__()
        self.journal = journal
        self.base_url = base_url # Website
        self.search_url = search_url # Query URL -> specific to every search query
        self.query_url = "" # Query URL -> specific to every search query
        self.articles = articles
        self.article_links = article_links
        self.levels = {0:'h2',1:'h3',2:'h4',3:'h5',4:'p'}
        if env=='dropbox':
            self.parser_home = os.path.join(os.environ['HOMEPATH'], 'Dropbox (CEEBIOS)',"Dossier de l'équipe CEEBIOS","MdR_DB")
        else:
            self.parser_home = os.path.join(os.environ['HOMEPATH'], '.open_parser')
        if not os.path.exists(self.parser_home):
            os.mkdir(self.parser_home)        
        self.savedir = os.path.join(self.parser_home, journal)
        if not os.path.exists(self.savedir):
            os.mkdir(self.savedir)
        
    def filename(self, article):
        return re.sub(r'[^a-zA-Z0-9 ]','',article.title)
       
    def save(self):
        for article in self.articles:
            article_dir = os.path.join(self.savedir, self.filename(article))
            if not os.path.exists(article_dir):
                os.mkdir(article_dir)
            article.save(article_dir)
        
    def parse_articles(self):
        self.articles = []
        for i in tqdm(range(len(self.article_links)), desc='Parsing {}'.format(self.journal.capitalize())):
            article = self.article_links[i]            
            self.articles.append(self.parse_article(article))

    def parse_article(self, article_link:dict)->Article:
        page_soup = self.get_page_soup(article_link.url)
        meta = self.get_meta(page_soup)
        sections = self.get_sections(page_soup)
        refs = self.get_refs(page_soup)
        return Article(meta=meta, sections=sections, title=article_link.title, refs=refs)

    def get_page_html(self, url)->str:
        return request.urlopen(url).read().decode("utf-8")

    def get_page_soup(self, article_url)->BeautifulSoup:
        page_html = self.get_page_html(article_url)
        return BeautifulSoup(page_html, "lxml")

    def get_query_url(self, query)->str:
        return self.search_url.format(parse.quote(query))

    def _search(self, query)->BeautifulSoup:
        self.query_url = self.get_query_url(query)
        return self.get_page_soup(self.query_url)

    def search(self, query, page_range=[0,1]):
        page_soup = self._search(query)
        self.get_num_pages(page_soup)
        article_links = self.get_page_links(page_soup)
        for i in range(page_range[0],page_range[1]+1):
            if i>1:
                print('Pagination not implemented')
        # Remove articles that have been already parsed
        available = os.listdir(self.savedir)
        self.article_links = [link for link in article_links if self.filename(link) not in available]


    # Each class instance should overwrite these methods
    def get_num_pages(self, soup:BeautifulSoup)->None:
        return None

    def get_page_links(self, soup:BeautifulSoup)->list[ArticleLink]:
        return None

    def get_meta(self, soup:BeautifulSoup)->Meta:
        return None

    def get_sections(self, soup:BeautifulSoup)->list[dict]:
        return []        

    def get_refs(self, soup:BeautifulSoup)->list[Reference]:
        return []        
