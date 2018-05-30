from typing import Dict
from itertools import groupby

def get_word_frequency(article_text: str) -> Dict[str, int]:
    '''
        Returns the frequency of all words (lowercased) in a string.
    '''
    return {
        word: len(list(group))
        for (word, group) in groupby(
            sorted(
                map(lambda s: s.lower(), article_text.split()),
            )
        )
    }

def article_similarity(article_word_dict: Dict[str, int], _article_word_dict: Dict[str, int]) -> float:
    '''
    Given two word distributions, return the percentage of words present in both distributions.
    '''
    word_set, _word_set = map(set, (article_word_dict, _article_word_dict))
    try:
        return len(word_set & _word_set) / len(word_set | _word_set)
    except ZeroDivisionError:
        # Case where both articles are empty
        return 0.0
