from typing import Dict, List
from functools import reduce
from itertools import combinations, groupby, chain
from json import loads, dumps
import unittest
from numpy import average
from os.path import basename

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

print(all_articles[:5])

def article_similarity_v_0(article: str, _article: str) -> float:
    return 1.0 if article == _article else 0.0

def article_similarity_v_1(article: str, _article: str) -> float:
    def get_keyword_frequency(article: str) -> Dict[str, int]:
        return {
            word: len(list(group))
            for (word, group) in groupby(
                sorted(
                    article['text'].split()
                )
            )
        }

    keywords, _keywords = map(
        get_keyword_frequency,
        (article, _article),
    )

    all_words = set(chain(keywords.keys(), _keywords.keys()))

    return average(
        [
            word in keywords and word in _keywords# and (keywords[word] == _keywords[word])
            for word in all_words
        ]
    )

SIMILARITY_THRESHOLD = 0.16

similarity_matrix_dict = {
    (article['link'], _article['link']): article_similarity_v_1(article, _article)
    for (article, _article) in combinations(all_articles, r=2)
}

def truncate_link(link: str, max_length: int = 50) -> str:
    link_basename = basename(link)
    if len(link_basename) <= max_length:
        return link_basename
    else:
        return link_basename[:max_length - 3] + '...'

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
