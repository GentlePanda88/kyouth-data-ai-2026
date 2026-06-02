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

  const riskColor = (r: RiskRating) => {
    if (r === "low") return "text-green-400";
    if (r === "high") return "text-red-400";
    return "text-yellow-400";
  };

  return (
    <main className="min-h-screen bg-[#0a0e0a] text-white font-sans">

      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4 bg-[#0a0e0a]/80 backdrop-blur border-b border-gray-800/50">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-green-500/20 border border-green-500/40 flex items-center justify-center">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L3 7v10l9 5 9-5V7L12 2z" stroke="#22c55e" strokeWidth="1.5" fill="none"/>
              <path d="M12 8v8M8 10l4-2 4 2" stroke="#22c55e" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </div>
          <div>
            <div className="text-sm font-bold tracking-widest text-white">SENTINEL</div>
            <div className="text-[10px] text-gray-500 -mt-0.5">AI Market Sentiment</div>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse inline-block" />
          Live Analysis
        </div>
      </nav>

      {/* Hero */}
      <div className="relative min-h-[480px] flex items-center justify-center overflow-hidden pt-16">

        {/* Bull — left */}
        <div className="absolute left-0 top-0 bottom-0 w-1/3 pointer-events-none">
          <Image
            src="/bull-bear.png"
            alt="Bull"
            fill
            className="object-cover object-left opacity-40"
            style={{ objectPosition: "25% center" }}
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-r from-transparent to-[#0a0e0a]" />
        </div>

        {/* Bear — right */}
        <div className="absolute right-0 top-0 bottom-0 w-1/3 pointer-events-none">
          <Image
            src="/bull-bear.png"
            alt="Bear"
            fill
            className="object-cover object-right opacity-40"
            style={{ objectPosition: "75% center" }}
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-l from-transparent to-[#0a0e0a]" />
        </div>

        {/* Center content */}
        <div className="relative z-10 text-center px-4 w-full max-w-2xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold mb-3 tracking-tight">
            Market Sentiment Analyzer
          </h1>
          <p className="text-gray-400 mb-10">
            AI-powered insights for smarter investment decisions
          </p>

          {/* Search bar */}
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 text-sm">🔍</span>
              <select
                className="w-full bg-[#111811] border border-gray-700 hover:border-gray-600 focus:border-green-500 rounded-xl pl-10 pr-4 py-4 text-white focus:outline-none transition-colors appearance-none text-sm"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
              >
                <option value="">Search for a company or stock (e.g. Maybank, CIMB)</option>
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
              className="bg-green-500 hover:bg-green-400 active:bg-green-600 disabled:bg-gray-800 disabled:text-gray-600 disabled:cursor-not-allowed px-8 py-4 rounded-xl font-bold text-black transition-all text-sm whitespace-nowrap"
            >
              {loading ? "Analysing..." : "Analyze"}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 pb-16">

        {/* Loading */}
        {loading && (
          <div className="text-center py-24">
            <div className="relative inline-block mb-6">
              <div className="w-16 h-16 border-4 border-green-500/20 rounded-full" />
              <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
            </div>
            <p className="text-gray-300 text-lg font-medium">Running AI Analysis</p>
            <p className="text-gray-600 text-sm mt-2">Fetching articles · Mapping sentiment · Synthesising consensus</p>
            <p className="text-gray-700 text-xs mt-1">This may take 30–60 seconds</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-500/5 border border-red-500/20 rounded-2xl p-5 text-red-400 text-center text-sm mt-4">
            ⚠ {error}
          </div>
        )}

        {/* Results */}
        {consensus && (
          <div className="space-y-4 mt-2">

            {/* Company Header */}
            <div className="text-center py-4">
              <h2 className="text-3xl font-bold">{consensus.company_name}</h2>
              <p className="text-gray-500 text-sm mt-1">Bursa Malaysia · {consensus.ticker}</p>
            </div>

            {/* Metric Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">

              {/* Sentiment */}
              <div className="bg-[#0f140f] border border-gray-800 rounded-2xl p-6 hover:border-gray-700 transition-colors">
                <p className="text-gray-500 text-xs uppercase tracking-widest mb-4">Overall Sentiment</p>
                <div className="flex items-center gap-4">
                  <div className={`w-14 h-14 rounded-2xl flex items-center justify-center text-3xl ${
                    consensus.overall_sentiment === "bullish"
                      ? "bg-green-500/10 border border-green-500/20"
                      : consensus.overall_sentiment === "bearish"
                      ? "bg-red-500/10 border border-red-500/20"
                      : "bg-yellow-500/10 border border-yellow-500/20"
                  }`}>
                    {consensus.overall_sentiment === "bullish" ? "🐂" : consensus.overall_sentiment === "bearish" ? "🐻" : "➡️"}
                  </div>
                  <div>
                    <div className={`text-2xl font-bold capitalize ${sentimentColor(consensus.overall_sentiment)}`}>
                      {consensus.overall_sentiment}
                    </div>
                    <div className="text-gray-600 text-xs mt-0.5">
                      {consensus.overall_sentiment === "bullish"
                        ? "Market outlook positive"
                        : consensus.overall_sentiment === "bearish"
                        ? "Market outlook negative"
                        : "Market outlook mixed"}
                    </div>
                  </div>
                </div>
              </div>

              {/* Confidence */}
              <div className="bg-[#0f140f] border border-gray-800 rounded-2xl p-6 hover:border-gray-700 transition-colors">
                <p className="text-gray-500 text-xs uppercase tracking-widest mb-4">Confidence Score</p>
                <div className="text-5xl font-bold text-white mb-4">
                  {Math.round(consensus.confidence_score * 100)}
                  <span className="text-2xl text-gray-500">%</span>
                </div>
                <div className="w-full bg-gray-800/60 rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full bg-gradient-to-r from-green-600 to-green-400 transition-all duration-700"
                    style={{ width: `${consensus.confidence_score * 100}%` }}
                  />
                </div>
                <p className="text-gray-600 text-xs mt-2">
                  {consensus.confidence_score >= 0.7 ? "High Confidence" : consensus.confidence_score >= 0.4 ? "Moderate Confidence" : "Low Confidence"}
                </p>
              </div>

              {/* Risk */}
              <div className="bg-[#0f140f] border border-gray-800 rounded-2xl p-6 hover:border-gray-700 transition-colors">
                <p className="text-gray-500 text-xs uppercase tracking-widest mb-4">Risk Rating</p>
                <div className={`text-5xl font-bold capitalize mb-4 ${riskColor(consensus.risk_rating)}`}>
                  {consensus.risk_rating}
                </div>
                <div className="relative w-full h-1.5 rounded-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500">
                  <div
                    className="absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-white rounded-full shadow-lg border-2 border-[#0f140f] transition-all duration-700"
                    style={{
                      left: consensus.risk_rating === "low" ? "12%" : consensus.risk_rating === "high" ? "88%" : "50%",
                    }}
                  />
                </div>
                <div className="flex justify-between text-[10px] text-gray-700 mt-2">
                  <span>Low</span><span>Medium</span><span>High</span>
                </div>
              </div>
            </div>

            {/* AI Summary + Sources */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="md:col-span-2 bg-[#0f140f] border border-gray-800 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-6 h-6 rounded-md bg-green-500/20 flex items-center justify-center">
                    <span className="text-green-400 text-xs">✦</span>
                  </div>
                  <h3 className="font-semibold text-sm uppercase tracking-widest text-gray-300">AI Summary</h3>
                </div>
                <p className="text-gray-300 leading-relaxed text-sm">{consensus.summary}</p>
              </div>

              <div className="bg-[#0f140f] border border-gray-800 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-sm uppercase tracking-widest text-gray-300">Source Articles</h3>
                  <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full">
                    {consensus.articles_analysed}
                  </span>
                </div>
                <div className="space-y-3">
                  {consensus.sources.map((source, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center text-xs font-bold text-gray-300 flex-shrink-0">
                        {source.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="text-sm text-gray-300 leading-tight">{source}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Bull vs Bear */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="bg-[#0a120a] border border-green-900/40 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-5">
                  <span className="text-green-400 text-lg font-bold">↗</span>
                  <h3 className="font-bold text-green-400 uppercase tracking-widest text-sm">Positive Factors</h3>
                </div>
                <ul className="space-y-3">
                  {consensus.bull_case.map((point, i) => (
                    <li key={i} className="flex gap-3 text-sm text-gray-300 leading-snug">
                      <span className="text-green-500 mt-0.5 flex-shrink-0 font-bold">✓</span>
                      {point}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-[#120a0a] border border-red-900/40 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-5">
                  <span className="text-red-400 text-lg font-bold">↘</span>
                  <h3 className="font-bold text-red-400 uppercase tracking-widest text-sm">Negative Factors</h3>
                </div>
                <ul className="space-y-3">
                  {consensus.bear_case.map((point, i) => (
                    <li key={i} className="flex gap-3 text-sm text-gray-300 leading-snug">
                      <span className="text-red-500 mt-0.5 flex-shrink-0 font-bold">✗</span>
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Article Breakdown */}
            {consensus.article_summaries && consensus.article_summaries.length > 0 && (
              <div className="bg-[#0f140f] border border-gray-800 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-5">
                  <div className="w-6 h-6 rounded-md bg-gray-800 flex items-center justify-center">
                    <span className="text-gray-400 text-xs">▤</span>
                  </div>
                  <h3 className="font-semibold text-sm uppercase tracking-widest text-gray-300">
                    Recent Article Sentiment Breakdown
                  </h3>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {consensus.article_summaries.map((article, i) => (
                    <div
                      key={i}
                      className="bg-[#0a0e0a] border border-gray-800/60 rounded-xl p-4 hover:border-gray-700 transition-colors"
                    >
                      <p className="text-sm text-gray-300 leading-snug mb-3 line-clamp-2 min-h-[40px]">
                        {article.headline}
                      </p>
                      <div className="flex items-center justify-between pt-2 border-t border-gray-800/60">
                        <span className="text-xs text-gray-600 truncate max-w-[120px]">{article.source}</span>
                        <span className={`text-xs font-semibold flex items-center gap-1.5 ${sentimentColor(article.sentiment)}`}>
                          <span className="w-1.5 h-1.5 rounded-full bg-current" />
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