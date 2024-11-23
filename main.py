from fastapi import FastAPI
from dotenv import load_dotenv
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./news_agent.json"
os.environ["creds"] = "./credentials.json"
from fetch_news import fetch_top_news
from summarizer import summarize_news
from send_email import send_email
load_dotenv()

app = FastAPI()

@app.get("/get_top_news")
def get_top_news():
    return fetch_top_news()


@app.get("/get_news_summary")
def get_summarized_news(toEmail : str):
    top_news = fetch_top_news()
    summarized_news = summarize_news(top_news)
    send_email("parkhigoyal46@gmail.com",toEmail, "Top Daily News", summarized_news)
    return summarized_news







  