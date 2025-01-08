
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

        prompt = f"""Analyze the following news article for electric atteries supply chain risks.
        1. Material Availability and Resource Scarcity
- Critical Materials: Lithium, cobalt, nickel, and rare earth elements are essential for EV batteries. Limited global reserves and geographic concentration increase vulnerability.
- Geopolitical Factors: A significant share of mining occurs in politically unstable regions, such as cobalt mining in the Democratic Republic of Congo (DRC).
- Competition for Resources: Growing global demand for these materials, driven by the EV boom and other industries, can strain supplies.
2. Environmental and Social Concerns
- Mining Practices: Extracting critical minerals can lead to deforestation, water pollution, and other environmental damage.
- Labor Issues: Cobalt mining, in particular, has been associated with child labor and poor working conditions.
- Sustainability Pressure: Consumers and regulators increasingly demand ethically sourced and environmentally friendly materials.
3. Refining and Processing Bottlenecks
- Geographic Concentration: A significant share of battery material processing occurs in China, creating potential risks due to geopolitical tensions or trade restrictions.
- Infrastructure Gaps: Countries lacking refining infrastructure are dependent on imports, increasing costs and delays.
4. Technological and Manufacturing Risks
- Technology Dependence: Battery production relies on advanced manufacturing technologies and expertise, which are not uniformly distributed globally.
- Quality and Reliability: Poor-quality materials or defects during manufacturing can lead to safety issues, such as battery fires or performance degradation.
5. Supply Chain Disruption
- Pandemics: COVID-19 highlighted vulnerabilities in global supply chains, including delays in material sourcing and component delivery.
- Natural Disasters: Earthquakes, floods, and other disasters can disrupt mining, transportation, and manufacturing.
- Cybersecurity Threats: Increasing digitization of supply chains introduces risks of cyberattacks on critical infrastructure.
6. Regulatory and Trade Challenges
- Export Controls: Countries with critical resources may impose export restrictions to prioritize domestic industries.
- Tariffs and Trade Wars: Geopolitical conflicts can result in tariffs or trade barriers, increasing costs.
- Regulatory Compliance: Meeting evolving global standards for environmental and social governance (ESG) practices can be costly and complex.
7. Transportation and Logistics
- Global Dependence: Battery components often travel thousands of miles before assembly, increasing risks of delays and carbon emissions.
- High Costs: Shipping costs for heavy materials like lithium carbonate can be substantial.
- Infrastructure Challenges: Inadequate transportation infrastructure in key mining regions can slow supply chain flows.


       

        Article: {truncated_content}

        Provide a structured analysis of the identified risks and their potential impact on the Medicine supply chain."""

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
