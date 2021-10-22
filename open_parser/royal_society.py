from .base import Retriever, Meta, ArticleLink
from bs4 import BeautifulSoup
from requests_html import  HTMLSession
from .base import Retriever,  Meta, ArticleLink
import re

# The Royal Society Publishing
URL = {'base':"https://royalsocietypublishing.org",
       'search':"https://royalsocietypublishing.org/action/doSearch?AllField={}",
        }
session = HTMLSession()      

class RoyalSociety(Retriever):
    def __init__(self) -> None:
        super().__init__(journal='royal_society', base_url=URL['base'], search_url=URL['search'])
        self.num_pages = 1

    def get_page_links(self, page_soup):
        article_links = []
        articles = page_soup.find_all('li',{'class':'clearfix separator search__item'})
        for article in articles:
             link = uri = article.find('a', {'title':'Full text'})
             if link:  
                title = re.sub('[\n ]+',' ', article.find('span',{'class':'hlFld-Title'}).find('a').text)
                doi = article.find('a', {'class':'meta__doi'}).get('href')
                uri = link.get('href')
                article_links.append(ArticleLink(title=title, url=self.base_url+uri, doi=doi))
        return article_links
       
    def get_page_html(self, url)->str:
        res = session.get(url)
        res.html.render(wait=1,sleep=1)
        html = res.html.html           
        return html

    def _search(self, query)->BeautifulSoup:
        self.query_url = self.get_query_url(query)
        res = session.get(self.query_url)
        res.html.render(wait=1,sleep=1)
        html = res.html.html
        soup = BeautifulSoup(html, "lxml")
        return soup

    def get_meta(self, page_soup)->Meta:
        data = {}
        article = page_soup.find('div',{'class':"article-data"})
        # Add authors
        authors = article.find_all('span', {'class':'hlFld-ContribAuthor'})
        data.update({'author':[a.text for a in authors]})
        # Add doi
        data.update({'doi':article.find('a',{'class':'doi-link'}).get('href')})
        # Add date
        data.update({'publication_date':page_soup.find('span',{'class':'epub-section__date'}).text})
        data.update({'citation_date':page_soup.find('span',{'class':'epub-section__date'}).text})
        # Add publisher
        data.update({'publisher':'The Royal Society'})
        # Add journal
        data.update({'journal':page_soup.find('div',{'class':'row col-md-12'}).find('img').get('alt')})
        # Add PDF
        doi_short = data['doi'].replace('https://doi.org', '')
        data.update({'pdf':self.base_url+'/doi/pdf'+doi_short})
        # Add link
        data.update({'link':self.base_url+'/doi/full'+doi_short})
        # Add article type
        data.update({'article_type':page_soup.find('span',{'class':'citation__top__item article__tocHeading'}).text})
        return Meta(**data)

    def get_sections(self,soup, level=0):
        abstract = soup.find('div',{'class':'hlFld-Abstract'})
        body = soup.find('div',{'class':'hlFld-Fulltext'})
        return self._get_sections(abstract)+self._get_sections(body, level=1)


    def _get_sections(self, soup, level=0):
        sections = soup.find_all(self.levels[level])
        try:
            sections = [sec for sec in sections if 'table-collapser' not in sec.get('class')[0]]
        except:
            x=0
        if len(sections)==0 and level<4:
            return self._get_sections(soup, level+1)
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
                part = {'title':sections[i].text, 'text':self._get_sections(div, level+1)}
                if part['text']:
                    parse.append(part)
            return parse