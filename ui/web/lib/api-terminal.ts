/**
 * Terminal-specific API client functions
 * These handle real-time terminal data and agent interactions
 */

import type {
  AgentStatus,
  WalletInfo,
  ChartAnnotation,
  BrainFeedEntry,
  StrategyControl,
  AgentCommand,
  OHLCVData,
  PerformanceComparison,
} from "./types"

// Get API URL - handle both client and server side
function getApiBaseUrl(): string {
  if (typeof window === "undefined") {
    // Server-side
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  }
  // Client-side - Next.js exposes NEXT_PUBLIC_ vars at build time
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
}

const API_BASE_URL = getApiBaseUrl()
// Use backend if URL is set and not localhost (unless explicitly set)
const USE_BACKEND = typeof API_BASE_URL === "string" && API_BASE_URL !== "" && API_BASE_URL !== "http://localhost:8000"

async function fetchTerminalAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  // REQUIRE backend - no mock data fallback
  if (!USE_BACKEND || !API_BASE_URL) {
    throw new Error("Backend API URL not configured. Set NEXT_PUBLIC_API_URL environment variable.")
  }

  // Ensure endpoint starts with / and remove double slashes
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`
  const cleanBaseUrl = API_BASE_URL.replace(/\/+$/, "")
  const url = `${cleanBaseUrl}${cleanEndpoint}`.replace(/([^:]\/)\/+/g, "$1")

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`)
  }

  return await response.json()
}

/**
 * Fetch agent status - REAL DATA ONLY
 */
export async function fetchAgentStatus(): Promise<AgentStatus> {
  return fetchTerminalAPI<AgentStatus>("/api/terminal/status")
}

/**
 * Update agent mode - REAL BACKEND CALL
 */
export async function updateAgentMode(mode: "OFF" | "DEMO" | "LIVE"): Promise<AgentStatus> {
  return fetchTerminalAPI<AgentStatus>(
    "/api/terminal/agent/mode",
    {
      method: "POST",
      body: JSON.stringify({ mode }),
    }
  )
}

/**
 * Fetch wallet information - REAL DATA ONLY
 */
export async function fetchWalletInfo(): Promise<WalletInfo> {
  return fetchTerminalAPI<WalletInfo>("/api/terminal/wallet")
}

/**
 * Fetch OHLCV data for chart - REAL DATA ONLY
 */
export async function fetchOHLCVData(
  symbol: string,
  interval: string = "1h",
  limit: number = 1000
): Promise<OHLCVData[]> {
  return fetchTerminalAPI<OHLCVData[]>(
    `/api/terminal/chart/data?symbol=${encodeURIComponent(symbol)}&interval=${interval}&limit=${limit}`
  )
}

/**
 * Fetch chart annotations - REAL DATA ONLY
 */
export async function fetchChartAnnotations(
  symbol?: string,
  strategy?: string
): Promise<ChartAnnotation[]> {
  const params = new URLSearchParams()
  if (symbol) params.append("symbol", symbol)
  if (strategy) params.append("strategy", strategy)

  return fetchTerminalAPI<ChartAnnotation[]>(
    `/api/terminal/chart/annotations?${params.toString()}`
  )
}

/**
 * Fetch brain feed entries - REAL DATA ONLY
 */
export async function fetchBrainFeed(limit: number = 100): Promise<BrainFeedEntry[]> {
  return fetchTerminalAPI<BrainFeedEntry[]>(
    `/api/terminal/brain-feed?limit=${limit}`
  )
}

/**
 * Fetch strategy controls - REAL DATA ONLY
 */
export async function fetchStrategies(): Promise<StrategyControl[]> {
  return fetchTerminalAPI<StrategyControl[]>("/api/terminal/strategies")
}

/**
 * Update strategy mode - REAL BACKEND CALL
 */
export async function updateStrategyMode(
  strategyName: string,
  mode: "OFF" | "DEMO" | "LIVE"
): Promise<void> {
  return fetchTerminalAPI<void>(
    `/api/terminal/strategies/${encodeURIComponent(strategyName)}/mode`,
    {
      method: "POST",
      body: JSON.stringify({ mode }),
    }
  )
}

/**
 * Send command to agent - REAL BACKEND CALL
 */
export async function sendAgentCommand(command: string): Promise<AgentCommand> {
  return fetchTerminalAPI<AgentCommand>(
    "/api/terminal/agent/command",
    {
      method: "POST",
      body: JSON.stringify({ command }),
    }
  )
}

/**
 * Fetch performance comparison data - REAL DATA ONLY
 */
export async function fetchPerformanceComparison(
  strategyName: string
): Promise<PerformanceComparison[]> {
  return fetchTerminalAPI<PerformanceComparison[]>(
    `/api/terminal/performance?strategy=${encodeURIComponent(strategyName)}`
  )
}

/**
 * Get WebSocket URL for real-time updates
 */
export function getWebSocketURL(): string {
  if (typeof window === "undefined") {
    return "" // Server-side, return empty
  }
  
  const apiUrl = getApiBaseUrl()
  if (!apiUrl) {
    return ""
  }
  
  // Allow localhost in development
  const isLocalhost = window.location.origin.includes("localhost")
  if (apiUrl === "http://localhost:8000" && !isLocalhost) {
    return "" // Don't connect to localhost in production
  }
  
  try {
    const wsProtocol = apiUrl.startsWith("https") ? "wss:" : "ws:"
    // Remove protocol and trailing slashes, then add ws/terminal
    const baseURL = apiUrl.replace(/^https?:\/\//, "").replace(/\/+$/, "")
    const wsUrl = `${wsProtocol}//${baseURL}/ws/terminal`
    console.log("🔌 WebSocket URL:", wsUrl)
    return wsUrl
  } catch (error) {
    console.warn("Failed to generate WebSocket URL:", error)
    return ""
  }
}

