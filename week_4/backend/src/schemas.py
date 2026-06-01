from enum import Enum

from pydantic import BaseModel, Field


class Sentiment(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class RiskRating(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ArticleAnalysis(BaseModel):
    source: str = Field(description="Name of the news source e.g. The Edge Malaysia")
    headline: str = Field(description="Article headline")
    sentiment: Sentiment = Field(description="Overall sentiment of the article")
    sentiment_score: float = Field(
        description="Sentiment strength from 0.0 to 1.0", ge=0.0, le=1.0
    )
    core_argument: str = Field(
        description="The main point of the article in one sentence"
    )
    bull_points: list[str] = Field(
        description="Positive signals mentioned in the article"
    )
    bear_points: list[str] = Field(
        description="Negative signals or risks mentioned in the article"
    )
    key_metrics: list[str] = Field(
        description="Any financial figures mentioned e.g. revenue up 12%"
    )


class ConsensusOutput(BaseModel):
    ticker: str = Field(description="Stock ticker e.g. 1155 for Maybank")
    company_name: str = Field(
        description="Full company name e.g. Malayan Banking Berhad"
    )
    overall_sentiment: Sentiment = Field(
        description="Overall market consensus sentiment"
    )
    confidence_score: float = Field(
        description="How strongly sources agree, 0.0 to 1.0", ge=0.0, le=1.0
    )
    bull_case: list[str] = Field(
        description="Top reasons the market is optimistic"
    )
    bear_case: list[str] = Field(
        description="Top reasons the market is concerned"
    )
    risk_rating: RiskRating = Field(
        description="Overall risk level based on all sources"
    )
    summary: str = Field(
        description="One paragraph plain English summary of the consensus"
    )
    articles_analysed: int = Field(
        description="Number of articles successfully processed"
    )
    sources: list[str] = Field(
        description="List of source names used in this analysis"
    )