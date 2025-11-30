"use client"

import { useState, useEffect } from "react"
import { TerminalErrorBoundary } from "./page-error-boundary"
import { GlobalControlBar } from "@/components/terminal/global-control-bar"
import { AnnotatedChart } from "@/components/terminal/annotated-chart"
import { BrainFeed } from "@/components/terminal/brain-feed"
import { StrategyControlPanel } from "@/components/terminal/strategy-control-panel"
import { AgentInteraction } from "@/components/terminal/agent-interaction"
import { PerformanceComparison } from "@/components/terminal/performance-comparison"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useWebSocket } from "@/hooks/use-websocket"
import { getWebSocketURL, fetchAgentStatus, fetchWalletInfo, fetchOHLCVData, fetchChartAnnotations, fetchBrainFeed, fetchStrategies, updateAgentMode, updateStrategyMode, sendAgentCommand, fetchPerformanceComparison } from "@/lib/api-terminal"
import type {
  AgentStatus,
  WalletInfo,
  ChartAnnotation,
  BrainFeedEntry,
  StrategyControl,
  AgentCommand,
  OHLCVData,
  PerformanceComparison as PerformanceComparisonType,
} from "@/lib/types"

// NO MOCK DATA - All data must come from backend API

export default function TerminalPage() {
  // State
  const [agentStatus, setAgentStatus] = useState<AgentStatus>({
    mode: "OFF",
    isActive: false,
    environment: "testnet",
    connected: false, // Will be updated from backend
    lastUpdate: new Date().toISOString(),
  })

  const [walletInfo, setWalletInfo] = useState<WalletInfo | undefined>(undefined)
  const [chartData, setChartData] = useState<OHLCVData[]>([])
  const [annotations, setAnnotations] = useState<ChartAnnotation[]>([])
  const [brainFeedEntries, setBrainFeedEntries] = useState<BrainFeedEntry[]>([])
  const [strategies, setStrategies] = useState<StrategyControl[]>([])

  const [commands, setCommands] = useState<AgentCommand[]>([])
  const [selectedStrategy, setSelectedStrategy] = useState<string | null>(null)
  const [showAnnotations, setShowAnnotations] = useState(true)
  const [backendConnected, setBackendConnected] = useState(false)
  const [performanceComparisons, setPerformanceComparisons] = useState<PerformanceComparisonType[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // WebSocket connection for real-time updates
  const [wsUrl, setWsUrl] = useState<string>("")
  
  useEffect(() => {
    // Only set WebSocket URL on client side
    if (typeof window !== "undefined") {
      try {
        const url = getWebSocketURL()
        setWsUrl(url)
      } catch (error) {
        console.error("Error getting WebSocket URL:", error)
        setWsUrl("") // Set empty to prevent connection attempts
      }
    }
  }, [])
  
  const { isConnected, send } = useWebSocket({
    url: wsUrl,
    reconnect: !!wsUrl, // Only reconnect if we have a valid URL
    onMessage: (data) => {
      // Handle different message types from WebSocket
      switch (data.type) {
        case "brain_feed":
          setBrainFeedEntries((prev) => [
            ...prev.slice(-99), // Keep last 99 entries
            data.entry as BrainFeedEntry,
          ])
          break
        case "annotation":
          // Add new annotation
          const newAnnotation = data.annotation as ChartAnnotation
          setAnnotations((prev) => {
            // Avoid duplicates
            const exists = prev.some(a => a.id === newAnnotation.id)
            if (exists) return prev
            return [...prev, newAnnotation]
          })
          break
        case "annotation_refresh":
          // Refresh annotations from backend
          if (apiUrl) {
            fetchChartAnnotations("BTC/USD", selectedStrategy || undefined)
              .then((freshAnnotations) => {
                setAnnotations(freshAnnotations)
              })
              .catch((error) => {
                console.error("Error refreshing annotations:", error)
              })
          }
          break
        case "chart_update":
          // Update latest candle
          if (data.candle) {
            setChartData((prev) => {
              const updated = [...prev]
              const lastCandle = updated[updated.length - 1]
              if (lastCandle && lastCandle.time === data.candle.time) {
                updated[updated.length - 1] = data.candle
              } else {
                updated.push(data.candle)
                if (updated.length > 1000) {
                  updated.shift()
                }
              }
              return updated
            })
          }
          break
        case "agent_status":
          setAgentStatus(data.status as AgentStatus)
          break
        case "wallet_update":
          setWalletInfo(data.wallet as WalletInfo)
          break
        case "strategy_update":
          setStrategies((prev) =>
            prev.map((s) =>
              s.name === data.strategy.name ? { ...s, ...data.strategy } : s
            )
          )
          break
        case "command_response":
          setCommands((prev) =>
            prev.map((cmd) =>
              cmd.id === data.commandId
                ? { ...cmd, ...data.command as AgentCommand }
                : cmd
            )
          )
          break
      }
    },
    onError: (error) => {
      console.error("🔌 WebSocket connection error:", error)
      console.error("WebSocket URL:", wsUrl)
    },
    onOpen: () => {
      console.log("✅ WebSocket connected successfully - real-time updates enabled")
    },
    onClose: () => {
      console.warn("⚠️ WebSocket disconnected - falling back to polling")
    },
  })

  // Load initial data - REAL DATA ONLY
  useEffect(() => {
    const loadData = async () => {
      const backendUrl = typeof window !== "undefined" 
        ? (process.env.NEXT_PUBLIC_API_URL || "")
        : ""
      
      if (!backendUrl) {
        console.error("❌ NEXT_PUBLIC_API_URL not configured! Cannot load data.")
        setBackendConnected(false)
        return
      }

      console.log("✅ Backend URL configured:", backendUrl)
      setBackendConnected(true)

      try {
        // Use API client functions which handle the backend URL correctly
        const [status, wallet, chartData, annotations, brainFeed, strategies] = await Promise.all([
          fetchAgentStatus().catch(() => null),
          fetchWalletInfo().catch(() => null),
          fetchOHLCVData("BTC/USDT", "1h", 100).catch(() => []),
          fetchChartAnnotations("BTC/USDT").catch(() => []),
          fetchBrainFeed(50).catch(() => []),
          fetchStrategies().catch(() => []),
        ])
        
        if (status) {
          setAgentStatus(status)
          console.log("✅ Loaded agent status from backend:", status)
        }
        if (wallet) {
          setWalletInfo(wallet)
          console.log("✅ Loaded wallet info from backend:", wallet)
        }
        if (chartData && chartData.length > 0) {
          console.log("✅ Loaded REAL chart data from backend:", chartData.length, "candles")
          console.log("📊 First candle:", chartData[0])
          console.log("📊 Last candle:", chartData[chartData.length - 1])
          setChartData(chartData)
        } else {
          console.warn("⚠️ Backend returned empty chart data")
          console.warn("Response was:", chartData)
          console.warn("This could mean:")
          console.warn("  1. Backend API endpoint not working")
          console.warn("  2. Market data source (Hyperliquid/Kraken) unavailable")
          console.warn("  3. Network/connection issue")
        }
        if (annotations && annotations.length > 0) {
          setAnnotations(annotations)
          console.log("✅ Loaded REAL annotations from backend:", annotations.length, "annotations")
        }
        if (brainFeed && brainFeed.length > 0) {
          setBrainFeedEntries(brainFeed)
          console.log("✅ Loaded brain feed from backend:", brainFeed.length, "entries")
        }
        if (strategies && strategies.length > 0) {
          setStrategies(strategies)
          console.log("✅ Loaded strategies from backend:", strategies.length, "strategies")
        }
      } catch (error) {
        console.error("❌ Error loading data from backend:", error)
        setBackendConnected(false)
        console.log("⚠️ Backend configured but failed - will retry or show empty state")
      }
      
      // Load performance data separately
      try {
        const performance = await fetchPerformanceComparison(selectedStrategy || "").catch(() => [])
        if (performance && performance.length > 0) {
          setPerformanceComparisons(performance)
          console.log("✅ Loaded performance data from backend:", performance.length, "comparisons")
        }
      } catch (error) {
        console.error("❌ Error loading performance data:", error)
      } finally {
        setIsLoading(false)
      }
    }
    
    loadData()
    
    // Set up polling fallback if WebSocket fails (refresh data every 10 seconds)
    // Only poll if WebSocket failed after initial connection attempts
    const pollingInterval = setInterval(() => {
      if (!isConnected && apiUrl) {
        // WebSocket not connected, use polling as fallback for annotations/performance
        // Don't poll chart data - it's loaded once on mount
        fetchChartAnnotations("BTC/USDT").then(setAnnotations).catch(() => {})
        if (agentStatus.isActive && agentStatus.mode === "DEMO") {
          fetchPerformanceComparison(selectedStrategy || "").then(setPerformanceComparisons).catch(() => {})
        }
      }
    }, 10000) // Poll every 10 seconds if WebSocket is down
    
    return () => clearInterval(pollingInterval)
  }, [selectedStrategy, isConnected, apiUrl, agentStatus.isActive, agentStatus.mode])
  
  // Refresh performance data periodically when demo trading is active
  useEffect(() => {
    if (!agentStatus.isActive || agentStatus.mode !== "DEMO") return
    
    const interval = setInterval(async () => {
      try {
        const performance = await fetchPerformanceComparison(selectedStrategy || "").catch(() => [])
        if (performance && performance.length > 0) {
          setPerformanceComparisons(performance)
        }
      } catch (error) {
        console.error("❌ Error refreshing performance data:", error)
      }
    }, 5000) // Refresh every 5 seconds
    
    return () => clearInterval(interval)
  }, [agentStatus.isActive, agentStatus.mode, selectedStrategy])

  // Handlers
  const handleModeChange = async (mode: "OFF" | "DEMO" | "LIVE") => {
    try {
      // Update backend first
      const updatedStatus = await updateAgentMode(mode)
      setAgentStatus(updatedStatus)
      
      // Also send via WebSocket if connected
      if (isConnected && send) {
        send({ type: "set_agent_mode", mode })
      }
    } catch (error) {
      console.error("Failed to update agent mode:", error)
      // Don't update local state if backend call failed
    }
  }

  const handleToggleAgent = async () => {
    const newMode = agentStatus.isActive ? "OFF" : "DEMO"
    await handleModeChange(newMode)
  }

  const handleEmergencyStop = async () => {
    try {
      // Stop all strategies
      for (const strategy of strategies) {
        if (strategy.mode !== "OFF") {
          try {
            const apiBase = process.env.NEXT_PUBLIC_API_URL
            if (apiBase) {
              await fetch(`${apiBase}/api/terminal/strategies/${encodeURIComponent(strategy.name)}/stop`, {
                method: "POST",
              }).catch(() => {})
            }
          } catch (e) {
            console.error(`Failed to stop strategy ${strategy.name}:`, e)
          }
        }
      }
      
      // Set agent to OFF mode
      await handleModeChange("OFF")
      
      // Send emergency stop via WebSocket
      if (isConnected && send) {
        send({ type: "emergency_stop" })
      }
    } catch (error) {
      console.error("Emergency stop failed:", error)
    }
  }

  const handleStrategyModeChange = async (strategyName: string, mode: "OFF" | "DEMO" | "LIVE") => {
    try {
      // Update backend first
      await updateStrategyMode(strategyName, mode)
      
      // Update local state on success
      setStrategies((prev) =>
        prev.map((s) => (s.name === strategyName ? { ...s, mode, status: mode !== "OFF" ? "scanning" : "idle" } : s))
      )
      
      // If starting strategy, trigger live trading
      if (mode === "DEMO" || mode === "LIVE") {
        try {
          const apiBase = process.env.NEXT_PUBLIC_API_URL
          if (apiBase) {
            await fetch(`${apiBase}/api/terminal/strategies/${encodeURIComponent(strategyName)}/start`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ mode }),
            })
          }
        } catch (e) {
          console.error("Failed to start strategy:", e)
        }
      }
    } catch (error) {
      console.error("Failed to update strategy mode:", error)
    }
  }

  const handleEditParameters = (strategyName: string) => {
    // Open parameters dialog
    console.log("Edit parameters for", strategyName)
  }

  const handleTriggerBacktest = async (strategyName: string) => {
    console.log("Trigger backtest for", strategyName)
    // TODO: Send to backend
  }

  const handleSendCommand = async (command: string) => {
    const newCommand: AgentCommand = {
      id: `cmd-${Date.now()}`,
      timestamp: new Date().toISOString(),
      command,
      status: "processing",
    }

    setCommands((prev) => [...prev, newCommand])

    try {
      // Send command to backend - REAL API CALL
      const response = await sendAgentCommand(command)
      
      // Update command with response
      setCommands((prev) =>
        prev.map((cmd) =>
          cmd.id === newCommand.id ? { ...cmd, ...response } : cmd
        )
      )
      
      // Also send via WebSocket if connected
      if (isConnected && send) {
        send({
          type: "agent_command",
          command: newCommand.command,
          commandId: newCommand.id,
        })
      }
    } catch (error) {
      console.error("Failed to send command:", error)
      setCommands((prev) =>
        prev.map((cmd) =>
          cmd.id === newCommand.id
            ? {
                ...cmd,
                status: "failed",
                response: `Error: ${error instanceof Error ? error.message : "Failed to send command"}`,
              }
            : cmd
        )
      )
    }
  }

  // Get API URL safely
  const apiUrl = typeof window !== "undefined" 
    ? (process.env.NEXT_PUBLIC_API_URL || "")
    : ""

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading terminal...</p>
        </div>
      </div>
    )
  }

  return (
    <TerminalErrorBoundary>
      <div className="flex flex-col h-full w-full bg-background">
      {/* Global Control Bar */}
      <div className="relative flex-shrink-0 border-b">
        <GlobalControlBar
          agentStatus={agentStatus}
          walletInfo={walletInfo}
          onModeChange={handleModeChange}
          onEmergencyStop={handleEmergencyStop}
          onToggleAgent={handleToggleAgent}
        />
        {(!isConnected || !apiUrl) && (
          <div className="absolute top-0 right-4 p-2 flex gap-2 z-10">
            {!apiUrl && (
              <Badge variant="destructive" className="text-xs">
                Backend URL Not Set - Cannot Load Data
              </Badge>
            )}
            {!isConnected && apiUrl && (
              <Badge variant="destructive" className="text-xs">
{isConnected ? (
                  <Badge variant="default" className="bg-green-500/20 text-green-400 border-green-500/50">
                    WebSocket Connected
                  </Badge>
                ) : reconnectAttempts >= 2 ? (
                  <Badge variant="outline" className="border-gray-700 text-gray-400">
                    Using Polling
                  </Badge>
                ) : null}
              </Badge>
            )}
          </div>
        )}
      </div>

      {/* Main Terminal Layout */}
      <div className="flex-1 flex overflow-hidden" style={{ minHeight: 0 }}>
        {/* Left Panel: Strategy Control */}
        <div className="w-80 border-r flex-shrink-0 overflow-hidden">
          <StrategyControlPanel
            strategies={strategies}
            onModeChange={handleStrategyModeChange}
            onEditParameters={handleEditParameters}
            onTriggerBacktest={handleTriggerBacktest}
          />
        </div>

        {/* Center: Chart and Brain Feed */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Chart Controls */}
          <div className="p-4 border-b flex items-center justify-between bg-muted/30">
            <div className="flex items-center gap-4">
              <Select
                value={selectedStrategy || "all"}
                onValueChange={(value) =>
                  setSelectedStrategy(value === "all" ? null : value)
                }
              >
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filter by strategy" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Strategies</SelectItem>
                  {strategies.map((s) => (
                    <SelectItem key={s.name} value={s.name}>
                      {s.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                variant={showAnnotations ? "default" : "outline"}
                size="sm"
                onClick={() => setShowAnnotations(!showAnnotations)}
              >
                {showAnnotations ? "Hide" : "Show"} Annotations
              </Button>
            </div>
          </div>

          {/* Chart */}
          <div className="flex-1 p-4 overflow-hidden">
            <AnnotatedChart
              data={chartData}
              annotations={annotations}
              symbol="BTC/USD"
              height={400}
              showAnnotations={showAnnotations}
              strategyFilter={selectedStrategy}
            />
          </div>

          {/* Brain Feed */}
          <div className="h-64 border-t">
            <BrainFeed entries={brainFeedEntries} />
          </div>
        </div>

        {/* Right Panel: Agent Interaction & Performance */}
        <div className="w-96 border-l flex-shrink-0 flex flex-col overflow-hidden">
          <div className="flex-1 border-b overflow-hidden">
            <AgentInteraction
              commands={commands}
              onSendCommand={handleSendCommand}
              isProcessing={commands.some((c) => c.status === "processing")}
            />
          </div>
          <div className="flex-1 overflow-hidden">
            <PerformanceComparison
              comparisons={performanceComparisons}
            />
          </div>
        </div>
      </div>
    </div>
    </TerminalErrorBoundary>
  )
}

