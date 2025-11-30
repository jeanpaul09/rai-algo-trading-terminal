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
const USE_BACKEND = API_BASE_URL && API_BASE_URL !== "http://localhost:8000"

async function fetchTerminalAPI<T>(
  endpoint: string,
  options?: RequestInit,
  fallback?: () => T | Promise<T>
): Promise<T> {
  if (!USE_BACKEND || !API_BASE_URL) {
    if (fallback) {
      const result = fallback()
      return result instanceof Promise ? result : Promise.resolve(result)
    }
    throw new Error("No API URL configured and no fallback provided")
  }

  // Ensure endpoint starts with / and remove double slashes
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`
  const cleanBaseUrl = API_BASE_URL.replace(/\/+$/, "") // Remove trailing slashes
  const url = `${cleanBaseUrl}${cleanEndpoint}`.replace(/([^:]\/)\/+/g, "$1") // Remove double slashes except after protocol

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    if (fallback) {
      console.warn(`API call to ${endpoint} failed, using fallback:`, error)
      const result = fallback()
      return result instanceof Promise ? result : Promise.resolve(result)
    }
    throw error
  }
}

/**
 * Fetch agent status
 */
export async function fetchAgentStatus(): Promise<AgentStatus> {
  const fallback: AgentStatus = {
    mode: "OFF",
    isActive: false,
    environment: "testnet",
    connected: false,
    lastUpdate: new Date().toISOString(),
  }

  return fetchTerminalAPI<AgentStatus>("/api/terminal/status", undefined, () => fallback)
}

/**
 * Update agent mode
 */
export async function updateAgentMode(mode: "OFF" | "DEMO" | "LIVE"): Promise<AgentStatus> {
  return fetchTerminalAPI<AgentStatus>(
    "/api/terminal/agent/mode",
    {
      method: "POST",
      body: JSON.stringify({ mode }),
    },
    () => fetchAgentStatus()
  )
}

/**
 * Fetch wallet information
 */
export async function fetchWalletInfo(): Promise<WalletInfo | null> {
  return fetchTerminalAPI<WalletInfo | null>(
    "/api/terminal/wallet",
    undefined,
    () => null
  )
}

/**
 * Fetch OHLCV data for chart
 */
export async function fetchOHLCVData(
  symbol: string,
  interval: string = "1h",
  limit: number = 1000
): Promise<OHLCVData[]> {
  const fallback: OHLCVData[] = []

  return fetchTerminalAPI<OHLCVData[]>(
    `/api/terminal/chart/data?symbol=${encodeURIComponent(symbol)}&interval=${interval}&limit=${limit}`,
    undefined,
    () => fallback
  )
}

/**
 * Fetch chart annotations
 */
export async function fetchChartAnnotations(
  symbol?: string,
  strategy?: string
): Promise<ChartAnnotation[]> {
  const params = new URLSearchParams()
  if (symbol) params.append("symbol", symbol)
  if (strategy) params.append("strategy", strategy)

  return fetchTerminalAPI<ChartAnnotation[]>(
    `/api/terminal/chart/annotations?${params.toString()}`,
    undefined,
    () => []
  )
}

/**
 * Fetch brain feed entries
 */
export async function fetchBrainFeed(limit: number = 100): Promise<BrainFeedEntry[]> {
  return fetchTerminalAPI<BrainFeedEntry[]>(
    `/api/terminal/brain-feed?limit=${limit}`,
    undefined,
    () => []
  )
}

/**
 * Fetch strategy controls
 */
export async function fetchStrategies(): Promise<StrategyControl[]> {
  return fetchTerminalAPI<StrategyControl[]>(
    "/api/terminal/strategies",
    undefined,
    () => []
  )
}

/**
 * Update strategy mode
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
    },
    () => Promise.resolve()
  )
}

/**
 * Send command to agent
 */
export async function sendAgentCommand(command: string): Promise<AgentCommand> {
  const fallback: AgentCommand = {
    id: `cmd-${Date.now()}`,
    timestamp: new Date().toISOString(),
    command,
    status: "pending",
  }

  return fetchTerminalAPI<AgentCommand>(
    "/api/terminal/agent/command",
    {
      method: "POST",
      body: JSON.stringify({ command }),
    },
    () => Promise.resolve(fallback)
  )
}

/**
 * Fetch performance comparison data
 */
export async function fetchPerformanceComparison(
  strategyName: string
): Promise<PerformanceComparison[]> {
  return fetchTerminalAPI<PerformanceComparison[]>(
    `/api/terminal/performance?strategy=${encodeURIComponent(strategyName)}`,
    undefined,
    () => []
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
  if (!apiUrl || apiUrl === "http://localhost:8000") {
    // Return empty string when no backend is configured (won't connect)
    return ""
  }
  
  try {
    const wsProtocol = apiUrl.startsWith("https") ? "wss:" : "ws:"
    // Remove protocol and trailing slashes, then add ws/terminal
    const baseURL = apiUrl.replace(/^https?:\/\//, "").replace(/\/+$/, "")
    return `${wsProtocol}//${baseURL}/ws/terminal`
  } catch (error) {
    console.warn("Failed to generate WebSocket URL:", error)
    return ""
  }
}

