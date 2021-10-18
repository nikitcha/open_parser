from .base import Retriever, Meta, ArticleLink
from bs4 import BeautifulSoup
from requests_html import  HTMLSession
from .base import Retriever,  Meta, ArticleLink
import re

URL = {'base':"https://iopscience.iop.org",
       'search':"https://iopscience.iop.org/nsearch?terms={}&orderBy=relevance&pageLength=20&accessType=open-access",
        }
session = HTMLSession()      

"""
IOP sends captcha almost immediately!
"""

class IOP(Retriever):
    def __init__(self) -> None:
        super().__init__(journal='iop', base_url=URL['base'], search_url=URL['search'])
        self.num_pages = 0

    def _search(self, query)->BeautifulSoup:
        self.query_url = self.get_query_url(query)
        res = session.get(self.query_url)
        res.html.render(wait=1,sleep=1)
        html = res.html.html
        soup = BeautifulSoup(html, "lxml")
        return soup

    def get_page_html(self, url)->str:
        res = session.get(url)
        res.html.render(wait=1,sleep=1)
        html = res.html.html           
        return html
        
    def get_page_links(self, page_soup):
        article_links = []
        articles = page_soup.find_all('div',{'class':'art-list-item'})
        for article in articles:
             if 'open access' in article.text.lower():
                title = article.find('h2')
                doi = article.find('a', {'class':'mr-2'}).get('href')
                uri = title.find('a').get('href')
                article_links.append(ArticleLink(title=title.text.strip(), url=self.base_url+uri, doi=doi))
        return article_links

    def get_meta(self, page_soup)->Meta:
        data = {}
        # Add authors
        authors = page_soup.find_all('span', {'itemprop':'author'})
        data.update({'author':[a.find('span',{'itemprop':'name'}).text for a in authors]})
        # Add doi
        data.update({'doi':page_soup.find('div', {'class':'article-meta'}).find('a',{'itemprop':'sameAs'}).get('href')})
        # Add date
        date = page_soup.find('span', {'class':'wd-jnl-art-pub-date'}).text.replace('Published ','')
        data.update({'publication_date':date})
        data.update({'citation_date':date})
        # Add publisher
        data.update({'publisher':'IOP Publishing'})
        # Add journal
        data.update({'journal':page_soup.find('span', {'itemid':'periodical'}).find('a',{'itemprop':'url'}).text})
        # Add PDF
        pdf = page_soup.find('div', {'class':'btn-multi-block mb-1'}).find('a',{'itemprop':'sameAs'}).get('href')
        data.update({'pdf':self.base_url+pdf})
        # Add link
        doi_short = data['doi'].replace('https://doi.org', '')
        data.update({'link':self.base_url+'/article'+doi_short})
        # Add article type
        data.update({'article_type':'Journal Article'})
        return Meta(**data)

    def get_sections(self, soup, level=0):
        sections = soup.find_all(self.levels[level])
        if len(sections)==0 and level<4:
            return self.get_sections(soup, level+1)
        if len(sections)==0:
            return None
        if level==4:
            return [s.text for s in sections if s.text if s.text]
        else:
            parse = []       
            for i in range(len(sections)):
                parent = str(soup)
                start = str(sections[i])
                div = parent[parent.rfind(start):]
                if i==len(sections)-1:
                    div = BeautifulSoup(div, "lxml")
                else:
                    end = str(sections[i+1])
                    div = BeautifulSoup(div[:div.rfind(end)], "lxml")               
                part = {'title':sections[i].text, 'text':self.get_sections(div, level+1)}
                if part['text']:
                    parse.append(part)
            return parse 