from itertools import combinations
from json import loads
from traceback import print_exc
from testAPI import JSON_ARTICLE_DUMP
from requests import post

if __name__ == '__main__':
    with open(JSON_ARTICLE_DUMP) as fh:
        all_articles = loads(fh.read())
    for (article, _article) in combinations(all_articles, r=2):
        try:
            response = post(
                'http://0.0.0.0:8083/article_pairs/add',
                json={
                    'url': article['link'],
                    'text': article['text'],
                    '_url': _article['link'],
                    '_text':_article['text'],
                },
            )
            assert response.status_code == 200, (response, response.text)
        except:
            print_exc()
