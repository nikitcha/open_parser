from bs4 import BeautifulSoup
from requests_html import  HTMLSession
from .base import Retriever,  Meta, ArticleLink
import time 

session = HTMLSession()
URL = {'base':"https://journals.plos.org",
       'search':"https://journals.plos.org/plosone/search?q={}&page=1",
        }

class PLOS(Retriever):

    def __init__(self) -> None:
        super().__init__(journal='plos', base_url=URL['base'], search_url=URL['search'])
        self.num_pages = 1
        self.meta = {
            'author':'citation_author', 
            'citation_date':'citation_date',
            'publication_date':'citation_date', 
            'doi':'citation_doi',
            'publisher':'citation_publisher', 
            'journal':'citation_journal_title', 
            'article_type':'citation_article_type'}

    def get_num_pages(self, page_soup):
        nav = page_soup.find('nav',{'id':'article-pagination'})
        links = nav.find_all('a')
        if len(links) >= 2:
            self.num_pages = int(links[-2].text)
                
    def get_page_links(self, page_soup):
        article_links = []
        articles = page_soup.find_all('dt')
        for article in articles:
            doi = article.get('data-doi')
            link = article.find('a')
            uri = link.get('href')
            article_links.append(ArticleLink(title=link.text, url=self.base_url+uri, doi=doi))
        return article_links
       
    def _search(self, query)->BeautifulSoup:
        self.query_url = self.get_query_url(query)
        r = session.get(self.query_url)
        r.html.render()        
        time.sleep(1)
        return BeautifulSoup(r.html.html, "lxml")

    def get_meta(self, page_soup)->Meta:
        data = {}
        for k,v in self.meta.items():
            els = page_soup.find_all('meta',{'name':v})
            els = [el.get('content') for el in els]
            if len(els)==1:
                data.update({k:els[0]})
            else:
                data.update({k:els})

        # Add PDF
        try:
            link = page_soup.find('a',{'id':"downloadPdf"})
            data.update({'pdf':self.base_url+link.get('href')})
        except:
            print('Could not find PDF')

        # Add link
        link = page_soup.find('meta',{'property':'og:url'})
        data.update({'link':link.get('content')})
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
            out = []
            for sec in sections:
                part = {'title':sec.text, 'text':self.get_sections(sec.parent, level+1)}
                if part['text']:
                    out.append(part)
            return out