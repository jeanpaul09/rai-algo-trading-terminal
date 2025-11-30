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

async function fetchAPI<T>(endpoint: string): Promise<T> {
  // REQUIRE backend - no mock data fallback
  if (!USE_BACKEND || !API_BASE_URL) {
    throw new Error("Backend API URL not configured. Set NEXT_PUBLIC_API_URL environment variable.");
  }

  const controller = typeof window !== "undefined" ? new AbortController() : null;
  const timeoutId = controller ? setTimeout(() => controller.abort(), 10000) : null;
  
  // Use no-store for client-side, revalidate for server-side
  const fetchOptions: RequestInit = {
    cache: typeof window !== "undefined" ? "no-store" : undefined,
    next: typeof window === "undefined" ? { revalidate: 5 } : undefined,
    signal: controller?.signal,
  };
  
  // Ensure endpoint starts with / and remove double slashes
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`
  const cleanBaseUrl = (API_BASE_URL || "").replace(/\/+$/, "")
  let url = `${cleanBaseUrl}${cleanEndpoint}`
  url = url.replace(/([^:]\/)\/+/g, "$1")
  
  const response = await fetch(url, fetchOptions);
  
  if (timeoutId) clearTimeout(timeoutId);

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  if (typeof window !== "undefined") {
    console.log(`✅ Fetched ${endpoint}:`, data.data_source || "real", data.btc_price ? `BTC: $${data.btc_price.toFixed(2)}` : "");
  }
  return data;
}

/**
 * Fetch overview dashboard data - REAL DATA ONLY
 */
export async function fetchOverview(): Promise<Overview> {
  return fetchAPI<Overview>("/api/overview");
}

/**
 * Fetch all strategies - REAL DATA ONLY
 */
export async function fetchStrategies(): Promise<Strategy[]> {
  return fetchAPI<Strategy[]>("/api/strategies");
}

/**
 * Fetch a single strategy by name - REAL DATA ONLY
 */
export async function fetchStrategy(name: string): Promise<Strategy> {
  return fetchAPI<Strategy>(`/api/strategies/${encodeURIComponent(name)}`);
}

/**
 * Fetch experiments for a strategy - REAL DATA ONLY
 */
export async function fetchStrategyExperiments(
  name: string
): Promise<Experiment[]> {
  return fetchAPI<Experiment[]>(
    `/api/strategies/${encodeURIComponent(name)}/experiments`
  );
}

/**
 * Fetch all experiments - REAL DATA ONLY
 */
export async function fetchExperiments(): Promise<Experiment[]> {
  return fetchAPI<Experiment[]>("/api/experiments");
}

/**
 * Fetch a single experiment by ID - REAL DATA ONLY
 */
export async function fetchExperiment(id: string): Promise<Experiment> {
  return fetchAPI<Experiment>(`/api/experiments/${id}`);
}

/**
 * Fetch live trading status - REAL DATA ONLY
 */
export async function fetchLiveStatus(): Promise<LiveStatus> {
  return fetchAPI<LiveStatus>("/api/live/status");
}

/**
 * Fetch correlation matrix for strategies - REAL DATA ONLY
 */
export async function fetchCorrelationMatrix(): Promise<CorrelationMatrix> {
  return fetchAPI<CorrelationMatrix>("/api/correlation");
}

/**
 * Fetch market exposure breakdown - REAL DATA ONLY
 */
export async function fetchMarketExposure(): Promise<MarketExposure[]> {
  return fetchAPI<MarketExposure[]>("/api/market-exposure");
}

