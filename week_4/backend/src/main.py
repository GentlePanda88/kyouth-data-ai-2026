import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import database
from ai_map import run_map_phase
from ai_reduce import run_reduce_phase
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ingestion import fetch_articles, get_company_name, is_supported
from schemas import ConsensusOutput

load_dotenv()

app = FastAPI(
    title="Sentinel Market Consensus Engine",
    description="AI-powered Bull/Bear consensus for Bursa Malaysia stocks",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

database.init_db()


@app.get("/")
def root():
    return {"message": "Sentinel API is running"}


@app.get("/consensus/{ticker}", response_model=ConsensusOutput)
def get_consensus(ticker: str, refresh: bool = False):
    """
    Get Bull/Bear consensus for a Bursa Malaysia ticker.
    Use ?refresh=true to force a fresh analysis instead of using cache.
    """
    ticker = ticker.strip()

    if not is_supported(ticker):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Ticker '{ticker}' is not supported. "
                "Please use a valid KLCI ticker."
            ),
        )

    # Return cached result unless refresh is requested
    if not refresh:
        cached = database.get_consensus(ticker)
        if cached:
            return cached

    # Run the full pipeline
    company_name = get_company_name(ticker)

    # Step 1 — Fetch articles
    articles = fetch_articles(ticker)
    if not articles:
        raise HTTPException(
            status_code=404,
            detail=f"No articles found for {company_name} ({ticker}). Try again later.",
        )

    # Step 2 — Map phase
    analyses = run_map_phase(articles)
    if not analyses:
        raise HTTPException(
            status_code=422,
            detail="Articles were fetched but could not be analysed. Try again.",
        )

    # Step 3 — Reduce phase
    consensus = run_reduce_phase(ticker, company_name, analyses)
    if not consensus:
        raise HTTPException(
            status_code=422,
            detail="Could not synthesise consensus from articles. Try again.",
        )

    # Cache and return
    database.save_consensus(ticker, company_name, consensus.model_dump())
    return consensus


@app.delete("/consensus/{ticker}")
def clear_consensus(ticker: str):
    """Clear cached consensus for a ticker to force fresh analysis."""
    database.clear_consensus(ticker)
    return {"message": f"Cache cleared for {ticker}"}


@app.get("/tickers")
def list_tickers():
    """Return list of all supported tickers."""
    from ingestion import SUPPORTED_TICKERS
    return {"tickers": SUPPORTED_TICKERS}