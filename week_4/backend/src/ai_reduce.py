import os

import instructor
from dotenv import load_dotenv
from google import genai
from schemas import ArticleAnalysis, ConsensusOutput

load_dotenv()

client = instructor.from_genai(
    client=genai.Client(api_key=os.environ["GEMINI_API_KEY"]),
    mode=instructor.Mode.GENAI_STRUCTURED_OUTPUTS,
)

def run_reduce_phase(
    ticker: str,
    company_name: str,
    analyses: list[ArticleAnalysis],
) -> ConsensusOutput | None:
    """
    Synthesise all ArticleAnalysis results into a single ConsensusOutput.
    Returns None if synthesis fails.
    """
    if not analyses:
        return None

    analyses_text = ""
    for i, analysis in enumerate(analyses, 1):
        analyses_text += f"""
        Article {i}:
        - Source: {analysis.source}
        - Headline: {analysis.headline}
        - Sentiment: {analysis.sentiment.value} ({analysis.sentiment_score})
        - Core Argument: {analysis.core_argument}
        - Bull Points: {", ".join(analysis.bull_points)}
        - Bear Points: {", ".join(analysis.bear_points)}
        - Key Metrics: {", ".join(analysis.key_metrics)}
        """

    prompt = f"""
    You are a senior financial analyst specialising in Bursa Malaysia stocks.
    Below are analyses of {len(analyses)} news articles about {company_name} ({ticker}).

    {analyses_text}

    Based on all the above, synthesise a unified market consensus:
    - What is the overall market sentiment?
    - How confident is the consensus (0.0 = completely split, 1.0 = unanimous)?
    - What are the top bull case arguments across all sources?
    - What are the top bear case arguments across all sources?
    - What is the overall risk rating (low, medium, high)?
    - Write a plain English summary paragraph of the overall consensus.
    """

    try:
        result = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            response_model=ConsensusOutput,
            model="gemini-2.5-flash",
        )
        result.ticker = ticker
        result.company_name = company_name
        result.articles_analysed = len(analyses)
        result.sources = list({a.source for a in analyses})
        return result
    except Exception as e:
        print(f"Failed to synthesise consensus for {ticker}: {e}")
        return None