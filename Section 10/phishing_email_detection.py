# This program takes in an Email body and evaluates whether or not it be deemed a potential Phishing threat

import openai
import re
from urllib.parse import urlparse
import requests
import streamlit as st

# Set your OpenAI API key here
openai.api_key = '<my API Key>'

# Function to analyze email body for potential phishing
def analyze_email(email_body):
    # Placeholder for your existing logic to analyze the email body
    # Assuming a call to an OpenAI model here
    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"Analyze this email for potential phishing content: {email_body} and provide an analysis.",
        max_tokens=500
    )
    return response.choices[0].text.strip()

# Streamlit UI setup
st.title("Phishing Email Detection")

# Input for email body
email_body = st.text_area("Enter the email body:")

if st.button("Analyze Email"):
    if email_body.strip():
        try:
            # Analyze the email body
            result = analyze_email(email_body)
            st.subheader("Analysis Result:")
            st.write(result)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter the email body to analyze.")
