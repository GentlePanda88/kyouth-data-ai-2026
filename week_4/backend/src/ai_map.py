import os

import instructor
from dotenv import load_dotenv
from google import genai
from schemas import ArticleAnalysis

load_dotenv()

client = instructor.from_genai(
    client=genai.Client(api_key=os.environ["GEMINI_API_KEY"]),
    mode=instructor.Mode.GENAI_STRUCTURED_OUTPUTS,
)


def analyse_article(source: str, headline: str, text: str) -> ArticleAnalysis | None:
    """
    Send a single article to Gemini and extract structured sentiment analysis.
    Returns None if the article fails to parse.
    """
    prompt = f"""
    You are a financial analyst specialising in Bursa Malaysia stocks.
    Analyse the following news article and extract structured information.

    Source: {source}
    Headline: {headline}
    Article Text: {text}

    Extract:
    - Overall sentiment (bullish, bearish, or neutral)
    - Sentiment score (0.0 = very bearish, 1.0 = very bullish, 0.5 = neutral)
    - Core argument of the article in one clear sentence
    - Bull points: specific positive signals mentioned
    - Bear points: specific risks or negative signals mentioned
    - Key metrics: any financial figures mentioned (revenue, profit, margins etc.)
    """

    try:
        result = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            response_model=ArticleAnalysis,
            model="gemini-2.5-flash",
        )
        result.source = source
        result.headline = headline
        return result
    except Exception as e:
        print(f"Failed to analyse article '{headline}': {e}")
        return None


def run_map_phase(articles: list[dict]) -> list[ArticleAnalysis]:
    """
    Run the Map phase across all fetched articles.
    Returns only successfully analysed articles.
    """
    results = []

    for article in articles:
        analysis = analyse_article(
            source=article["source"],
            headline=article["headline"],
            text=article["text"],
        )
        if analysis is not None:
            results.append(analysis)

    return results