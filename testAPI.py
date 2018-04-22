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

def main(query: str = None, max_page: int = 4, page_size: int = 100):
    newsapi = NewsApiClient(api_key='INSERT_KEY_HERE')

    article_dicts = []
    for page in range(1, max_page + 1):
        articleList = newsapi.get_top_headlines(
            language='en',
            page_size=page_size,
            page=page,
        )['articles']

        if len(articleList) == 0 or len(article_dicts) >= max_page * page_size:
            break

        with Pool(25) as p:
            article_dicts += p.starmap(
                get_article,
                enumerate(articleList, start=len(article_dicts))
            )

    with open('articles_V2.json', 'wt') as fh:
        fh.write(dumps(article_dicts))

if __name__ == '__main__':
    main()
