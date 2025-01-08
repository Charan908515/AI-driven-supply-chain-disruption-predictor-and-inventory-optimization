# AI-driven-supply-chain-disruption-predictor-and-inventory-optimization:

## STEP-1: COLLECTING DATA  
In this step the data is collected in form of news articles by using apis of Media Stack and NewsApi and also created a custom search engine that search for the news articles from news pages like bbc,cnn etc. based on the given query,to get more articles  include the pagination so that it collect more articles for each api request.The articles are saved in json format,after filtering the json to extract the required data like content,publisher,date etc..,the filtered data is saved in both json and csv format for future use.  

You can use the apis by refering the below documentation link for both newsapi and media stack:  
 * Newsapi:https://newsapi.org/docs/get-started  
*  MediaStack:https://mediastack.com/documentation   

*  For creating a custom search engine:   
     * Step 1: Create a Custom Search Engine   
          * Go to the Google Custom Search Engine (CSE) website.   
          * Click on "Get started".   
          * Specify the sites you want to search or choose "Search the entire web".   
          * Complete the setup and make a note of your CSE ID.
      
    * Step 2: Get API Access    
        * Go to the Google Cloud Console.   
        * Create a new project or select an existing project.      
        * Navigate to APIs & Services > Library.   
        * Search for Custom Search JSON API and enable it.      
        * Go to APIs & Services > Credentials:    
        * Click Create Credentials > API Key.     
        * Copy your API Key.    
     * Step 3: Configure CSE for API Use     
        * In the CSE control panel, go to the Custom Search Engine you created.    
       *  Click Settings > Search features:   
       *  Adjust the settings (e.g., site restrictions, layout, etc.).    
       *  Make sure the Search engine ID matches your API usage     
     * Step 4: Use the API    
        * Use the Custom Search JSON API to programmatically access the search engine. Here's an example of a search query:    
        * API Endpoint:https://www.googleapis.com/customsearch/v1    
        * Required Parameters:    
           *  key: Your API Key.    
            * cx: Your Custom Search Engine ID.    
           *  q: The search query.
  ## STEP-2:ANALYSING THE ARTICLES USING LLM'S:
  ### Electric Vehicle Battery Supply Chain Risk & Sentiment Analysis

This project analyzes news articles related to the electric vehicle (EV) battery supply chain. It integrates sentiment analysis and risk assessment to extract insights, compute risk scores, and save the results for further analysis.

### Features

1. **News Fetching**:

   - Retrieves articles using the Event Registry API.
   - Filters articles by keywords, date range, and language.

2. **Risk Analysis**:

   - Utilizes the Groq LLaMa model for structured risk analysis.
   - Focuses on key EV battery supply chain risks, including raw material dependencies, supplier issues, and technological challenges.

3. **Sentiment Analysis**:

   - Uses Hugging Face's `distilbert-base-uncased-finetuned-sst-2-english` model.
   - Evaluates sentiment and provides a confidence score.

4. **Risk Scoring**:

   - Computes a normalized risk score based on the occurrence of high-risk and low-risk keywords.

5. **Data Aggregation**:

   - Aggregates results into a structured pandas DataFrame.
   - Saves the output to a CSV file.

### Models Used

1. **Groq LLaMa**:
   - A state-of-the-art language model used for detailed and structured risk analysis.
   - Provides contextual insights specific to EV battery supply chain challenges.
   - **Why Chosen**: This model excels in generating in-depth, domain-specific analyses, making it ideal for identifying nuanced risks within the EV battery supply chain.

2. **Hugging Face Sentiment Model**:
   - `distilbert-base-uncased-finetuned-sst-2-english`:
     - A lightweight transformer model fine-tuned for sentiment analysis.
     - Offers high accuracy in classifying text as positive or negative.
   - **Why Chosen**: This model provides a balance of speed and accuracy, making it well-suited for processing multiple articles efficiently while maintaining reliable sentiment evaluation.

### Configuration

- Modify the `fetch_news` function to change:

  - Keywords: Update the `keywords` parameter.
  - Date Range: Adjust the `dateStart` and `dateEnd` parameters.

- Adjust sentiment model or tokenizer if needed in `initialize_sentiment_analyzer`.

### Output

The results are saved to `Risk_and_Sentiment_Results.csv` with the following columns:

- **Title**: Title of the article.
- **Source**: Source of the article.
- **Published At**: Publication date.
- **Sentiment**: Sentiment label (e.g., Positive, Negative).
- **Sentiment Score**: Sentiment confidence score.
- **Sentiment Analysis**: Summary of sentiment analysis.
- **Risk Analysis**: Detailed risk assessment.
- **Risk Score**: Computed risk score (-1 to 1).

### Dependencies

- Python 3.8+
- `requests`
- `pandas`
- `datetime`
- `transformers`
- `eventregistry`





