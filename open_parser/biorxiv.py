from .base import Retriever, Meta, ArticleLink

URL = {'base':"https://www.biorxiv.org",
       'search':"https://www.biorxiv.org/search/{}%20jcode%3Amedrxiv%7C%7Cbiorxiv%20numresults%3A25%20sort%3Arelevance-rank",
        }

class Biorxiv(Retriever):

    def __init__(self) -> None:
        super().__init__(journal='biorxiv', base_url=URL['base'], search_url=URL['search'])
        self.num_pages = 0
        self.meta = {
            'author':'DC.Contributor', 
            'citation_date':'citation_publication_date',
            'publication_date':'DC.Date', 
            'doi':'citation_doi',
            'publisher':'DC.Publisher', 
            'access':'DC.AccessRights',
            'link':'citation_full_html_url',
            'pdf':'citation_pdf_url'}

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
        article_links = []
        links = page_soup.find_all("a", {"class": "highwire-cite-linked-title"})
        dois = page_soup.find_all("span", {"class": "highwire-cite-metadata-doi"})

        for link,doi in zip(links, dois):
            uri = link.get('href')+'.full'
            article_links.append(ArticleLink(title=link.text, url=self.base_url+uri, doi=list(doi.children)[1].text.strip()))
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
            return [s.text for s in sections]
        else:
            out = []
            for sec in sections:
                part = {'title':sec.text, 'text':self.get_sections(sec.parent, level+1)}
                if part['text']:
                    out.append(part)
            return out