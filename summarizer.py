from NewsArticle import NewsArticle
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


summary_prompt_template = PromptTemplate(
    input_variables=["articles"],
    template="""
    You are an expert news summarizer. Summarize the following news articles in concise bullet points. For each article, include:
    - Title
    - Key highlights
    - URL
    Give me final result as HTML string
    Here is the data in the form of json with fields title, description, url
    and below is the data :
    {articles}
    """
)

llm = ChatGoogleGenerativeAI(
    model = "gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

def summarize_news(articles : list[NewsArticle]):
    chain = LLMChain(llm=llm, prompt = summary_prompt_template)
    summary = chain.run(articles = [article.__dict__ for article in articles])  
    return summary