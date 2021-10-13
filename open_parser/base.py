import os
import json
import re
from dataclasses import dataclass, field
import datetime
from urllib import request, parse

from bs4 import BeautifulSoup, BeautifulStoneSoup

@dataclass
class Meta:
    author:list[str]
    doi:str
    link:str
    citation_date:str
    publication_date:str
    publisher:str
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
    def __init__(self, journal:str, base_url:str, search_url:str, articles:list[Article]=[], article_links:list[ArticleLink]=[]) -> None:
        super().__init__()
        self.journal = journal
        self.base_url = base_url # Website
        self.search_url = search_url # Query URL -> specific to every search query
        self.query_url = "" # Query URL -> specific to every search query
        self.articles = articles
        self.article_links = article_links

        self.parser_home = os.path.join(os.environ['HOMEPATH'], '.article_parser')
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
        for article in self.article_links:
            self.articles.append(self.parse_article(article))

    def parse_article(self, article_link:dict)->Article:
        page_soup = self.get_page_soup(article_link.url)
        meta = self.get_meta(page_soup)
        sections = self.get_sections(page_soup)
        refs = self.get_refs(page_soup)
        return Article(meta=meta, sections=sections, title=article_link.title, refs=refs)

    def _search(self, query):
        self.query_url = self.get_query_url(query)
        page_html = request.urlopen(self.query_url).read().decode("utf-8")
        return BeautifulSoup(page_html, "lxml")
        
    def get_query_url(self, query):
        return self.search_url.format(parse.quote(query))

    # Each class instance should overwrite these methods
    def get_page_soup(self, article_url)->BeautifulStoneSoup:
        pass

    def get_meta(self, soup:BeautifulSoup)->Meta:
        pass

    def get_sections(self, soup:BeautifulSoup)->list[dict]:
        pass

    def get_refs(self, soup:BeautifulSoup)->list[Reference]:
        pass        