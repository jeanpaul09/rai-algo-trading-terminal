"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { Experiment } from "@/lib/types"
import { TrendingUp, TrendingDown, Target, Zap } from "lucide-react"

interface StrategyAnalyticsViewProps {
  experiments: Experiment[]
}

export function StrategyAnalyticsView({ experiments }: StrategyAnalyticsViewProps) {
  // Calculate strategy rankings
  const rankedStrategies = experiments
    .map((exp: Experiment) => ({
      name: exp.strategy_name,
      sharpe: exp.metrics?.sharpe || 0,
      sortino: exp.metrics?.sortino || 0,
      max_drawdown: exp.metrics?.max_drawdown || 0,
      cagr: exp.metrics?.cagr || 0,
      win_rate: exp.metrics?.win_rate || 0,
      total_trades: (exp.metrics as any)?.total_trades || 0,
    }))
    .sort((a, b) => b.sharpe - a.sharpe)
    .slice(0, 10)

  const avgSharpe = experiments.length > 0
    ? experiments.reduce((sum: number, e: Experiment) => sum + (e.metrics?.sharpe || 0), 0) / experiments.length
    : 0

  const avgWinRate = experiments.length > 0
    ? experiments.reduce((sum: number, e: Experiment) => sum + (e.metrics?.win_rate || 0), 0) / experiments.length
    : 0

  return (
    <div className="space-y-6">
      {/* Strategy Performance Summary */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Target className="h-4 w-4" />
              Total Strategies
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{experiments.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              Avg Sharpe Ratio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgSharpe.toFixed(2)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Zap className="h-4 w-4 text-yellow-500" />
              Avg Win Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(avgWinRate * 100).toFixed(1)}%</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-red-500" />
              Best Strategy
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold">
              {rankedStrategies[0]?.name || "N/A"}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Sharpe: {rankedStrategies[0]?.sharpe.toFixed(2) || "0.00"}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Strategy Rankings */}
      <Card>
        <CardHeader>
          <CardTitle>Strategy Performance Rankings</CardTitle>
        </CardHeader>
        <CardContent>
          {rankedStrategies.length === 0 ? (
            <p className="text-sm text-muted-foreground">No strategy data available</p>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Rank</TableHead>
                    <TableHead>Strategy</TableHead>
                    <TableHead>Sharpe</TableHead>
                    <TableHead>Sortino</TableHead>
                    <TableHead>Max DD</TableHead>
                    <TableHead>CAGR</TableHead>
                    <TableHead>Win Rate</TableHead>
                    <TableHead>Total Trades</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rankedStrategies.map((strategy, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Badge variant={index === 0 ? "default" : "outline"}>
                          #{index + 1}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-semibold">{strategy.name}</TableCell>
                      <TableCell className={strategy.sharpe > 1 ? "text-green-500 font-semibold" : ""}>
                        {strategy.sharpe.toFixed(2)}
                      </TableCell>
                      <TableCell>{strategy.sortino.toFixed(2)}</TableCell>
                      <TableCell className="text-red-500">
                        {(strategy.max_drawdown * 100).toFixed(2)}%
                      </TableCell>
                      <TableCell className={strategy.cagr > 0 ? "text-green-500" : "text-red-500"}>
                        {(strategy.cagr * 100).toFixed(2)}%
                      </TableCell>
                      <TableCell>{(strategy.win_rate * 100).toFixed(1)}%</TableCell>
                      <TableCell>{strategy.total_trades}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Strategy Insights */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Top Performers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {rankedStrategies.slice(0, 3).map((strategy, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-muted rounded">
                  <span className="text-sm font-medium">{strategy.name}</span>
                  <Badge variant="default">Sharpe: {strategy.sharpe.toFixed(2)}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Risk Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Worst Drawdown:</span>
                <span className="font-semibold text-red-500">
                  {rankedStrategies.length > 0
                    ? `${(Math.min(...rankedStrategies.map(s => s.max_drawdown)) * 100).toFixed(2)}%`
                    : "N/A"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Best CAGR:</span>
                <span className="font-semibold text-green-500">
                  {rankedStrategies.length > 0
                    ? `${(Math.max(...rankedStrategies.map(s => s.cagr)) * 100).toFixed(2)}%`
                    : "N/A"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Total Experiments:</span>
                <span className="font-semibold">{experiments.length}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

