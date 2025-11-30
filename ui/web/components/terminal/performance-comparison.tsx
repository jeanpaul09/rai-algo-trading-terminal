"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { EquityCurve } from "@/components/charts/equity-curve"
import { DrawdownCurve } from "@/components/charts/drawdown-curve"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { PerformanceComparison, TradingMode } from "@/lib/types"

interface PerformanceComparisonProps {
  comparisons: PerformanceComparison[]
  selectedStrategies?: string[]
}

export function PerformanceComparison({
  comparisons,
  selectedStrategies = [],
}: PerformanceComparisonProps) {
  const backtestData = comparisons.find((c) => c.mode === "BACKTEST")
  const demoData = comparisons.find((c) => c.mode === "DEMO")
  const liveData = comparisons.find((c) => c.mode === "LIVE")

  const getModeColor = (mode: TradingMode) => {
    switch (mode) {
      case "LIVE":
        return "text-red-500"
      case "DEMO":
        return "text-yellow-500"
      case "BACKTEST":
        return "text-blue-500"
    }
  }

  const getModeBadgeVariant = (mode: TradingMode): "default" | "secondary" | "destructive" | "outline" => {
    switch (mode) {
      case "LIVE":
        return "destructive"
      case "DEMO":
        return "secondary"
      case "BACKTEST":
        return "outline"
    }
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="border-b pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Performance Comparison</CardTitle>
          <div className="flex gap-2">
            {backtestData && (
              <Badge variant={getModeBadgeVariant("BACKTEST")}>BACKTEST</Badge>
            )}
            {demoData && (
              <Badge variant={getModeBadgeVariant("DEMO")}>DEMO</Badge>
            )}
            {liveData && (
              <Badge variant={getModeBadgeVariant("LIVE")}>LIVE</Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 p-6">
        <Tabs defaultValue="overview" className="h-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="equity">Equity Curves</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6 mt-6">
            {/* Metrics Table */}
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Metric</TableHead>
                    {backtestData && <TableHead className="text-blue-500">Backtest</TableHead>}
                    {demoData && <TableHead className="text-yellow-500">Demo</TableHead>}
                    {liveData && <TableHead className="text-red-500">Live</TableHead>}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell className="font-medium">Sharpe Ratio</TableCell>
                    {backtestData && (
                      <TableCell className={getModeColor("BACKTEST")}>
                        {backtestData.metrics.sharpe.toFixed(2)}
                      </TableCell>
                    )}
                    {demoData && (
                      <TableCell className={getModeColor("DEMO")}>
                        {demoData.metrics.sharpe.toFixed(2)}
                      </TableCell>
                    )}
                    {liveData && (
                      <TableCell className={getModeColor("LIVE")}>
                        {liveData.metrics.sharpe.toFixed(2)}
                      </TableCell>
                    )}
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-medium">Max Drawdown</TableCell>
                    {backtestData && (
                      <TableCell className={getModeColor("BACKTEST")}>
                        {(backtestData.metrics.max_drawdown * 100).toFixed(2)}%
                      </TableCell>
                    )}
                    {demoData && (
                      <TableCell className={getModeColor("DEMO")}>
                        {(demoData.metrics.max_drawdown * 100).toFixed(2)}%
                      </TableCell>
                    )}
                    {liveData && (
                      <TableCell className={getModeColor("LIVE")}>
                        {(liveData.metrics.max_drawdown * 100).toFixed(2)}%
                      </TableCell>
                    )}
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-medium">CAGR</TableCell>
                    {backtestData && (
                      <TableCell className={getModeColor("BACKTEST")}>
                        {(backtestData.metrics.cagr * 100).toFixed(2)}%
                      </TableCell>
                    )}
                    {demoData && (
                      <TableCell className={getModeColor("DEMO")}>
                        {(demoData.metrics.cagr * 100).toFixed(2)}%
                      </TableCell>
                    )}
                    {liveData && (
                      <TableCell className={getModeColor("LIVE")}>
                        {(liveData.metrics.cagr * 100).toFixed(2)}%
                      </TableCell>
                    )}
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-medium">Win Rate</TableCell>
                    {backtestData && (
                      <TableCell className={getModeColor("BACKTEST")}>
                        {(backtestData.metrics.win_rate * 100).toFixed(2)}%
                      </TableCell>
                    )}
                    {demoData && (
                      <TableCell className={getModeColor("DEMO")}>
                        {(demoData.metrics.win_rate * 100).toFixed(2)}%
                      </TableCell>
                    )}
                    {liveData && (
                      <TableCell className={getModeColor("LIVE")}>
                        {(liveData.metrics.win_rate * 100).toFixed(2)}%
                      </TableCell>
                    )}
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-medium">Total Return</TableCell>
                    {backtestData && (
                      <TableCell className={getModeColor("BACKTEST")}>
                        {backtestData.metrics.total_return
                          ? `${(backtestData.metrics.total_return * 100).toFixed(2)}%`
                          : "N/A"}
                      </TableCell>
                    )}
                    {demoData && (
                      <TableCell className={getModeColor("DEMO")}>
                        {demoData.metrics.total_return
                          ? `${(demoData.metrics.total_return * 100).toFixed(2)}%`
                          : "N/A"}
                      </TableCell>
                    )}
                    {liveData && (
                      <TableCell className={getModeColor("LIVE")}>
                        {liveData.metrics.total_return
                          ? `${(liveData.metrics.total_return * 100).toFixed(2)}%`
                          : "N/A"}
                      </TableCell>
                    )}
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          <TabsContent value="equity" className="space-y-6 mt-6">
            {backtestData && (
              <div>
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <Badge variant={getModeBadgeVariant("BACKTEST")}>BACKTEST</Badge>
                  Equity Curve
                </h3>
                <EquityCurve data={backtestData.equityCurve} height={300} />
              </div>
            )}
            {demoData && (
              <div>
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <Badge variant={getModeBadgeVariant("DEMO")}>DEMO</Badge>
                  Equity Curve
                </h3>
                <EquityCurve data={demoData.equityCurve} height={300} />
              </div>
            )}
            {liveData && (
              <div>
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <Badge variant={getModeBadgeVariant("LIVE")}>LIVE</Badge>
                  Equity Curve
                </h3>
                <EquityCurve data={liveData.equityCurve} height={300} />
              </div>
            )}
          </TabsContent>

          <TabsContent value="metrics" className="space-y-6 mt-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {backtestData && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Badge variant={getModeBadgeVariant("BACKTEST")}>BACKTEST</Badge>
                      Metrics
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Sharpe:</span>
                      <span className="font-semibold">
                        {backtestData.metrics.sharpe.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Sortino:</span>
                      <span className="font-semibold">
                        {backtestData.metrics.sortino.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Hit Rate:</span>
                      <span className="font-semibold">
                        {(backtestData.metrics.hit_rate * 100).toFixed(2)}%
                      </span>
                    </div>
                  </CardContent>
                </Card>
              )}
              {demoData && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Badge variant={getModeBadgeVariant("DEMO")}>DEMO</Badge>
                      Metrics
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Sharpe:</span>
                      <span className="font-semibold">
                        {demoData.metrics.sharpe.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Sortino:</span>
                      <span className="font-semibold">
                        {demoData.metrics.sortino.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Hit Rate:</span>
                      <span className="font-semibold">
                        {(demoData.metrics.hit_rate * 100).toFixed(2)}%
                      </span>
                    </div>
                  </CardContent>
                </Card>
              )}
              {liveData && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <Badge variant={getModeBadgeVariant("LIVE")}>LIVE</Badge>
                      Metrics
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Sharpe:</span>
                      <span className="font-semibold">
                        {liveData.metrics.sharpe.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Sortino:</span>
                      <span className="font-semibold">
                        {liveData.metrics.sortino.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Hit Rate:</span>
                      <span className="font-semibold">
                        {(liveData.metrics.hit_rate * 100).toFixed(2)}%
                      </span>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

