import os
import re
import json
from urllib import request, parse
from bs4 import BeautifulSoup
from tqdm import tqdm
from .base import Retriever, Article, Meta, ArticleLink

URL = {'base':"https://www.nature.com",
       'search':"https://www.nature.com/search?q={}&journal=srep,%20ismej,%20ncomms&order=relevance",
        }

class Nature(Retriever):

    def __init__(self) -> None:
        super().__init__(journal='nature', base_url=URL['base'], search_url=URL['search'])
        self.num_pages = 1
        self.meta = {
            'author':'dc.creator', 
            'citation_date':'citation_online_date',
            'publication_date':'prism.publicationDate', 
            'doi':'citation_doi',
            'publisher':'citation_journal_title', 
            'article_type':'content.category.contentType',
            'pdf':'citation_pdf_url',
            'link':'citation_fulltext_html_url'}
        self.levels = {0:'h2',1:'h3',2:'h4',3:'h5',4:'p'}

    def get_num_pages(self, page_soup):
        pages = page_soup.find_all('li', {'class':'c-pagination__item'})
        if len(pages) >= 2:
            self.num_pages = int(pages[-2].get("data-page"))
                
    def get_page_links(self, page_soup):
        article_links = []
        articles = page_soup.find_all('article')
        for article in articles:
            link = article.find('a')
            uri = link.get('href')
            article_links.append(ArticleLink(title=link.text, url=self.base_url+uri, doi=""))
        return article_links

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
        page_html = request.urlopen(article_url).read().decode("utf-8")
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

    def get_sections(self,soup, level=0):
        sections = soup.find_all(self.levels[level])
        if len(sections)==0 and level<4:
            return self.get_sections(soup, level+1)
        if len(sections)==0:
            return None
        if level==4:
            return [s.text for s in sections]
        else:
            parse = []
            sections = [section for section in sections if section.get('id')]
            for i in range(len(sections)):
                div = soup.find_all('div',{'id':sections[i].get('id')+'-content'})
                if not div:
                    parent = str(sections[i].parent)
                    start = str(sections[i])
                    div = parent[parent.rfind(start):]
                    if i==len(sections)-1:
                        div = BeautifulSoup(div, "lxml")
                    else:
                        end = str(sections[i+1])
                        div = BeautifulSoup(div[:div.rfind(end)], "lxml")
                else:
                    div=div[0]
                parse.append({'title':sections[i].text, 'text':self.get_sections(div, level+1)})
            return parse