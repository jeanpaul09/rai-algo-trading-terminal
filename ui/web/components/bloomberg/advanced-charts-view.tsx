"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useState } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from "recharts"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface EquityPoint {
  timestamp: string
  equity: number
}

interface AdvancedChartsViewProps {
  equityCurve: EquityPoint[]
}

export function AdvancedChartsView({ equityCurve }: AdvancedChartsViewProps) {
  const [timeframe, setTimeframe] = useState("1d")
  const [selectedMetric, setSelectedMetric] = useState("equity")

  // Calculate additional metrics
  const returns = equityCurve.slice(1).map((point, i) => ({
    timestamp: point.timestamp,
    return: ((point.equity - equityCurve[i].equity) / equityCurve[i].equity) * 100,
  }))

  const rollingVolatility = equityCurve.map((point, i) => {
    if (i < 20) return { timestamp: point.timestamp, volatility: 0 }
    const window = equityCurve.slice(i - 20, i)
    const returns_window = window.slice(1).map((p, j) => 
      ((p.equity - window[j].equity) / window[j].equity) * 100
    )
    const mean = returns_window.reduce((a, b) => a + b, 0) / returns_window.length
    const variance = returns_window.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns_window.length
    return {
      timestamp: point.timestamp,
      volatility: Math.sqrt(variance) * Math.sqrt(252), // Annualized
    }
  })

  const sharpeRatio = equityCurve.length > 0 ? (() => {
    const returns_data = returns.map(r => r.return)
    const meanReturn = returns_data.reduce((a, b) => a + b, 0) / returns_data.length
    const stdDev = Math.sqrt(
      returns_data.reduce((sum, r) => sum + Math.pow(r - meanReturn, 2), 0) / returns_data.length
    )
    return stdDev > 0 ? (meanReturn / stdDev) * Math.sqrt(252) : 0
  })() : 0

  return (
    <div className="space-y-6">
      {/* Chart Controls */}
      <div className="flex items-center gap-4">
        <Select value={timeframe} onValueChange={setTimeframe}>
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1h">1 Hour</SelectItem>
            <SelectItem value="1d">1 Day</SelectItem>
            <SelectItem value="1w">1 Week</SelectItem>
            <SelectItem value="1m">1 Month</SelectItem>
          </SelectContent>
        </Select>

        <Select value={selectedMetric} onValueChange={setSelectedMetric}>
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="equity">Equity</SelectItem>
            <SelectItem value="returns">Returns</SelectItem>
            <SelectItem value="volatility">Volatility</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Performance Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Sharpe Ratio</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{sharpeRatio.toFixed(2)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Return</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {equityCurve.length > 0 
                ? `${(((equityCurve[equityCurve.length - 1].equity - equityCurve[0].equity) / equityCurve[0].equity) * 100).toFixed(2)}%`
                : "0%"}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Max Drawdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">
              {equityCurve.length > 0
                ? `${Math.min(...equityCurve.map((p, i) => {
                    const peak = Math.max(...equityCurve.slice(0, i + 1).map(pp => pp.equity))
                    return ((p.equity - peak) / peak) * 100
                  })).toFixed(2)}%`
                : "0%"}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Volatility (Annual)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {rollingVolatility.length > 0
                ? `${(rollingVolatility[rollingVolatility.length - 1].volatility).toFixed(2)}%`
                : "0%"}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Advanced Charts */}
      <Tabs defaultValue="equity" className="space-y-4">
        <TabsList>
          <TabsTrigger value="equity">Equity Curve</TabsTrigger>
          <TabsTrigger value="returns">Returns Distribution</TabsTrigger>
          <TabsTrigger value="volatility">Volatility</TabsTrigger>
          <TabsTrigger value="drawdown">Drawdown</TabsTrigger>
        </TabsList>

        <TabsContent value="equity">
          <Card>
            <CardHeader>
              <CardTitle>Equity Curve</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={equityCurve}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value: number) => [`$${value.toLocaleString()}`, "Equity"]}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="equity" 
                    stroke="#22c55e" 
                    fill="#22c55e" 
                    fillOpacity={0.2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="returns">
          <Card>
            <CardHeader>
              <CardTitle>Returns Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={returns}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value: number) => [`${value.toFixed(2)}%`, "Return"]}
                  />
                  <Bar 
                    dataKey="return" 
                    fill="#3b82f6"
                    fillOpacity={0.7}
                  />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="volatility">
          <Card>
            <CardHeader>
              <CardTitle>Rolling Volatility (20-period)</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={rollingVolatility}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value: number) => [`${value.toFixed(2)}%`, "Volatility"]}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="volatility" 
                    stroke="#f59e0b" 
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="drawdown">
          <Card>
            <CardHeader>
              <CardTitle>Drawdown Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={equityCurve.map((p, i) => {
                  const peak = Math.max(...equityCurve.slice(0, i + 1).map(pp => pp.equity))
                  return {
                    timestamp: p.timestamp,
                    drawdown: ((p.equity - peak) / peak) * 100,
                  }
                })}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value: number) => [`${value.toFixed(2)}%`, "Drawdown"]}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="drawdown" 
                    stroke="#ef4444" 
                    fill="#ef4444" 
                    fillOpacity={0.2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

