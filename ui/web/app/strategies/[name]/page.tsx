"use client"

import { Topbar } from "@/components/layout/topbar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { EquityCurve } from "@/components/charts/equity-curve"
import { DrawdownCurve } from "@/components/charts/drawdown-curve"
import { DistributionChart } from "@/components/charts/distribution-chart"
import { ExperimentsTable } from "@/components/tables/experiments-table"
import { RunBacktestDialog } from "@/components/backtest/run-backtest-dialog"
import { StartTradingDialog } from "@/components/live/start-trading-dialog"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import {
  fetchStrategy,
  fetchStrategyExperiments,
} from "@/lib/api"
import type { Strategy, Experiment } from "@/lib/types"

export default function StrategyDetailPage() {
  const params = useParams()
  const name = decodeURIComponent(params.name as string)
  
  const [strategy, setStrategy] = useState<Strategy | null>(null)
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const [strat, exps] = await Promise.all([
          fetchStrategy(name),
          fetchStrategyExperiments(name),
        ])
        setStrategy(strat)
        setExperiments(exps)
      } catch (error) {
        console.error("Failed to load strategy:", error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [name])

  if (loading) {
    return (
      <div className="flex flex-col h-full">
        <Topbar title="Loading..." />
        <div className="flex-1 p-6">
          <p className="text-sm text-muted-foreground">Loading strategy...</p>
        </div>
      </div>
    )
  }

  if (!strategy) {
    return (
      <div className="flex flex-col h-full">
        <Topbar title="Strategy Not Found" />
        <div className="flex-1 p-6">
          <p className="text-sm text-muted-foreground">Strategy not found</p>
        </div>
      </div>
    )
  }

  const equityCurve = experiments[0]?.equity_curve || []
  const drawdownCurve = experiments[0]?.drawdown_curve || []
  const returnDistribution = experiments[0]?.return_distribution || []

  return (
    <div className="flex flex-col h-full">
      <Topbar title={strategy.name} />
      <div className="flex-1 p-6 space-y-6">
        {/* Overview Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Overview</CardTitle>
            <div className="flex gap-2">
              <RunBacktestDialog strategyName={name} />
              <StartTradingDialog strategyName={name} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {strategy.description && (
                <p className="text-sm text-muted-foreground">
                  {strategy.description}
                </p>
              )}
              <div className="flex flex-wrap gap-2">
                {strategy.markets.map((market) => (
                  <Badge key={market} variant="outline">
                    {market}
                  </Badge>
                ))}
                {strategy.tags.map((tag) => (
                  <Badge key={tag} variant="secondary">
                    {tag}
                  </Badge>
                ))}
              </div>
              {strategy.latest_metrics && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                  <div>
                    <p className="text-xs text-muted-foreground">Sharpe</p>
                    <p className="text-lg font-semibold">
                      {strategy.latest_metrics.sharpe.toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Sortino</p>
                    <p className="text-lg font-semibold">
                      {strategy.latest_metrics.sortino.toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Max DD</p>
                    <p className="text-lg font-semibold">
                      {(strategy.latest_metrics.max_drawdown * 100).toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">CAGR</p>
                    <p className="text-lg font-semibold">
                      {(strategy.latest_metrics.cagr * 100).toFixed(2)}%
                    </p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs defaultValue="performance" className="space-y-4">
          <TabsList>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="experiments">Experiments</TabsTrigger>
          </TabsList>

          <TabsContent value="performance" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              {equityCurve.length > 0 && (
                <EquityCurve data={equityCurve} />
              )}
              {drawdownCurve.length > 0 && (
                <DrawdownCurve data={drawdownCurve} />
              )}
            </div>
            {returnDistribution.length > 0 && (
              <DistributionChart data={returnDistribution} />
            )}
          </TabsContent>

          <TabsContent value="experiments">
            <ExperimentsTable experiments={experiments} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
