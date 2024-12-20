import requests
import json
import time
import pandas as pd
#  MediaStack API key
API_KEY = '939de3f5d7bcd9030de41c23754ec20b'

# API endpoint
BASE_URL = 'https://api.mediastack.com/v1/news'

# Function to fetch articles without pagination
def fetch_media_stack_articles():
    params = {
        'access_key': API_KEY,
        'keywords': ['transportation delay',"shipment delay"],
        "category":"business"  # Maximum articles to fetch
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


# Filter the required fields
def filter_mediastack_articles(data):
    if data and 'data' in data:
        filtered_articles = [
            {
                'source': article.get('source'),
                'publisher': article.get('author'),  # Using 'author' as a substitute for publisher
                'title': article.get('title'),
                'content': article.get('description'),  # 'description' used as content
                'language': article.get('language'),
                'date': article.get('published_at')
            }
            for article in data['data']
        ]

        # Save filtered articles to a JSON file
        output_file = 'media_stack_filtered_supply_chain_articles.json'
        with open(output_file, 'a') as file:
            json.dump(filtered_articles, file, indent=4)

        print(f"Total articles saved: {len(filtered_articles)}")
        print(f"Articles saved to {output_file}")
    else:
        print("No articles retrieved.")

media_stack_data = fetch_media_stack_articles()
media_stack=filter_mediastack_articles()
media_stack=pd.read_json(media_stack)
df=pd.DataFrame(media_stack)
print(df.describe())
print(df.info())
print(df.head())
#df.to_excel("media_stack_filtered_supply_chain_articles.xlsx")
df.to_csv("media_stack_articles.csv")





# Your API Key and Custom Search Engine ID
API_KEY = "AIzaSyBRu1jSldkSrJbWXcHPOWfy7s1K_TlvV54"
CSE_ID = "d03a2f288016547d9"

def search_engine_news(query, num_results=10000):
    url = "https://www.googleapis.com/customsearch/v1"
    results = []
    start_index = 1  # Start from the first result

    while len(results) < num_results:
        params = {
            "key": API_KEY,
            "cx": CSE_ID,
            "q": query,
            "num": 10,  # Maximum results per page
            "start": start_index,  # Starting index for the results
            "sort": "date",        # Optional: Sort results by date
              # Optional: Limit to the last month
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            if not items:  # Stop if no more results
                break

            results.extend(items)
            start_index += 10  # Move to the next page of results

            # Google API has a quota; wait to avoid rate limits
            time.sleep(1)  # Adjust as needed
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

    return results[:num_results]  # Return only the requested number of results

def filter_search_engine_news(results):
    total=0
    filtered_results = []
    for item in results:
        # Extract fields with fallbacks
        title = item.get("title", "No title")
        link = item.get("link", "No link")
        snippet = item.get("snippet", "No content")
        language=item.get("language", "unknown")
        country=item.get("country", "unknown")
        # Approximate publisher from the URL
        publisher = item.get("displayLink", "Unknown publisher")
        # Date is not always provided directly; estimate from the snippet or use external tools if available
        date = "Unknown date"  # Replace this with your date extraction logic if possible
        total=total+1
        filtered_results.append({
            "title": title,
            "url": link,
            "content": snippet,
            "publisher": publisher,
            "language":language,
            "country":country,
            "source": publisher,  # For simplicity, using publisher as source
        
        })
    return filtered_results

# Search query for supply chain news
querys = ["supply chain disruption","shipment delay","transportation delay"]
num_articles = 100
for query in querys:
    results = search_engine_news(query, num_articles)
    
    # Extract the relevant fields
    filtered_results =filter_search_engine_news(results)
    
    # Save results to a JSON file
    output_file = "custom_search_engine_news.json"
    with open(output_file, "a", encoding="utf-8") as file:
        json.dump(filtered_results, file, ensure_ascii=False, indent=4)

    print(f"Saved {len(filtered_results)} articles to {output_file}")

# Display the first few articles (optional)
    if filtered_results:
        for idx, article in enumerate(filtered_results[:5], start=1):  # Display only the first 5
            print(f"{idx}. {article['title']}\n   {article['url']}\n   {article['content']}\n")
    else:
        print("No results found.")
search_engine=pd.read_json("custom_search_engine_articles.json")
df1=pd.DataFrame(search_engine)
print(df1.describe())
print(df1.info())
print(df1.head())
#df1.to_excel("custom_search_engine_news.xlsx")
df1.to_csv("custom_search_engine_articles.json.csv")





def fetch_newsapi_articles(api_key, query, page_size=100, max_results=1000):
    url = "https://newsapi.org/v2/everything"
    all_articles = []
    page = 1

    # Fetch articles in pages, stopping once we have the desired number of results
    while len(all_articles) < max_results:
        params = {
            "q": query,         # Query for "supply chain" news
            "apiKey": api_key,# Your NewsAPI key
            #"from":2021-12-11
            #"pageSize": page_size,  # Max 100 articles per request
            #"page": page,       # Pagination (starting from page 1)
            #"language": "en"    # Optional: Filter for English articles
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            if not articles:
                break  # Stop if no articles are returned
            
            all_articles.extend(articles)
            page += 1  # Go to the next page
        else:
            print(f"Error: {response.status_code}")
            break  # Stop if an error occurs

    return all_articles

# Replace with your actual NewsAPI key
API_KEY = "271b4406b0f24a899c09bb77c3723780"
querys = ["shipment delay","supply chain disruption","transportation delay"]

for query in querys:
    all_articles = fetch_newsapi_articles(API_KEY, query, page_size=100, max_results=1000)
    
    # Create a DataFrame from the articles
    if all_articles:
        with open("newsapi_articles.json", "a", encoding="utf-8") as file:
            json.dump(all_articles, file, ensure_ascii=False, indent=4)
         # Display the first few rows
    else:
        print("No articles found!")
newsapi=pd.read_json("newsapi_articles.json")
df2=pd.DataFrame(newsapi)
df2.drop(columns=["urlToImage","source"],inplace=True)
df2["source"]=df2["publishedAt"]
df2.drop(columns=["publishedAt"],inplace=True)
#df2.to_excel("newsapi_articles.xlsx")
df2.to_csv("newsapi_articles.csv")
