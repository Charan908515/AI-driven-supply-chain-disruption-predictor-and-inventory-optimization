# AI-driven-supply-chain-disruption-predictor-and-inventory-optimization:

## step-1: Collecting data  
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



