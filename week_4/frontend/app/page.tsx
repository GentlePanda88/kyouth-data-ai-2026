"use client";

import { useState } from "react";

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
        `http://localhost:8000/consensus/${ticker.trim()}`
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

  const riskBadge = (r: RiskRating) => {
    if (r === "low") return "bg-green-500/20 text-green-400 border border-green-500/30";
    if (r === "high") return "bg-red-500/20 text-red-400 border border-red-500/30";
    return "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30";
  };

  return (
    <main className="min-h-screen bg-gray-950 text-white px-4 py-12">
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold tracking-tight mb-3">
            <span className="text-blue-400">Sentinel</span>
          </h1>
          <p className="text-gray-400 text-lg">
            AI-powered Bull vs Bear consensus for Bursa Malaysia stocks
          </p>
        </div>

        {/* Search */}
        <div className="flex gap-3 mb-4">
          <select
            className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
          >
            <option value="">Select a ticker...</option>
            {Object.entries(SUPPORTED_TICKERS).map(([code, name]) => (
              <option key={code} value={code}>
                {code} — {name}
              </option>
            ))}
          </select>
          <button
            onClick={handleSearch}
            disabled={loading || !ticker}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed px-6 py-3 rounded-xl font-semibold transition-colors"
          >
            {loading ? "Analysing..." : "Analyse"}
          </button>
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center py-16">
            <div className="inline-block w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-gray-400">
              Fetching articles and running AI analysis...
            </p>
            <p className="text-gray-600 text-sm mt-1">This may take 30–60 seconds</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400">
            {error}
          </div>
        )}

        {/* Results */}
        {consensus && (
          <div className="space-y-6 mt-6">

            {/* Summary Card */}
            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
              <div className="flex items-start justify-between flex-wrap gap-4">
                <div>
                  <h2 className="text-2xl font-bold">{consensus.company_name}</h2>
                  <p className="text-gray-500 text-sm mt-1">Ticker: {consensus.ticker}</p>
                </div>
                <div className="flex gap-3 flex-wrap">
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold capitalize ${riskBadge(consensus.risk_rating)}`}>
                    {consensus.risk_rating} risk
                  </span>
                  <span className={`text-lg font-bold capitalize ${sentimentColor(consensus.overall_sentiment)}`}>
                    {consensus.overall_sentiment}
                  </span>
                </div>
              </div>

              {/* Confidence Bar */}
              <div className="mt-4">
                <div className="flex justify-between text-sm text-gray-500 mb-1">
                  <span>Consensus confidence</span>
                  <span>{Math.round(consensus.confidence_score * 100)}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${consensus.confidence_score * 100}%` }}
                  />
                </div>
              </div>

              <p className="text-gray-400 text-sm mt-4 leading-relaxed">
                {consensus.summary}
              </p>
            </div>

            {/* Bull vs Bear */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

              {/* Bull Case */}
              <div className="bg-green-500/5 border border-green-500/20 rounded-2xl p-5">
                <h3 className="text-green-400 font-bold text-lg mb-4">🐂 Bull Case</h3>
                <ul className="space-y-2">
                  {consensus.bull_case.map((point, i) => (
                    <li key={i} className="flex gap-2 text-sm text-gray-300">
                      <span className="text-green-500 mt-0.5">✓</span>
                      {point}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Bear Case */}
              <div className="bg-red-500/5 border border-red-500/20 rounded-2xl p-5">
                <h3 className="text-red-400 font-bold text-lg mb-4">🐻 Bear Case</h3>
                <ul className="space-y-2">
                  {consensus.bear_case.map((point, i) => (
                    <li key={i} className="flex gap-2 text-sm text-gray-300">
                      <span className="text-red-500 mt-0.5">✗</span>
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Sources */}
            <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
              <h3 className="text-gray-400 font-semibold text-sm mb-3">
                SOURCES ANALYSED — {consensus.articles_analysed} articles
              </h3>
              <div className="flex flex-wrap gap-2">
                {consensus.sources.map((source, i) => (
                  <span
                    key={i}
                    className="bg-gray-800 text-gray-300 text-xs px-3 py-1 rounded-full"
                  >
                    {source}
                  </span>
                ))}
              </div>
            </div>

          </div>
        )}
      </div>
    </main>
  );
}