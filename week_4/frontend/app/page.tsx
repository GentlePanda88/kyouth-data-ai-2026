"use client";

import { useState } from "react";
import Image from "next/image";

const SUPPORTED_TICKERS: Record<string, string> = {
  "1155": "Maybank",
  "5347": "Tenaga Nasional",
  "1295": "Public Bank",
  "1023": "CIMB Group",
  "5183": "Petronas Chemicals",
  "5225": "IHH Healthcare",
  "1066": "RHB Bank",
  "5819": "Hong Leong Bank",
  "6888": "Axiata Group",
  "6012": "Maxis",
  "4197": "Sime Darby",
  "5168": "Hartalega",
};

type Sentiment = "bullish" | "bearish" | "neutral";
type RiskRating = "low" | "medium" | "high";

interface ArticleSummary {
  headline: string;
  source: string;
  sentiment: Sentiment;
  url: string;
}

interface ConsensusOutput {
  ticker: string;
  company_name: string;
  overall_sentiment: Sentiment;
  confidence_score: number;
  bull_case: string[];
  bear_case: string[];
  risk_rating: RiskRating;
  summary: string;
  articles_analysed: number;
  sources: string[];
  article_summaries: ArticleSummary[];
}

export default function Home() {
  const [ticker, setTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [consensus, setConsensus] = useState<ConsensusOutput | null>(null);

  const handleSearch = async () => {
    if (!ticker.trim()) return;
    setLoading(true);
    setError("");
    setConsensus(null);

    try {
      const res = await fetch(
        `http://localhost:8000/consensus/${ticker.trim()}?refresh=true`
      );
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Something went wrong");
      }
      const data = await res.json();
      setConsensus(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to fetch consensus. Is the backend running?");
      }
    } finally {
      setLoading(false);
    }
  };

  const sentimentColor = (s: Sentiment) => {
    if (s === "bullish") return "text-green-400";
    if (s === "bearish") return "text-red-400";
    return "text-yellow-400";
  };

  const sentimentBg = (s: Sentiment) => {
    if (s === "bullish") return "bg-green-500/10 border-green-500/30 text-green-400";
    if (s === "bearish") return "bg-red-500/10 border-red-500/30 text-red-400";
    return "bg-yellow-500/10 border-yellow-500/30 text-yellow-400";
  };

  const riskBadge = (r: RiskRating) => {
    if (r === "low") return "bg-green-500/20 text-green-400 border border-green-500/30";
    if (r === "high") return "bg-red-500/20 text-red-400 border border-red-500/30";
    return "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30";
  };

  const sentimentIcon = (s: Sentiment) => {
    if (s === "bullish") return "●";
    if (s === "bearish") return "●";
    return "●";
  };

  return (
    <main className="min-h-screen bg-gray-950 text-white">

      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gray-950 border-b border-gray-800">
        <div className="absolute inset-0 z-0">
          <Image
            src="/bull-bear.png"
            alt="Bull vs Bear"
            fill
            className="object-cover opacity-20"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-gray-950/60 via-gray-950/40 to-gray-950" />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto px-4 py-20 text-center">
          {/* Logo */}
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-green-500/20 border border-green-500/40 flex items-center justify-center text-green-400 text-xl">
              ⬡
            </div>
            <div className="text-left">
              <div className="text-2xl font-bold tracking-tight">SENTINEL</div>
              <div className="text-xs text-gray-400 -mt-1">AI Market Sentiment</div>
            </div>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold mb-3 mt-6">
            Market Sentiment Analyzer
          </h1>
          <p className="text-gray-400 text-lg mb-10">
            AI-powered insights for smarter investment decisions
          </p>

          {/* Search */}
          <div className="flex gap-3 max-w-2xl mx-auto">
            <div className="flex-1 relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">🔍</span>
              <select
                className="w-full bg-gray-900/80 backdrop-blur border border-gray-700 rounded-xl pl-10 pr-4 py-4 text-white focus:outline-none focus:border-green-500 transition-colors appearance-none"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
              >
                <option value="">Search for a company or stock...</option>
                {Object.entries(SUPPORTED_TICKERS).map(([code, name]) => (
                  <option key={code} value={code}>
                    {code} — {name}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={handleSearch}
              disabled={loading || !ticker}
              className="bg-green-500 hover:bg-green-400 disabled:bg-gray-700 disabled:cursor-not-allowed px-8 py-4 rounded-xl font-bold text-black transition-colors whitespace-nowrap"
            >
              {loading ? "Analysing..." : "Analyze"}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-10">

        {/* Loading */}
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full animate-spin mb-6" />
            <p className="text-gray-300 text-lg">Fetching articles and running AI analysis...</p>
            <p className="text-gray-600 text-sm mt-2">This may take 30–60 seconds</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-5 text-red-400 text-center">
            {error}
          </div>
        )}

        {/* Results */}
        {consensus && (
          <div className="space-y-6">

            {/* Top Metric Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">

              {/* Overall Sentiment */}
              <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
                <p className="text-gray-500 text-sm mb-3">Overall Sentiment</p>
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl ${
                    consensus.overall_sentiment === "bullish"
                      ? "bg-green-500/20"
                      : consensus.overall_sentiment === "bearish"
                      ? "bg-red-500/20"
                      : "bg-yellow-500/20"
                  }`}>
                    {consensus.overall_sentiment === "bullish" ? "🐂" : consensus.overall_sentiment === "bearish" ? "🐻" : "➡️"}
                  </div>
                  <div>
                    <div className={`text-2xl font-bold capitalize ${sentimentColor(consensus.overall_sentiment)}`}>
                      {consensus.overall_sentiment}
                    </div>
                    <div className="text-gray-500 text-xs">
                      {consensus.overall_sentiment === "bullish"
                        ? "Market outlook is positive"
                        : consensus.overall_sentiment === "bearish"
                        ? "Market outlook is negative"
                        : "Market outlook is mixed"}
                    </div>
                  </div>
                </div>
              </div>

              {/* Confidence Score */}
              <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
                <p className="text-gray-500 text-sm mb-3">Confidence Score</p>
                <div className="text-4xl font-bold text-white mb-3">
                  {Math.round(consensus.confidence_score * 100)}%
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full transition-all"
                    style={{ width: `${consensus.confidence_score * 100}%` }}
                  />
                </div>
                <p className="text-gray-500 text-xs mt-2">
                  {consensus.confidence_score >= 0.7
                    ? "High Confidence"
                    : consensus.confidence_score >= 0.4
                    ? "Moderate Confidence"
                    : "Low Confidence"}
                </p>
              </div>

              {/* Risk Rating */}
              <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
                <p className="text-gray-500 text-sm mb-3">Risk Rating</p>
                <div className={`text-4xl font-bold capitalize mb-3 ${
                  consensus.risk_rating === "low"
                    ? "text-green-400"
                    : consensus.risk_rating === "high"
                    ? "text-red-400"
                    : "text-yellow-400"
                }`}>
                  {consensus.risk_rating}
                </div>
                {/* Risk Slider Visual */}
                <div className="w-full h-2 rounded-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 relative">
                  <div
                    className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full border-2 border-gray-900 shadow"
                    style={{
                      left: consensus.risk_rating === "low"
                        ? "15%"
                        : consensus.risk_rating === "high"
                        ? "85%"
                        : "50%",
                    }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-600 mt-1">
                  <span>Low</span>
                  <span>Medium</span>
                  <span>High</span>
                </div>
              </div>
            </div>

            {/* AI Summary + Sources Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

              {/* AI Summary */}
              <div className="md:col-span-2 bg-gray-900 border border-gray-800 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-green-400">✦</span>
                  <h3 className="font-bold text-lg">AI Summary</h3>
                </div>
                <p className="text-gray-300 leading-relaxed text-sm">{consensus.summary}</p>
              </div>

              {/* Source Articles */}
              <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-lg">Source Articles</h3>
                  <span className="text-xs text-gray-500">{consensus.articles_analysed} articles</span>
                </div>
                <div className="space-y-3">
                  {consensus.sources.map((source, i) => (
                    <div key={i} className="flex items-center gap-3 text-sm">
                      <div className="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center text-xs font-bold text-gray-400">
                        {source.charAt(0)}
                      </div>
                      <span className="text-gray-300 truncate">{source}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Bull vs Bear */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

              {/* Bull Case */}
              <div className="bg-gray-900 border border-green-500/20 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-green-400 text-xl">↗</span>
                  <h3 className="font-bold text-lg text-green-400">Positive Factors</h3>
                </div>
                <ul className="space-y-3">
                  {consensus.bull_case.map((point, i) => (
                    <li key={i} className="flex gap-3 text-sm text-gray-300">
                      <span className="text-green-500 mt-0.5 flex-shrink-0">✓</span>
                      {point}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Bear Case */}
              <div className="bg-gray-900 border border-red-500/20 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-red-400 text-xl">↘</span>
                  <h3 className="font-bold text-lg text-red-400">Negative Factors</h3>
                </div>
                <ul className="space-y-3">
                  {consensus.bear_case.map((point, i) => (
                    <li key={i} className="flex gap-3 text-sm text-gray-300">
                      <span className="text-red-500 mt-0.5 flex-shrink-0">✗</span>
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Article Sentiment Breakdown */}
            {consensus.article_summaries && consensus.article_summaries.length > 0 && (
              <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
                <h3 className="font-bold text-lg mb-4">Recent Article Sentiment Breakdown</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {consensus.article_summaries.map((article, i) => (
                    <div
                      key={i}
                      className="bg-gray-800/50 rounded-xl p-4 border border-gray-700/50"
                    >
                      <p className="text-sm text-gray-300 leading-snug mb-3 line-clamp-2">
                        {article.headline}
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">{article.source}</span>
                        <span className={`text-xs font-semibold flex items-center gap-1 ${sentimentColor(article.sentiment)}`}>
                          {sentimentIcon(article.sentiment)}
                          <span className="capitalize">{article.sentiment}</span>
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        )}
      </div>
    </main>
  );
}