"use client"

import { Topbar } from "@/components/layout/topbar"
import { KPICard } from "@/components/cards/kpi-card"
import { PerformancePanel } from "@/components/lab/performance-panel"
import { RiskPanel } from "@/components/lab/risk-panel"
import { ExperimentsPanel } from "@/components/lab/experiments-panel"
import { JobStatus } from "@/components/jobs/job-status"
import { useEffect, useState } from "react"
import {
  fetchOverview,
  fetchExperiments,
  fetchCorrelationMatrix,
  fetchMarketExposure,
} from "@/lib/api"
import type { Overview, Experiment, CorrelationMatrix, MarketExposure } from "@/lib/types"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MarketPositionsView } from "@/components/bloomberg/market-positions-view"
import { AdvancedChartsView } from "@/components/bloomberg/advanced-charts-view"
import { StrategyAnalyticsView } from "@/components/bloomberg/strategy-analytics-view"
import { MarketIntelligenceView } from "@/components/bloomberg/market-intelligence-view"

export default function DashboardPage() {
  const [overview, setOverview] = useState<Overview | null>(null)
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [correlationMatrix, setCorrelationMatrix] = useState<CorrelationMatrix>({ strategies: [], correlations: [] })
  const [marketExposure, setMarketExposure] = useState<MarketExposure[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("overview")

  useEffect(() => {
    const loadData = async () => {
      try {
        const [overviewData, experimentsData, correlationData, exposureData] =
          await Promise.all([
            fetchOverview(),
            fetchExperiments(),
            fetchCorrelationMatrix(),
            fetchMarketExposure(),
          ])
        setOverview(overviewData)
        setExperiments(experimentsData)
        setCorrelationMatrix(correlationData)
        setMarketExposure(exposureData)
      } catch (error) {
        console.error("Failed to load dashboard data:", error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
    
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading || !overview) {
    return (
      <div className="flex flex-col h-full">
        <Topbar title="Lab Dashboard" />
        <div className="flex-1 p-6 flex items-center justify-center">
          <p className="text-sm text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  // Generate drawdown curve from equity curve
  const drawdownCurve = overview.latest_equity_curve.map((point, index) => {
    const peak = Math.max(
      ...overview.latest_equity_curve
        .slice(0, index + 1)
        .map((p) => p.equity)
    )
    return {
      timestamp: point.timestamp,
      drawdown: (point.equity - peak) / peak,
    }
  })

  return (
    <div className="flex flex-col h-full bg-background">
      <Topbar title="RAI-ALGO Trading Lab" />
      
      {/* Bloomberg-style Header Bar */}
      <div className="border-b bg-muted/30 px-6 py-2 flex items-center justify-between text-xs font-mono">
        <div className="flex items-center gap-6">
          <div>
            <span className="text-muted-foreground">BTC/USD:</span>
            <span className="ml-2 font-semibold text-green-500">
              ${overview.btc_price ? overview.btc_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "N/A"}
            </span>
          </div>
          <div>
            <span className="text-muted-foreground">Data Source:</span>
            <span className={`ml-2 font-semibold ${overview.data_source === "real" ? "text-green-500" : "text-yellow-500"}`}>
              {overview.data_source === "real" ? "REAL ✅" : (overview.data_source?.toUpperCase() || "MOCK")}
            </span>
          </div>
          <div>
            <span className="text-muted-foreground">Active Strategies:</span>
            <span className="ml-2 font-semibold">{overview.deployed_strategies}</span>
          </div>
        </div>
        <div className="text-muted-foreground">
          {new Date().toLocaleTimeString()} UTC
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
          <div className="border-b px-6">
            <TabsList className="h-12 bg-transparent">
              <TabsTrigger value="overview" className="data-[state=active]:bg-background">
                Overview
              </TabsTrigger>
              <TabsTrigger value="performance" className="data-[state=active]:bg-background">
                Performance
              </TabsTrigger>
              <TabsTrigger value="positions" className="data-[state=active]:bg-background">
                Market Positions
              </TabsTrigger>
              <TabsTrigger value="charts" className="data-[state=active]:bg-background">
                Advanced Charts
              </TabsTrigger>
              <TabsTrigger value="strategy" className="data-[state=active]:bg-background">
                Strategy Analytics
              </TabsTrigger>
              <TabsTrigger value="intelligence" className="data-[state=active]:bg-background">
                Market Intelligence
              </TabsTrigger>
            </TabsList>
          </div>

          <div className="flex-1 overflow-y-auto">
            <TabsContent value="overview" className="m-0 p-6 space-y-6">
              {/* KPI Cards */}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
                <KPICard
                  label="Total Strategies"
                  value={overview.total_strategies}
                  trend="neutral"
                />
                <KPICard
                  label="Deployed"
                  value={overview.deployed_strategies}
                  trend="neutral"
                />
                <KPICard
                  label="Best Sharpe"
                  value={overview.best_sharpe.toFixed(2)}
                  trend="up"
                />
                <KPICard
                  label="Worst Drawdown"
                  value={`${(overview.worst_drawdown * 100).toFixed(2)}%`}
                  trend="down"
                />
                {overview.daily_pnl !== undefined && (
                  <KPICard
                    label="Daily PnL"
                    value={`$${overview.daily_pnl.toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}`}
                    trend={overview.daily_pnl >= 0 ? "up" : "down"}
                  />
                )}
              </div>

              {/* Performance Charts */}
              <PerformancePanel
                equityCurve={overview.latest_equity_curve}
                drawdownCurve={drawdownCurve}
              />

              {/* Bottom Section */}
              <div className="grid gap-6 lg:grid-cols-3">
                <ExperimentsPanel experiments={experiments} />
                <RiskPanel
                  correlationMatrix={correlationMatrix}
                  marketExposure={marketExposure}
                  currentDrawdown={overview.worst_drawdown}
                  maxDrawdownAllowed={-0.15}
                />
                <JobStatus />
              </div>
            </TabsContent>

            <TabsContent value="performance" className="m-0 p-6">
              <PerformancePanel
                equityCurve={overview.latest_equity_curve}
                drawdownCurve={drawdownCurve}
              />
            </TabsContent>

            <TabsContent value="positions" className="m-0 p-6">
              <MarketPositionsView />
            </TabsContent>

            <TabsContent value="charts" className="m-0 p-6">
              <AdvancedChartsView equityCurve={overview.latest_equity_curve} />
            </TabsContent>

            <TabsContent value="strategy" className="m-0 p-6">
              <StrategyAnalyticsView experiments={experiments} />
            </TabsContent>

            <TabsContent value="intelligence" className="m-0 p-6">
              <MarketIntelligenceView />
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  )
}
