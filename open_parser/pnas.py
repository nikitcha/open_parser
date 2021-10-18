from bs4 import BeautifulSoup
from requests_html import  HTMLSession
from .base import Retriever,  Meta, ArticleLink
import time 

session = HTMLSession()
URL = {'base':"https://www.pnas.org/",
       'search':"https://www.pnas.org/search/{}%20content_type%3Ajournal%20numresults%3A25%20sort%3Arelevance-rank?page=1",
        }

class PNAS(Retriever):
    def __init__(self) -> None:
        super().__init__(journal='pnas', base_url=URL['base'], search_url=URL['search'])
        self.num_pages = 0
        self.meta = {
            'author':'citation_author', 
            'citation_date':'citation_date',
            'publication_date':'citation_date', 
            'doi':'citation_doi',
            'publisher':'citation_publisher', 
            'journal':'citation_journal_title', 
            'article_type':'citation_article_type',
            'pdf':'citation_pdf_url',
            'link':'citation_full_html_url'
            }

    def get_num_pages(self, page_soup):
        ul = page_soup.find('ul', {'class':'pager'})
        if ul:
            try:
                link = ul.find("li",{'class':'pager-current last'})
                page = link.text
            except:
                link = ul.find("a",{'title':'Go to last page'})
                page = link.get('href').split('?page=')[1]
            self.num_pages = int(page)
                
    def get_page_links(self, page_soup):
        article_links = []
        ul = page_soup.find('ul', {'class':'highwire-search-results-list'})
        articles = list(ul.children)
        for article in articles:
            access = article.find('div', {'class':'highwire-cite-access'}).text
            if access in ['You have access','Open Access']:
                a = article.find('a',{'class':'highwire-cite-linked-title'})
                uri = a.get('href')
                title = a.text
                links = article.find_all('a')
                doi = [a.get('href') for a in links if "https://doi.org" in a.get('href')][0]
                article_links.append(ArticleLink(title=title, url=self.base_url+uri, doi=doi))
        return article_links

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
            return [s.text for s in sections if s.text]
        else:
            out = []
            for sec in sections:
                part = {'title':sec.text, 'text':self.get_sections(sec.parent, level+1)}
                if part['text']:
                    out.append(part)
            return out