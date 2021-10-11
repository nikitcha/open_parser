import os
import re
import json
from urllib import request, parse
from bs4 import BeautifulSoup
from tqdm import tqdm
from .base import Retriever, Article, Meta, ArticleLink

URL = {'base':"https://www.biorxiv.org",
       'search':"https://www.biorxiv.org/search/{}%20numresults%3A25%20sort%3Apublication-date%20direction%3Adescending",
        }

class Biorxiv(Retriever):

    def __init__(self) -> None:
        super().__init__(journal='biorxiv', base_url=URL['base'], search_url=URL['search'])
        self.num_pages = 0
        self.meta = {'author':'DC.Contributor', 'citation_date':'citation_publication_date','publication_date':'DC.Date', 'doi':'citation_doi','publisher':'DC.Publisher', 'access':'DC.AccessRights','link':'citation_full_html_url','pdf':'citation_pdf_url'}
        self.levels = {0:'h2',1:'h3',2:'h4',3:'h5',4:'p'}

    def get_num_pages(self, page_soup):
        page_links = page_soup.find_all("li", {"class": "pager-item"})
        num_pages = 0
        if len(page_links) > 0:
            page_possible_last = page_soup.find("li", {"class": "pager-last"})
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
            links.append(ArticleLink(title=link.text, url=self.base_url+uri))
        return links

    def search(self, query, max_pages=1):
        page_soup = self._search(query)
        self.get_num_pages(page_soup)
        self.article_links = []
        for i in range(max_pages):
            self.article_links.extend(self.get_page_articles(page_soup,i))

    def get_page_articles(self, page_soup, page=0):
        if page==0:
            links = self.get_page_links(page_soup)            
        else:
            if self.num_pages>0 and page<=self.num_pages:
                page_url = self.query_url + '?page={}'.format(page)
                page_html = request.urlopen(page_url).read().decode("utf-8")
                page_soup = BeautifulSoup(page_html, "lxml")
                links = self.get_page_links(page_soup)
        return links

    def get_page_soup(self, article_url):
        page_html = request.urlopen(article_url+'.full').read().decode("utf-8")
        return BeautifulSoup(page_html, "lxml")

    def get_refs(self, page_soup):
        print('TO DO REFS')
        return []

    def get_meta(self, page_soup)->Meta:
        data = {}
        for k,v in self.meta.items():
            els = page_soup.find_all('meta',{'name':v})
            els = [el.get('content') for el in els]
            if len(els)==1:
                data.update({k:els[0]})
            else:
                data.update({k:els})
        return Meta(**data)

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