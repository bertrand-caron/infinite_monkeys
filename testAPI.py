from newsapi import NewsApiClient
from sys import argv
from newspaper import fulltext
from requests import get
from json import dumps

article_dicts = []
articleCount = 0
articleHasText = True
articleMaxRange = 3

newsapi = NewsApiClient(api_key='ddac6b98882444029f877e86e6614a6a')

articleList = newsapi.get_top_headlines(language='en', page_size=100)['articles']

while articleHasText == True:
    for pageNumber in range(1,articleMaxRange):
        articleList = newsapi.get_top_headlines(language='en', page_size=100, page=pageNumber)['articles']
        for article in articleList:
            linkText = get(article['url'], headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})

            try:
                articleText=fulltext(linkText.text)
            except AttributeError:
                articleText=('Article text is raising an error')

            if len(articleText) < 1:
                articleHasText = False
            article_dict = {
                'link': article['url'],
                'title': article['title'],
                'text': articleText,
                'date': article['publishedAt']
            }

            article_dicts.append(article_dict)
            print('Downloaded article: {0}'.format(article_dict['title']))
            articleCount+=1
            print('Article number: {0}'.format(articleCount))
            with open('articles_V2.json', 'wt') as fh:
                fh.write(dumps(article_dicts))
    break

