from flask import current_app


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
    return [current_app.config.get("OPAC_GOOGLE_LINK") + title for title in titles]


def get_scholar_results_searched_by_article_titles(titles):
    """
    Retorna os links do resultado de busca para o Google Scholar usando
    os títulos do artigo
    """
    return [
        current_app.config.get("OPAC_GOOGLE_SCHOLAR_LINK") + title for title in titles
    ]
