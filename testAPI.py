from newsapi import NewsApiClient
from sys import argv
from newspaper import Article, fulltext
from requests import get
from json import dumps


newsapi = NewsApiClient(api_key='<api key>')

articleList = newsapi.get_top_headlines(q="Trump", language='en', page_size=100)['articles']


article_dicts = []
i=0
for article in articleList:
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

    article_dicts.append(article_dict)
    print('Downloaded article: {0}'.format(article_dict['title']))
    i+=1
    print('Article number: {0}'.format(i))

with open('articles_V2.json', 'wt') as fh:
    fh.write(dumps(article_dicts))
