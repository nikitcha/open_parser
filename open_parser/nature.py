from bs4 import BeautifulSoup
from .base import Retriever,  Meta, ArticleLink

URL = {'base':"https://www.nature.com",
       'search':"https://www.nature.com/search?q={}&journal=srep,%20ismej,%20ncomms&order=relevance",
        }

class Nature(Retriever):

    def __init__(self) -> None:
        super().__init__(journal='nature', base_url=URL['base'], search_url=URL['search'])
        self.num_pages = 1
        self.meta = {
            'author':'dc.creator', 
            'citation_date':'dc.date',
            'publication_date':'dc.date', 
            'doi':'citation_doi',
            'journal':'citation_journal_title', 
            'publisher':'citation_publisher',
            'article_type':'citation_article_type',
            'pdf':'citation_pdf_url',
            'link':'citation_fulltext_html_url'}

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
            return [s.text for s in sections if s.text]
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
                part = {'title':sections[i].text, 'text':self.get_sections(div, level+1)}
                if part['text']:
                    parse.append(part)
            return parse