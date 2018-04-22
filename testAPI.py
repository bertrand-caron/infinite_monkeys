from newsapi import NewsApiClient
from sys import argv
from newspaper import fulltext
from requests import get
from json import dumps
from multiprocessing import Pool
from typing import Any

def get_article(i:int, article: Any) -> Any:
    linkText = get(article['url'], headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})

    try:
        articleText=fulltext(linkText.text)
    except AttributeError:
        articleText=('Article text is raising an error')

    article_dict = {
        'link': article['url'],
        'title': article['title'],
        'text': articleText,
    }

    print('Downloaded article: {0}'.format(article_dict['title']))
    print('Article number: {0}'.format(i))
    return article_dict

def main(query: str):
    newsapi = NewsApiClient(api_key='<api key>')

    articleList = newsapi.get_top_headlines(
        q=query,
        language='en',
        page_size=100,
    )['articles']

    with Pool(25) as p:
        article_dicts = p.starmap(
            get_article,
            enumerate(articleList)
        )

    with open('articles_V2.json', 'wt') as fh:
        fh.write(dumps(article_dicts))

if __name__ == '__main__':
    main('Trump')
