/**
 * Typed API client for RAI-ALGO backend
 * Assumes backend runs on a different port (e.g., Python FastAPI on port 8000)
 */

import type {
  Overview,
  Strategy,
  Experiment,
  LiveStatus,
  CorrelationMatrix,
  MarketExposure,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
// Use backend if API URL is explicitly set (not empty string)
const USE_BACKEND = typeof process.env.NEXT_PUBLIC_API_URL === "string" && process.env.NEXT_PUBLIC_API_URL !== "";

async function fetchAPI<T>(endpoint: string, fallback?: () => T | Promise<T>): Promise<T> {
  // If no API URL is set, use mock data
  if (!USE_BACKEND || !API_BASE_URL) {
    if (fallback) {
      const result = fallback();
      return result instanceof Promise ? result : Promise.resolve(result);
    }
    throw new Error("No API URL configured and no fallback provided");
  }

  try {
    const controller = typeof window !== "undefined" ? new AbortController() : null;
    const timeoutId = controller ? setTimeout(() => controller.abort(), 10000) : null;
    
    // Use no-store for client-side, revalidate for server-side
    const fetchOptions: RequestInit = {
      cache: typeof window !== "undefined" ? "no-store" : undefined,
      next: typeof window === "undefined" ? { revalidate: 5 } : undefined, // Revalidate every 5 seconds on server
      signal: controller?.signal,
    };
    
    // Ensure endpoint starts with / and remove double slashes
    const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`
    const cleanBaseUrl = (API_BASE_URL || "").replace(/\/+$/, "") // Remove trailing slashes
    let url = `${cleanBaseUrl}${cleanEndpoint}`
    // Remove double slashes except after protocol (https:// or http://)
    url = url.replace(/([^:]\/)\/+/g, "$1")
    
    const response = await fetch(url, fetchOptions);
    
    if (timeoutId) clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    // Log data source for debugging
    if (typeof window !== "undefined") {
      console.log(`✅ Fetched ${endpoint}:`, data.data_source || "no data_source", data.btc_price ? `BTC: $${data.btc_price.toFixed(2)}` : "");
    }
    return data;
  } catch (error) {
    // If API call fails and we have a fallback, use it
    if (fallback) {
      console.warn(`API call to ${endpoint} failed, using mock data:`, error);
      const result = fallback();
      return result instanceof Promise ? result : Promise.resolve(result);
    }
    throw error;
  }
}

/**
 * Fetch overview dashboard data
 */
export async function fetchOverview(): Promise<Overview> {
  const mockData = {
    total_strategies: 12,
    deployed_strategies: 5,
    best_sharpe: 2.45,
    worst_drawdown: -0.1523,
    latest_equity_curve: generateMockEquityCurve(),
    daily_pnl: 1250.50,
    data_source: "mock",
  };
  
  // ALWAYS try to fetch real data first
  try {
    const realData = await fetchAPI<Overview>("/api/overview");
    // If we got real data (even if equity curve is empty, check data_source)
    if (realData.data_source === "real" || (realData.latest_equity_curve && realData.latest_equity_curve.length > 0)) {
      console.log("✅ Using REAL data from API:", realData.data_source, "BTC:", realData.btc_price);
      return realData;
    }
    // If API returned but data_source is mock, still use it (API knows best)
    if (realData.data_source) {
      console.log("⚠️ API returned mock data:", realData.data_source);
      return realData;
    }
  } catch (e) {
    console.error("❌ Failed to fetch from API, using mock:", e);
    // Fall through to mock data
  }
  
  return mockData;
}

/**
 * Fetch all strategies
 */
export async function fetchStrategies(): Promise<Strategy[]> {
  const mockData: Strategy[] = [
    {
      name: "MA Cross Momentum",
      description: "Moving average crossover strategy",
      markets: ["BTC/USD", "ETH/USD"],
      state: "deployed",
      tags: ["momentum", "crypto"],
      best_sharpe: 2.45,
      worst_drawdown: -0.1523,
    },
    {
      name: "Mean Reversion Arb",
      description: "Mean reversion arbitrage strategy",
      markets: ["BTC/USD", "SOL/USD"],
      state: "validated",
      tags: ["mean-reversion", "arbitrage", "crypto"],
      best_sharpe: 1.89,
      worst_drawdown: -0.0891,
    },
    {
      name: "Prediction Market Scanner",
      description: "Scans prediction markets for opportunities",
      markets: ["Polymarket", "Kalshi"],
      state: "experimental",
      tags: ["prediction-markets", "scanner"],
      best_sharpe: 1.23,
      worst_drawdown: -0.2341,
    },
  ];
  
  return fetchAPI<Strategy[]>("/api/strategies", () => mockData);
}

/**
 * Fetch a single strategy by name
 */
export async function fetchStrategy(name: string): Promise<Strategy> {
  const fallback = async () => {
    const strategies = await fetchStrategies();
    const strategy = strategies.find((s) => s.name === name);
    if (!strategy) {
      throw new Error(`Strategy not found: ${name}`);
    }
    return strategy;
  };
  
  return fetchAPI<Strategy>(`/api/strategies/${encodeURIComponent(name)}`, fallback);
}

/**
 * Fetch experiments for a strategy
 */
export async function fetchStrategyExperiments(
  name: string
): Promise<Experiment[]> {
  const mockData: Experiment[] = [
    {
      id: `exp-${name}-001`,
      strategy_name: name,
      market: "BTC/USD",
      start_date: "2024-01-01",
      end_date: "2024-03-31",
      status: "completed",
      parameters: { fast_period: 10, slow_period: 30 },
      metrics: {
        sharpe: 2.45,
        sortino: 2.78,
        max_drawdown: -0.1523,
        cagr: 0.2345,
        hit_rate: 0.65,
        win_rate: 0.65,
      },
    },
  ];
  
  return fetchAPI<Experiment[]>(
    `/api/strategies/${encodeURIComponent(name)}/experiments`,
    () => mockData
  );
}

/**
 * Fetch all experiments
 */
export async function fetchExperiments(): Promise<Experiment[]> {
  const fallback = async () => {
    const strategies = await fetchStrategies();
    const experiments: Experiment[] = [];
    for (const strategy of strategies) {
      const strategyExps = await fetchStrategyExperiments(strategy.name);
      experiments.push(...strategyExps);
    }
    return experiments;
  };
  
  return fetchAPI<Experiment[]>("/api/experiments", fallback);
}

/**
 * Fetch a single experiment by ID
 */
export async function fetchExperiment(id: string): Promise<Experiment> {
  const fallback = async () => {
    const experiments = await fetchExperiments();
    const experiment = experiments.find((e) => e.id === id);
    if (!experiment) {
      throw new Error(`Experiment not found: ${id}`);
    }
    
    // Add mock equity curve and drawdown data
    return {
      ...experiment,
      equity_curve: generateMockEquityCurve(),
      drawdown_curve: generateMockDrawdownCurve(),
      return_distribution: generateMockReturnDistribution(),
    };
  };
  
  return fetchAPI<Experiment>(`/api/experiments/${id}`, fallback);
}

/**
 * Fetch live trading status
 */
export async function fetchLiveStatus(): Promise<LiveStatus> {
  const mockData: LiveStatus = {
    equity: 125000,
    daily_pnl: 1250.50,
    total_exposure: 50000,
    max_exposure: 100000,
    current_drawdown: -0.0234,
    max_drawdown_allowed: -0.15,
    risk_status: "OK",
    positions: [
      {
        exchange: "Hyperliquid",
        symbol: "BTC/USD",
        side: "long",
        size: 0.5,
        entry_price: 45000,
        mark_price: 45250,
        unrealized_pnl: 125,
        leverage: 2,
      },
    ],
    venue_overview: [
      {
        venue: "Hyperliquid",
        notional_exposure: 50000,
        pnl: 1250.50,
        funding_impact: 12.5,
      },
    ],
  };
  
  return fetchAPI<LiveStatus>("/api/live/status", () => mockData);
}

/**
 * Fetch correlation matrix for strategies
 */
export async function fetchCorrelationMatrix(): Promise<CorrelationMatrix> {
  const fallback = async () => {
    const strategies = await fetchStrategies();
    const names = strategies.map((s) => s.name);
    
    // Mock correlation matrix
    const correlations: number[][] = names.map(() =>
      names.map(() => Math.random() * 2 - 1)
    );
    
    // Make it symmetric and set diagonal to 1
    for (let i = 0; i < names.length; i++) {
      correlations[i][i] = 1;
      for (let j = i + 1; j < names.length; j++) {
        correlations[j][i] = correlations[i][j];
      }
    }
    
    return { strategies: names, correlations };
  };
  
  return fetchAPI<CorrelationMatrix>("/api/correlation", fallback);
}

/**
 * Fetch market exposure breakdown
 */
export async function fetchMarketExposure(): Promise<MarketExposure[]> {
  const mockData: MarketExposure[] = [
    { market: "BTC", exposure: 25000, percentage: 50 },
    { market: "ETH", exposure: 15000, percentage: 30 },
    { market: "SOL", exposure: 10000, percentage: 20 },
  ];
  
  return fetchAPI<MarketExposure[]>("/api/market-exposure", () => mockData);
}

// Helper functions for mock data generation
function generateMockEquityCurve() {
  const points = [];
  const startDate = new Date("2024-01-01");
  let equity = 100000;
  
  for (let i = 0; i < 90; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    const dailyReturn = (Math.random() - 0.45) * 0.02; // Slight positive bias
    equity *= 1 + dailyReturn;
    points.push({
      timestamp: date.toISOString(),
      equity,
      pnl: dailyReturn * equity,
    });
  }
  
  return points;
}

function generateMockDrawdownCurve() {
  const points = [];
  const startDate = new Date("2024-01-01");
  
  for (let i = 0; i < 90; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    points.push({
      timestamp: date.toISOString(),
      drawdown: Math.max(0, (Math.random() - 0.7) * 0.2),
    });
  }
  
  return points;
}

function generateMockReturnDistribution() {
  return Array.from({ length: 100 }, () => (Math.random() - 0.5) * 0.1);
}

