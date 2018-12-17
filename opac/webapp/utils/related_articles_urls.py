import requests
from bs4 import BeautifulSoup


URL_GSCHOLAR = "https://scholar.google.com/scholar?q="

#  similares no Google Scholar
URL_GSCHOLAR_RELATED = "/scholar?q=related:"

#  Citados no Google Scholar
URL_GSCHOLAR_CITES = "/scholar?cites="

# Similares no Google
URL_GOOGLE = "https://www.google.com/search?q="


def related_links(article_url, titles):
    return [
        (
            "Google",
            "Similares no",
            get_google_results_searched_by_article_titles(titles)[0],
        ),
        (
            "Google Scholar",
            "Citados e Similares no",
            get_scholar_results_searched_by_article_titles(titles)[0],
        ),
    ]


def get_google_results_searched_by_article_titles(titles):
    """
    Retorna os links do resultado de busca para o Google usando os
    títulos do artigo
    """
    return [URL_GOOGLE + title for title in titles]


def get_scholar_results_searched_by_article_titles(titles):
    """
    Retorna os links do resultado de busca para o Google Scholar usando
    os títulos do artigo
    """
    return [URL_GSCHOLAR + title for title in titles]


def get_scholar_results_searched_by_article_url(article_page_url):
    """
    Retorna o link do resultado de busca para o Google Scholar usando
    a URL do artigo
    """
    return URL_GSCHOLAR + article_page_url


def get_page_content(url):
    """
    Retorna o conteúdo de uma página HTML acessada por url
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.content
    except:
        pass


def get_scholar_urls(content):
    """
    Retorna todos os links para o Google Scholar encontrados em um conteúdo de
    página HTML
    """
    bs = BeautifulSoup(content, "lxml")
    return [
        a["href"]
        for a in bs.find_all("a")
        if a.get("href") and a["href"].startswith("/scholar?")
    ]


def get_scholar_cited_and_related_article_urls(article_page_url, titles):
    """
    Retorna URL de cited e related encontrada na página de resultado de busca
    do artigo, fazendo "raspagem de dados"
    Ex.:
    Título do artigo:
        "Genome features of Leptospira interrogans serovar Copenhageni"
    Página de resultado de busca no Google Scholar:
        https://scholar.google.com.br/scholar?q=Genome+features+of+Leptospira+interrogans+serovar+Copenhageni&hl=pt-BR&as_sdt=0&as_vis=1&oi=scholart
    Link de "Citado por 206" (cited):
        https://scholar.google.com.br/scholar?cites=11763399093478119389&as_sdt=2005&sciodt=0,5&hl=pt-BR
    Link de "Artigos relacionados" (related):
        https://scholar.google.com.br/scholar?q=related:3VfqfSb9P6MJ:scholar.google.com/&scioq=Genome+features+of+Leptospira+interrogans+serovar+Copenhageni&hl=pt-BR&as_sdt=0,5&as_vis=1
    """
    urls = get_scholar_results_searched_by_article_titles(titles) + [
        get_scholar_results_searched_by_article_url(article_page_url)
    ]
    related = None
    cited = None
    for url in urls:
        content = get_page_content(url)
        if content:
            links = get_scholar_urls(content)
            for link in links:
                if "cites=" in link:
                    cited = link
                elif "q=related:" in link:
                    related = link
                if cited and related:
                    return cited, related
