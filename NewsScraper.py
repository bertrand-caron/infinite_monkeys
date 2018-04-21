import feedparser as fp
import json
import newspaper
from newspaper import Article
from time import mktime
from datetime import datetime
from typing import List, Any, Dict
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

# Set the limit for number of articles to download
LIMIT = 99999

KEEP_ARTICLES_WITH_NO_DATE = True

def process_rss_entry(entry: Any, company: str) -> Any:
    if KEEP_ARTICLES_WITH_NO_DATE or (not KEEP_ARTICLES_WITH_NO_DATE and hasattr(entry, 'published')):
        article = {}
        article['link'] = entry.link
        try:
            date = entry.published_parsed
            article['published'] = datetime.fromtimestamp(mktime(date)).isoformat()
        except:
            article['published'] = None
        try:
            content = Article(entry.link)
            content.download()
            content.parse()
        except Exception as e:
            # If the download for some reason fails (ex. 404) the script will continue downloading
            # the next article.
            print(e)
            print("continuing...")
            return None
        article['title'] = content.title or entry.title
        article['text'] = content.text
        print("Article downloaded from", company, ", url: ", entry.link)
        return article

def get_articles_from_company(company: str, links_dict: Dict[str, str]) -> Any:
    count = 1
    # If a RSS link is provided in the JSON file, this will be the first choice.
    # Reason for this is that, RSS feeds often give more consistent and correct data.
    # If you do not want to scrape from the RSS-feed, just leave the RSS attr empty in the JSON file.
    if 'rss' in links_dict:
        d = fp.parse(links_dict['rss'])
        print("Downloading articles from ", company)
        with ThreadPool(1) as p:
            newsPaper = {
                "rss": links_dict['rss'],
                "link": links_dict['link'],
                "articles": list(
                    filter(
                        lambda article: article is not None,
                        p.starmap(
                            process_rss_entry,
                            [(entry, company) for (entry, _) in zip(d.entries, range(LIMIT))],
                        ),
                    ),
                ),
            }
    else:
        # This is the fallback method if a RSS-feed link is not provided.
        # It uses the python newspaper library to extract articles
        print("Building site for ", company)
        paper = newspaper.build(links_dict['link'], memoize_articles=False)
        newsPaper = {
            "link": links_dict['link'],
            "articles": []
        }
        noneTypeCount = 0
        for content in paper.articles:
            if count > LIMIT:
                break
            try:
                content.download()
                content.parse()
            except Exception as e:
                print(e)
                print("continuing...")
                continue
            # Again, for consistency, if there is no found publish date the article will be skipped.
            # After 10 downloaded articles from the same newspaper without publish date, the company will be skipped.
            if not KEEP_ARTICLES_WITH_NO_DATE and content.publish_date is None:
                print(count, " Article has date of type None...")
                noneTypeCount = noneTypeCount + 1
                if noneTypeCount > 10:
                    print("Too many noneType dates, aborting...")
                    noneTypeCount = 0
                    break
                count = count + 1
                continue
            article = {}
            article['title'] = content.title
            article['text'] = content.text
            article['link'] = content.url
            try:
                article['published'] = content.publish_date.isoformat()
            except:
                article['published'] = None
            newsPaper['articles'].append(article)
            print(count, "articles downloaded from", company, " using newspaper, url: ", content.url)
            count = count + 1
            noneTypeCount = 0
    return newsPaper

if __name__ == '__main__':
    # Loads the JSON files with news sites
    with open('NewsPapers.json') as data_file:
        companies = json.load(data_file)

    ordered_companies = list(companies.keys())

    with Pool(10) as p:
        articles_for_company = p.starmap(
            get_articles_from_company,
            companies.items(),
        )

    data = {
        'newspapers': {
            company: articles
            for (company, articles) in zip(ordered_companies, articles_for_company)
        }
    }

    # Finally it saves the articles as a JSON-file.
    try:
        with open('scraped_articles.json', 'w') as outfile:
            json.dump(data, outfile)
    except Exception as e:
        print(e)
        raise
