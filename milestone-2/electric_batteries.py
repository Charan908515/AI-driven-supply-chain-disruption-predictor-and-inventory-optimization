
import requests
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from groq import Groq
from transformers import pipeline, AutoTokenizer
from eventregistry import *

# API Configuration
GROQ_API_KEY = "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"
EVENT_REGISTRY_API_KEY = "ec2c22cd-4147-4ad3-a255-6a771011a513"

# Model names
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"

def fetch_news(max_items=100):
    try:
        # Initialize EventRegistry
        er = EventRegistry(apiKey=EVENT_REGISTRY_API_KEY)

        # Create query for articles
        q = QueryArticlesIter(
            keywords= "electric batteries supply chain",
            dateStart=(dt.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            dateEnd=dt.now().strftime('%Y-%m-%d'),
            dataType=["news", "blog"],
            lang="eng"
        )

        # Fetch articles with a limit on the number of results
        articles = []
        for article in q.execQuery(er, sortBy="date", maxItems=max_items):
            articles.append(article)

        return {"articles": {"results": articles}}
    except Exception as e:
        print(f"Error fetching news: {e}")
        return None

def initialize_groq():
    return Groq(api_key=GROQ_API_KEY)



def truncate_for_llama(text, max_length=900):
    """Truncate text for LLaMA model"""
    words = text.split()
    if len(words) > max_length:
        return ' '.join(words[:max_length]) + "..."
    return text

# Function to fetch news data from Event Registry


# Risk analysis with Groq LLaMa
def analyze_risk_with_llama(content, client):
    try:
        truncated_content = truncate_for_llama(content)

        prompt = f"""You are a supply chain risk analyst specializing in electric vehicle (EV) batteries. Below is a news article about the EV battery supply chain. Based on the information in the article, identify and analyze the supply chain risks specifically for EV batteries. Use the following risk categories to structure your analysis:
1. Raw Material Supply Risks
   - Dependency on critical minerals like lithium, cobalt, and nickel.
   - Geographic concentration of mining and processing facilities.
2. Supplier Dependency
   - Reliance on a limited number of battery manufacturers or suppliers.
   - Risks associated with quality control and delivery timelines.
3. Production and Manufacturing Risks
   - Issues in scaling battery production to meet demand.
   - Challenges related to advanced battery technology adoption (e.g., solid-state batteries).
4. Transportation and Logistics Risks
   - Delays or damages during the shipment of batteries or raw materials.
   - Hazardous material handling regulations affecting transport.
5. Regulatory and Compliance Risks
   - Adherence to safety, environmental, and trade policies.
   - Regional restrictions on battery materials and recycling practices.
6. Technological Risks
   - Rapid advancements in battery technology making current products obsolete.
   - Cybersecurity risks in smart battery systems.
7. Demand and Market Risks
   - Fluctuations in demand for specific battery chemistries or capacities.
   - Price pressures due to competition or market saturation.
8. Environmental and Natural Disasters
   - Climate events disrupting mining, production, or logistics.
   - Long-term environmental concerns related to resource extraction and battery disposal.

Provide a detailed assessment of the risks highlighted or implied in the article and suggest potential mitigation strategies.
NEWS ARTICLE:{truncated_content}
"""

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False
        )

        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error with Groq LLaMa: {e}")
        return "Error in risk analysis"
  
def initialize_sentiment_analyzer():
    tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL)
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model=SENTIMENT_MODEL,
        tokenizer=tokenizer,
        device=-1
    )
    return sentiment_pipeline, tokenizer
  
def truncate_for_model(text, tokenizer, max_length=512):
    """Truncate text to fit within model's token limit"""
    tokens = tokenizer.encode(text, truncation=False)
    if len(tokens) > max_length:
        tokens = tokens[:max_length-1] + [tokenizer.sep_token_id]
        text = tokenizer.decode(tokens, skip_special_tokens=True)
    return text


# Sentiment analysis with proper truncation
def analyze_sentiment_with_model(content, sentiment_pipeline, tokenizer):
    try:
        # Properly truncate content for the model
        truncated_content = truncate_for_model(content, tokenizer)

        # Get sentiment prediction
        result = sentiment_pipeline(truncated_content)[0]

        # Format the result
        return {
            "label": result["label"],
            "score": float(result["score"]),
            "analysis": f"Sentiment: {result['label']} (confidence: {result['score']:.2f})"
        }
    except Exception as e:
        print(f"Error with sentiment analysis: {e}")
        return {
            "label": "ERROR",
            "score": 0.0,
            "analysis": "Error in sentiment analysis"
        }


def compute_risk_score(risk_analysis):
    """
    Compute a normalized risk score based on extracted factors from risk analysis.
    """
    try:
        # Example scoring logic: count risk-related keywords
        high_risk_keywords = ["scarcity", "shortage", "critical", "geopolitical", "disruption", "instability"]
        low_risk_keywords = ["available", "sustainable", "abundant", "resolved"]

        high_risk_count = sum(risk_analysis.lower().count(word) for word in high_risk_keywords)
        low_risk_count = sum(risk_analysis.lower().count(word) for word in low_risk_keywords)

        # Normalize score to be between -1 and 1
        risk_score = (low_risk_count - high_risk_count) / max((high_risk_count + low_risk_count + 1), 1)
        return round(risk_score, 2)  # Limit to two decimal places
    except Exception as e:
        print(f"Error in computing risk score: {e}")
        return 0.0  # Default neutral score

# Aggregate data into structured format
def aggregate_data(news_data):
    try:
        structured_data = []
        for article in news_data.get('articles', {}).get('results', []):
            structured_data.append({
                "source": article.get('source', {}).get('title', ''),
                "title": article.get('title', ''),
                "description": article.get('body', ''),
                "content": article.get('body', ''),
                "published_at": article.get('dateTime', '')
            })
        return pd.DataFrame(structured_data)
    except Exception as e:
        print(f"Error structuring data: {e}")
        return None

# Main pipeline
def main():
    # Initialize models
    # Initialize models
    groq_client = initialize_groq()
    sentiment_pipeline, tokenizer = initialize_sentiment_analyzer()

    # Fetch news data
    news_data = fetch_news(max_items=10)
    if not news_data:
        return

    # Aggregate data into structured format
    structured_data = aggregate_data(news_data)
    if structured_data is None or structured_data.empty:
        print("No data to analyze")
        return

    # Analyze risk and sentiment
    results = []
    for idx, row in structured_data.iterrows():
        print(f"\nAnalyzing article {idx + 1}/{len(structured_data)}: {row['title']}")

        # Perform analyses
        risk_analysis = analyze_risk_with_llama(row['content'], groq_client)
        sentiment_analysis = analyze_sentiment_with_model(row['content'], sentiment_pipeline, tokenizer)
        risk_score=compute_risk_score(risk_analysis)
        # Store results
        results.append({
            'Title': row['title'],
            'Source': row['source'],
            'Published At': row['published_at'],
            'Sentiment': sentiment_analysis['label'],
            'Sentiment Score': sentiment_analysis['score'],
            'Sentiment Analysis': sentiment_analysis['analysis'],
            'Risk Analysis': risk_analysis,
            "risk score": risk_score
        })

    # Save results to CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv("Risk_and_Sentiment_Results.csv", index=False, encoding='utf-8')

    print("Analysis saved to Risk_and_Sentiment_Results.csv")

if __name__ == "__main__":
    main()
