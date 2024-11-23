from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from google.oauth2.credentials import Credentials
import os
import http.client
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import urllib.parse
import json
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./news_agent.json"
os.environ["creds"] = "./credentials.json"
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from google_auth_oauthlib.flow import InstalledAppFlow
import json

load_dotenv()

app = FastAPI()

LANGCHAIN_TRACING_V2=True
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="LANGCHAIN_API_KEY"
LANGCHAIN_PROJECT="news-agent"

llm = ChatGoogleGenerativeAI(
    model = "gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

summary_prompt_template = PromptTemplate(
    input_variables=["articles"],
    template="""
    You are an expert news summarizer. Summarize the following news articles in concise bullet points. For each article, include:
    - Title
    - Key highlights
    - URL
    Here is the data:
    {articles}
    """
)

@app.get("/get_top_news")
def fetch_top_news():
    API_URL = os.getenv("MEDIASTACK_API_URL")
    API_KEY = os.getenv("MEDIASTACK_API_KEY")

    if not API_URL or not API_KEY:
        raise HTTPException(status_code=500, detail="API URL or API Key not set in environment variables")

    api_connection = http.client.HTTPSConnection(API_URL)

    now = datetime.utcnow().date()
    yesterday = (datetime.utcnow() - timedelta(days=1)).date()

    params = urllib.parse.urlencode({
        "access_key": API_KEY,
        "categories": "general",
        "sort": "published_desc",
        "limit": 5,
        "languages": "en",
        "date": f"{yesterday},{now}",
    })

    api_connection.request("GET", f"/v1/news?{params}")
    response = api_connection.getresponse()
    if response.status != 200:
        raise HTTPException(status_code=response.status, detail="Failed to fetch news from MediaStack API")

    data = response.read()
    json_data = json.loads(data.decode("utf-8"))

    filtered_news = []
    for article in json_data.get("data", []):
        filtered_news.append({
            "title": article.get("title", "No Title"),
            "description": article.get("description", "No Description"),
            "url": article.get("url", "No URL"),
            "image": article.get("image", None)  
        })

    return filtered_news

def preprocess_articles(articles):
    formatted_articles = []
    for article in articles:
        title = article.get("title", "No Title")
        description = article.get("description", "No Description")
        url = article.get("url", "No URL")
        formatted_articles.append(
            f"Title: {title}\nDescription: {description}\nURL: {url}"
        )
    return "\n\n".join(formatted_articles)


@app.post("/summarize_news")
def summarize_news():
    # Fetch top news
    articles = fetch_top_news()
    
    # Preprocess articles into formatted string
    formatted_articles = preprocess_articles(articles)
    
    # Generate summaries using LLM chain
    chain = LLMChain(llm=llm, prompt=summary_prompt_template)
    summary = chain.run(articles=formatted_articles)
    
    return {"summaries": summary}

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
def authenticate_user(credentials_path, token_path):
    # Start the OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the credentials to a file
    with open(token_path, 'w') as token_file:
        token_file.write(creds.to_json())
    print("Authentication successful. Token saved to:", token_path)

# Provide the path to your OAuth client JSON file
# authenticate_user("credentials.json", "token.json")


import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load credentials from token.json
def load_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.send'])
    return creds

# Send email function
def send_email(sender, to, subject, body):
    creds = load_credentials()

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid credentials available. Please authenticate.")
            return

    try:
        # Build the Gmail API service
        service = build('gmail', 'v1', credentials=creds)

        # Create the email message
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        msg = MIMEText(body)
        message.attach(msg)

        # Encode the message as base64url
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the email
        message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        print(f"Message sent successfully with ID: {message['id']}")

    except HttpError as error:
        print(f"An error occurred: {error}")

send_email("parkhigoyal46@gmail.com", "parkhig.ee.21@nitj.ac.in", "Test Email", "This is a test email from the News Agent API")





  