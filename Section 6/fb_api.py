# Facebook Post Phishing Susceptibility Analyzer
# This script analyzes public Facebook profiles for potential phishing vulnerabilities
# by extracting posts using Apify's Facebook scraper and analyzing them with OpenAI's GPT model.
# The results are displayed through a Streamlit web interface.

# Required Libraries
import streamlit as st  # For creating the web interface
from apify_client import ApifyClient  # For scraping Facebook posts
import openai  # For GPT-based text analysis
import os  # For environment variable handling

# Load API tokens from environment variables
# These tokens should be set in your environment for security
APIFY_API_TOKEN = os.getenv('APIFY_API_TOKEN')  # Token for Apify services
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')    # Token for OpenAI API access

# Initialize API clients
client = ApifyClient(APIFY_API_TOKEN)  # Set up Apify client for Facebook scraping
openai.api_key = OPENAI_API_KEY       # Configure OpenAI API access

def extract_facebook_posts(fb_url):
    """
    Extracts Facebook posts using Apify's Facebook Posts Scraper.
    
    Args:
        fb_url (str): URL of the public Facebook profile to analyze
        
    Returns:
        list: Collection of extracted posts, or None if extraction fails
    """
    try:
        # Configure the input for Apify's Facebook scraper
        run_input = {
            "startUrls": [{"url": fb_url}],
        }
        
        # Display progress indicator to user
        st.info("Extracting Facebook posts... This may take a few moments.")
        
        # Execute the Apify scraper and wait for results
        run = client.actor("apify/facebook-posts-scraper").call(run_input=run_input)
        
        # Verify successful data extraction
        if "defaultDatasetId" in run:
            dataset_id = run["defaultDatasetId"]
            # Retrieve all items from the dataset
            items = client.dataset(dataset_id).list_items().items
            return items
        else:
            # Handle cases where no data was extracted
            st.error("Dataset not found in the response. Please check the URL or permissions.")
            return None
            
    except Exception as e:
        # Handle any errors during the extraction process
        st.error(f"An error occurred while extracting posts: {e}")
        return None

def analyze_posts_with_llm(posts):
    """
    Analyzes Facebook posts for phishing susceptibility using OpenAI's GPT model.
    
    Args:
        posts (list): Collection of Facebook posts to analyze
        
    Returns:
        str: Analysis results from the GPT model, or None if analysis fails
    """
    try:
        # Format posts for analysis by combining all post texts
        post_texts = "\n\n".join([f"{i+1}. {post['text']}" for i, post in enumerate(posts)])
        
        # Construct the prompt for GPT analysis
        prompt = f"""
        Analyze the first two of the following Facebook posts for susceptibility to Phishing attacks based on the content shared. 
        Identify references of oversharing of personal information, tone, personal activity, location sharing, 
        or any other potential vulnerabilities. Also provide recommendations if anything should have been avoided in the post to avid Phishing attack possibilities. 
        Make the responses simple and crisp. 
        At the start of each of the Post analysis, please mention the first 10 words of the post so that we can identify the post directly. 
        Posts' contents: 
        {post_texts}
        """
        
        # Inform user of analysis progress
        st.info("Analyzing posts with LLM...")
        
        # Make API call to OpenAI's GPT model
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5 for analysis
            messages=[
                # Set up the AI's role and provide the analysis prompt
                {"role": "system", "content": "You are a Cybersecurity Expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500  # Limit response length
        )
        
        # Extract and return the analysis result
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # Handle any errors during the analysis process
        st.error(f"An error occurred during analysis: {e}")
        return None

# Streamlit Web Interface Setup
st.title("Facebook Post Phishing Susceptibility Analyzer")

# Create input field for Facebook URL
fb_url = st.text_input("Enter a public Facebook profile URL:")

# Create analysis trigger button
if st.button("Analyze"):
    if fb_url:
        # Execute the analysis pipeline if URL is provided
        posts = extract_facebook_posts(fb_url)
        if posts:
            # Display success message with post count
            st.success(f"Extracted {len(posts)} posts successfully!")
            
            # Perform and display analysis
            analysis = analyze_posts_with_llm(posts)
            if analysis:
                st.subheader("Phishing Susceptibility Analysis:")
                st.write(analysis)
    else:
        # Prompt user to enter URL if none provided
        st.warning("Please enter a valid Facebook profile URL.")