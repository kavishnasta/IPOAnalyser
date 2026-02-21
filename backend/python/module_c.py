import sys
import json
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time

def scrape_reddit_mentions(company_name, limit=100):
    mentions = []
    try:
        url = f"https://www.reddit.com/r/IndianStreetBets/search.json"
        params = {
            'q': company_name,
            'limit': min(limit, 100),
            'sort': 'relevance',
            'restrict_sr': 'true'
        }
        headers = {
            'User-Agent': 'IPO-Screener-Bot/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'children' in data['data']:
                for post in data['data']['children']:
                    if 'data' in post:
                        title = post['data'].get('title', '')
                        selftext = post['data'].get('selftext', '')
                        mentions.append(title + ' ' + selftext)
    except Exception:
        pass
    
    return mentions

def scrape_news_headlines(company_name, limit=50):
    headlines = []
    try:
        search_query = f"{company_name} IPO India"
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': search_query,
            'language': 'en',
            'sortBy': 'relevance',
            'pageSize': min(limit, 50)
        }
        headers = {
            'User-Agent': 'IPO-Screener-Bot/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'articles' in data:
                for article in data['articles']:
                    title = article.get('title', '')
                    description = article.get('description', '')
                    headlines.append(title + ' ' + description)
    except Exception:
        pass
    
    return headlines

def calculate_sentiment_score(texts):
    analyzer = SentimentIntensityAnalyzer()
    scores = []
    
    for text in texts:
        if text and text.strip():
            score = analyzer.polarity_scores(text)
            scores.append(score['compound'])
    
    if scores:
        avg_score = sum(scores) / len(scores)
        return avg_score
    return 0.0

if __name__ == '__main__':
    company_name = sys.argv[1] if len(sys.argv) > 1 else ''
    
    if not company_name:
        result = {
            'vaderScore': 0.0,
            'redditMentions': 0,
            'newsHeadlines': 0
        }
    else:
        reddit_mentions = scrape_reddit_mentions(company_name)
        news_headlines = scrape_news_headlines(company_name)
        
        all_texts = reddit_mentions + news_headlines
        vader_score = calculate_sentiment_score(all_texts)
        
        result = {
            'vaderScore': round(vader_score, 4),
            'redditMentions': len(reddit_mentions),
            'newsHeadlines': len(news_headlines)
        }
    
    print(json.dumps(result))
