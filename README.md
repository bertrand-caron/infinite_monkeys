# The Problem

A key aspect of evaluating news is determining its source. Primary sources, the original eyewitness reports of an event, should take priority over secondary sources (reports by others based on previous accounts). Identifying sources is also helpful for determining the likely biases that shape particular news reports. As the news source is important for verifying its credibility, those with an interest in promoting a specific interpretation of events may obscure the original source of news it promotes.

While we would expect some similarity between accounts of the same event, identical or highly similar news articles appearing in multiple sources (almost) simultaneously without a common attribution suggests a common link between these sources. This source may be content from an attributed common supplier (such as news agencies like the Associated Press (AP), Reuters, and Agence France-Presse (AFP)) or a hidden common source, such as an organised misinformation or propaganda campaign.

# Our Response

Our project addresses these concerns by searching for similarities between news stories. Extensive amounts of common text within news articles from different sources suggests that the stories have a common origin. By comparing the publishing times of news stories, we can track the spread of a common news item across different sources, and hopefully identify its original source.

# The Project

The project has three components: data gathering, analysis, and visualisation. It has a Python 3 backend that gathers the data and performs the analysis, and a JavaScript frontend that displays the results. It requires the Python 3 libraries `numpy`, `feedparser`, and `newspaper3k`. To run it locally, first you need to either create a list of RSS feeds in a JSON file named `NewsPapers.json`.

## Data Gathering

The data source used is [News API](https://newsapi.org/), which gathers data from over 30,000 sources.

The data gathering code is based on [NewsScraper](https://github.com/holwech/NewsScraper).

## Analysis

> def article_similarity_v_2(article_word_dict: str, _article_word_dict: str) -> float:    
>    word_set, _word_set = map(set, (article_word_dict, _article_word_dict))  
>    try:  
>        return len(word_set & _word_set) / len(word_set | _word_set)  
>    except ZeroDivisionError:  
> return -1000.  

## Visualisation

Our data visualisation uses the [D3](www.d3js.org) JavaScript framework. Articles with a high similarity (>75%) are connected with a thick line. Articles with smaller similiarity values have thinner lines connecting them.

# "Infinite Monkeys?"

The project name comes from the adage that an infinite number of monkeys typing at an infinite number of typewriters will produce the works of Shakespeare. 

This project began at the [2018 Brisbane Internet Freedom Hack: Defending Truth](https://internetfreedomhack.org/brisbane).
