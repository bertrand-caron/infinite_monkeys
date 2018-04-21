from typing import Dict, List
from functools import reduce, lru_cache
from itertools import combinations, groupby, chain
from json import loads, dumps
import unittest
from numpy import average
from os.path import basename
from pprint import pprint
from operator import itemgetter

DEBUG = True

def article_similarity_v_0(article: str, _article: str) -> float:
    return 1.0 if article == _article else 0.0

def get_keyword_frequency(article_text: str) -> Dict[str, int]:
    return {
        word: len(list(group))
        for (word, group) in groupby(
            sorted(
                article_text.split()
            )
        )
    }

def article_similarity_v_1(article: str, _article: str) -> float:
    keywords, _keywords = map(
        lambda article: get_keyword_frequency(article['text']),
        (article, _article),
    )

    all_words = set(chain(keywords.keys(), _keywords.keys()))

    return average(
        [
            word in keywords and word in _keywords# and (keywords[word] == _keywords[word])
            for word in all_words
        ]
    )

def article_similarity_v_2(article_word_dict: str, _article_word_dict: str) -> float:
    word_set, _word_set = map(set, (article_word_dict, _article_word_dict))
    try:
        return len(word_set & _word_set) / len(word_set | _word_set)
    except ZeroDivisionError:
        return -1000.

def truncate_link(link: str, max_length: int = 50) -> str:
    link_basename = basename(link)
    if len(link_basename) <= max_length:
        return link_basename
    else:
        return link_basename[:max_length - 3] + '...'

if __name__ == '__main__':
    with open('scraped_articles.json') as fh:
        data = loads(fh.read())

    all_articles = reduce(
        lambda acc, e: acc + e,
        [
            newspaper_dict['articles']
            for newspaper, newspaper_dict in data['newspapers'].items()
        ],
        []
    )

    keyword_frequency_for_link = {
        article['link']: get_keyword_frequency(article['text'])
        for article in all_articles
    }

    if DEBUG:
        BAD_ARTICLE = [
            'https://www.independent.co.uk/news/uk/politics/theresa-may-immigration-policies-ministers-responsibility-video-windrush-latest-a8314811.html',
            'https://www.independent.co.uk/news/world/americas/us-politics/michael-cohen-lawsuit-stormy-daniels-delay-raid-fbi-donald-trump-a8315151.html',
        ]

        pprint([(article, keyword_frequency_for_link[article['link']]) for article in all_articles if article['link'] in BAD_ARTICLE])
        exit()

    SIMILARITY_THRESHOLD = 0.16

    similarity_matrix_dict = {
        (article['link'], _article['link']): article_similarity_v_2(
            keyword_frequency_for_link[article['link']],
            keyword_frequency_for_link[_article['link']],
        )
        for (article, _article) in combinations(all_articles, r=2)
    }

    pprint(
        sorted(
            similarity_matrix_dict.items(),
            key=itemgetter(1),
        )
    )

    with open('news_articles_.json', 'wt') as fh:
        fh.write(
            dumps(
                {
                    'nodes': [
                        {'id': truncate_link(article['link']), 'group': 1}
                        for article in all_articles
                    ],
                    'links': [
                        {'source': truncate_link(article), 'target': truncate_link(_article), 'value': similarity_score}
                        for ((article, _article), similarity_score) in similarity_matrix_dict.items()
                        if similarity_score >= SIMILARITY_THRESHOLD
                    ],
                },
                indent=True,
            ),
        )
