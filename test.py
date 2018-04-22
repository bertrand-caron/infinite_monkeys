from typing import Dict, List
from functools import reduce, lru_cache
from itertools import combinations, groupby, chain
from json import loads, dumps
import unittest
from numpy import average
from os.path import basename, dirname
from pprint import pprint
from operator import itemgetter

DEBUG = False

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
    return link
    if link.endswith('/'):
        link = link[:-1]
    if link.endswith('index.html'):
        link_basename = basename(dirname(link))
    else:
        link_basename = basename(link)

    if len(link_basename) <= max_length:
        return link_basename
    else:
        return link_basename[:max_length - 3] + '...'

def main():
    with open('scraped_articles.json') as fh:
        data = loads(fh.read())

    with open('articles_V2.json') as fh:
        data_V2 = loads(fh.read())

    all_articles = list(
        {
            article['link']: article
            for article in (
#                reduce(
#                    lambda acc, e: acc + e,
#                    [
#                        newspaper_dict['articles']
#                        for newspaper, newspaper_dict in data['newspapers'].items()
#                    ],
#                    []
#                )
#                +
                data_V2
            )
        }.values(),
    )

    article_title_for = {
        article['link']: article['title']
        for article in all_articles
    }

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

    KEEP_N = 50
    THRESHOLD = 0.25

    similarity_matrix_dict = {
        (article['link'], _article['link']): article_similarity_v_2(
            keyword_frequency_for_link[article['link']],
            keyword_frequency_for_link[_article['link']],
        )
        for (article, _article) in combinations(all_articles, r=2)
    }

    similarity_matrix_dict = dict(
        filter(
            lambda I: I[1] != 1.0,
            similarity_matrix_dict.items(),
        ),
    )

    similarity_threshold = sorted(
        similarity_matrix_dict.items(),
        key=itemgetter(1),
    )[-KEEP_N][1]

    pprint(
        sorted(
            similarity_matrix_dict.items(),
            key=itemgetter(1),
        )[-KEEP_N:]
    )

    links = reduce(
        lambda acc, e: acc | e,
        [
            frozenset((article, _article))
            for ((article, _article), similarity_score) in similarity_matrix_dict.items()
            if similarity_score >= similarity_threshold
        ],
        frozenset(),
    )

    def on_journal(article_link: str) -> str:
        try:
            _, url = article_link.split('://')
            base_url, *_ = url.split('/')
            return base_url
        except:
            raise Exception('In: {0}'.format(article_link))

    assert all('://' in article['link'] for article in all_articles), [
        (article['link'],) for article in all_articles
        if '://' not in article['link']
    ]

    journal_colors = {
        key: i
        for (i, (key, group)) in enumerate(
            groupby(
                sorted(
                    links,
                    key=on_journal,
                ),
                key=on_journal,
            )
        )
    }

    colors = {
        article_link: journal_colors[on_journal(article_link)]
        for article_link in links
    }

    with open('journals.json', 'wt') as fh:
        fh.write(
            dumps(
                journal_colors,
            ),
        )

    with open('journals.html', 'wt') as fh:
        fh.write(
            ''.join(['<p>{0}: {1}</p>'.format(journal, journal_color) for (journal, journal_color) in journal_colors.items()])
        )

    with open('news_articles_.json', 'wt') as fh:
        fh.write(
            dumps(
                {
                    'nodes': [
                        {'id': truncate_link(article['link']), 'group': colors[article['link']], 'title': article_title_for[article['link']]}
                        for article in all_articles
                        if article['link'] in links
                    ],
                    'links': [
                        {'source': truncate_link(article), 'target': truncate_link(_article), 'value': similarity_score}
                        for ((article, _article), similarity_score) in similarity_matrix_dict.items()
                        if article in links and _article in links and similarity_score >= THRESHOLD
                    ],
                },
                indent=True,
            ),
        )

if __name__ == '__main__':
    main()
