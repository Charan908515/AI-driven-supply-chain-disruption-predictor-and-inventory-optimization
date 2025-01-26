# AI-driven-supply-chain-disruption-predictor-and-inventory-optimization:

## MILESTONE-1: COLLECTING DATA  
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
  ## MILESTONE-2:ANALYSING THE ARTICLES USING LLM'S:
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
## MILESTONE-3:INVENTORY MANAGEMENT SYSTEM

  This is a Flask-based application for managing inventory, analyzing risks, and visualizing stock adjustments. The application uses SQLite for data storage and integrates various functionalities such as data import/export, risk analysis, and damage logging.

### Features
#### Core Features
* Inventory Management:

    * Add, delete, and update products.
    * Store product information, including company, cost price, selling price, stock levels, and more.
    * Risk Analysis and Stock Adjustment:

    * Adjust inventory levels based on risk predictions.
    * Generate stock adjustment reports and alerts (e.g., "buy", "sell", "monitor").
*Data Import and Export:

    * Import data from .csv and .xlsx files.
    * Export inventory data to Excel files.
    * Visualization:

* Visualize stock levels by company.
    * Visualize stock adjustments per company.
* Damage Logging:

    * Log damaged items, including reasons, quantities, and reporting dates.
    * View detailed damage logs.
* API Endpoints:

    * Fetch inventory data in JSON format.
    * Log and retrieve damaged product logs via API calls.
* Database Structure
    * 1. Products Table (products.db)
        * Fields:

            * product_id: Integer (Primary Key)
            * company: Text
            * month: Text
            * cost_price: Integer
            * selling_price: Integer
            * country: Text
            * stock_level: Integer
    * 2. Adjusted Inventory Table (adjusted_data.db)
        * Fields:
    
            * id: Integer (Primary Key)
            * product_id: Integer
            * company: Text
            * country: Text
            * stock_level: Integer
            * stock_adjusted: Integer
            * adjustment: Float
            * month: Text
            * reason: Text
            * alert: Text
    * 3. Damaged Logs Table (damaged_logs.db)
        * Fields:
    
            * id: Integer (Primary Key)
            * product_id: Integer
            * company: Text
            * country: Text
            * damage_reason: Text
            * quantity: Integer
            * reported_date: Text
            
* Endpoints
    * Web Endpoints
        * / - Homepage (View products).
        * /add - Add a new product (POST).
        * /delete/<int:product_id> - Delete a product (POST).
        * /export - Export data to an Excel file (POST).
        * /import - Import data from .csv or .xlsx files (POST).
        * /visualize/inventory - Visualize stock levels by company (GET).
        * /visualize/adjusted_inventory - Visualize stock adjustments (GET).
    * API Endpoints
        * /api/products - Fetch all products (GET).
        * /log_damage - Log damaged product (POST).
        * /get_damaged_logs - Fetch all damaged product logs (GET).



* Risk Analysis Integration
The app integrates with an external module (electric_batteries) to perform risk analysis and adjust inventory. Risk levels determine stock adjustment as follows:

    * High Risk: Decrease stock by 30% and set alert as "sell".
    * Moderate Risk: No adjustment, set alert as "monitor".
    * Low Risk: Increase stock by 10% and set alert as "buy".
* Visualization
    * Stock and adjustment data are visualized using Matplotlib.
    * Graphs are dynamically rendered and embedded in the application.
## MILESTONE-4: Sending Alerts through GMAIL and SLACK
### Features
* 1. Risk-Based Inventory Alerts
        * Fetches risk data from external modules.
        * Matches inventory data with risk levels to generate actionable alerts.
* 2. Automated Email Notifications
        * Sends detailed alerts via email to notify stakeholders about necessary actions.
* 3. Slack Notifications
        * Sends alert summaries to a specified Slack channel using a webhook.
### How It Works:
* Risk Analysis:Risk data is fetched using the electric_batteries module.Risk scores are computed for products based on analysis of relevant risk data.
* Alert Levels:
    * Sell: High risk and stock levels above a threshold.
    * Buy: Low/moderate risk and stock levels below a threshold.
    * Monitor: High risk with manageable stock or stable conditions.
* Database Interaction:
    * Uses SQLite for managing product data and adjusted inventory levels.
* Notification Delivery:
    * Alerts are sent via Gmail SMTP for email and a Slack webhook for Slack notifications.

