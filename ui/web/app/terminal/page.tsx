"use client"

import { useState, useEffect } from "react"
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
import { getWebSocketURL } from "@/lib/api-terminal"
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

// Mock data generators (replace with real API calls)
function generateMockOHLCV(): OHLCVData[] {
  const data: OHLCVData[] = []
  const now = Date.now()
  const oneDay = 24 * 60 * 60 * 1000

  for (let i = 100; i >= 0; i--) {
    const time = now - i * oneDay
    const basePrice = 45000 + Math.random() * 5000
    data.push({
      time: Math.floor(time / 1000),
      open: basePrice,
      high: basePrice * (1 + Math.random() * 0.02),
      low: basePrice * (1 - Math.random() * 0.02),
      close: basePrice * (1 + (Math.random() - 0.5) * 0.02),
      volume: Math.random() * 1000,
    })
  }
  return data
}

function generateMockAnnotations(): ChartAnnotation[] {
  const annotations: ChartAnnotation[] = []
  const now = Date.now()
  const oneDay = 24 * 60 * 60 * 1000

  // Add some entry/exit markers
  for (let i = 0; i < 5; i++) {
    const time = now - (10 + i * 20) * oneDay
    annotations.push({
      id: `entry-${i}`,
      type: "entry",
      timestamp: Math.floor(time / 1000),
      price: 45000 + Math.random() * 5000,
      strategy: i % 2 === 0 ? "MA Cross Momentum" : "Mean Reversion Arb",
      reason: "Signal detected",
      label: "Entry",
    })
  }

  return annotations
}

export default function TerminalPage() {
  // State
  const [agentStatus, setAgentStatus] = useState<AgentStatus>({
    mode: "OFF",
    isActive: false,
    environment: "testnet",
    connected: true,
    lastUpdate: new Date().toISOString(),
  })

  const [walletInfo, setWalletInfo] = useState<WalletInfo | undefined>({
    address: "0x1234...5678",
    balance: 125000,
    marginUsed: 25000,
    marginAvailable: 100000,
    realizedPnL: 1250.5,
    unrealizedPnL: 125.75,
    environment: "testnet",
  })

  const [chartData, setChartData] = useState<OHLCVData[]>([])
  const [annotations, setAnnotations] = useState<ChartAnnotation[]>([])
  const [brainFeedEntries, setBrainFeedEntries] = useState<BrainFeedEntry[]>([])
  const [strategies, setStrategies] = useState<StrategyControl[]>([
    {
      name: "MA Cross Momentum",
      description: "Moving average crossover strategy",
      category: "Trend",
      mode: "OFF",
      status: "idle",
      parameters: { fast_period: 10, slow_period: 30 },
      currentExposure: 0,
      lastPnL: 0,
    },
    {
      name: "Mean Reversion Arb",
      description: "Mean reversion arbitrage strategy",
      category: "Mean Reversion",
      mode: "OFF",
      status: "idle",
      parameters: { lookback: 20, threshold: 0.02 },
      currentExposure: 0,
      lastPnL: 0,
    },
  ])

  const [commands, setCommands] = useState<AgentCommand[]>([])
  const [selectedStrategy, setSelectedStrategy] = useState<string | null>(null)
  const [showAnnotations, setShowAnnotations] = useState(true)

  // WebSocket connection for real-time updates
  const [wsUrl, setWsUrl] = useState<string>("")
  
  useEffect(() => {
    // Only set WebSocket URL on client side
    if (typeof window !== "undefined") {
      const url = getWebSocketURL()
      setWsUrl(url)
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
          setAnnotations((prev) => [...prev, data.annotation as ChartAnnotation])
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
      console.error("WebSocket error:", error)
    },
  })

  // Load initial data - try real API first, fallback to mock
  useEffect(() => {
    const loadData = async () => {
      try {
        // Try to fetch real data from backend
        const apiBase = process.env.NEXT_PUBLIC_API_URL || ""
        if (apiBase) {
          const [status, wallet] = await Promise.all([
            fetch(`${apiBase}/api/terminal/status`).then(r => r.ok ? r.json() : null).catch(() => null),
            fetch(`${apiBase}/api/terminal/wallet`).then(r => r.ok ? r.json() : null).catch(() => null),
          ])
          
          if (status) {
            setAgentStatus(status)
          }
          if (wallet) {
            setWalletInfo(wallet)
          }
        }
      } catch (error) {
        console.log("Using mock data - backend not available:", error)
      }
      
      // Always load mock data as fallback
      setChartData(generateMockOHLCV())
      setAnnotations(generateMockAnnotations())
    }
    
    loadData()
  }, [])

  // Handlers
  const handleModeChange = async (mode: "OFF" | "DEMO" | "LIVE") => {
    setAgentStatus((prev) => ({ ...prev, mode, isActive: mode !== "OFF" }))
    
    // Send to backend if connected
    if (isConnected && send) {
      send({ type: "set_agent_mode", mode })
    } else {
      // Try REST API as fallback
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL
        if (apiBase) {
          await fetch(`${apiBase}/api/terminal/status`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode }),
          }).catch(() => {})
        }
      } catch (e) {
        console.log("Could not update mode on backend")
      }
    }
  }

  const handleToggleAgent = () => {
    setAgentStatus((prev) => ({
      ...prev,
      isActive: !prev.isActive,
      mode: !prev.isActive ? "DEMO" : "OFF",
    }))
  }

  const handleEmergencyStop = () => {
    setAgentStatus((prev) => ({ ...prev, mode: "OFF", isActive: false }))
    // Close all positions, etc.
  }

  const handleStrategyModeChange = (strategyName: string, mode: "OFF" | "DEMO" | "LIVE") => {
    setStrategies((prev) =>
      prev.map((s) => (s.name === strategyName ? { ...s, mode } : s))
    )
  }

  const handleEditParameters = (strategyName: string) => {
    // Open parameters dialog
    console.log("Edit parameters for", strategyName)
  }

  const handleTriggerBacktest = (strategyName: string) => {
    // Trigger backtest
    console.log("Trigger backtest for", strategyName)
  }

  const handleSendCommand = (command: string) => {
    const newCommand: AgentCommand = {
      id: `cmd-${Date.now()}`,
      timestamp: new Date().toISOString(),
      command,
      status: "processing",
    }

    setCommands((prev) => [...prev, newCommand])

    // Send command via WebSocket if connected, otherwise simulate response
    if (isConnected) {
      send({
        type: "agent_command",
        command: newCommand.command,
        commandId: newCommand.id,
      })
    } else {
      // Fallback: simulate agent response
      setTimeout(() => {
        setCommands((prev) =>
          prev.map((cmd) =>
            cmd.id === newCommand.id
              ? {
                  ...cmd,
                  status: "completed",
                  response: `I understand you want me to: "${command}". WebSocket not connected - this is a mock response.`,
                }
              : cmd
          )
        )
      }, 2000)
    }
  }

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Global Control Bar */}
      <div className="relative">
        <GlobalControlBar
          agentStatus={agentStatus}
          walletInfo={walletInfo}
          onModeChange={handleModeChange}
          onEmergencyStop={handleEmergencyStop}
          onToggleAgent={handleToggleAgent}
        />
        {(!isConnected || !process.env.NEXT_PUBLIC_API_URL) && (
          <div className="absolute top-0 right-4 p-2 flex gap-2">
            {!process.env.NEXT_PUBLIC_API_URL && (
              <Badge variant="destructive" className="text-xs">
                Backend URL Not Set - Using Mock Data
              </Badge>
            )}
            {!isConnected && process.env.NEXT_PUBLIC_API_URL && (
              <Badge variant="destructive" className="text-xs">
                WebSocket Disconnected
              </Badge>
            )}
          </div>
        )}
      </div>

        {/* Main Terminal Layout */}
        <div className="flex-1 flex overflow-hidden min-h-0">
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
              comparisons={[
                {
                  mode: "BACKTEST",
                  equityCurve: [],
                  metrics: {
                    sharpe: 2.45,
                    sortino: 2.78,
                    max_drawdown: -0.1523,
                    cagr: 0.2345,
                    hit_rate: 0.65,
                    win_rate: 0.65,
                    total_return: 0.5,
                  },
                  trades: [],
                },
              ]}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

