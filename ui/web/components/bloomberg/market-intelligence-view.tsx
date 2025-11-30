"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useEffect, useState } from "react"
import { TrendingUp, TrendingDown, AlertTriangle, Activity, DollarSign } from "lucide-react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface Liquidation {
  symbol: string
  side: string
  price: number
  quantity: number
  timestamp: string
}

interface MarketIntelligence {
  total_liquidations_24h: number
  long_liquidations: number
  short_liquidations: number
  largest_liquidation: { symbol: string; value: number }
  liquidation_trend: "increasing" | "decreasing" | "stable"
}

export function MarketIntelligenceView() {
  const [liquidations, setLiquidations] = useState<Liquidation[]>([])
  const [intelligence, setIntelligence] = useState<MarketIntelligence | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        const cleanBaseUrl = (API_BASE_URL || "").replace(/\/+$/, "")
        const url = `${cleanBaseUrl}/api/liquidations?exchange=binance`.replace(/([^:]\/)\/+/g, "$1")
        const response = await fetch(url, {
          cache: "no-store",
        })
        
        if (response.ok) {
          const data = await response.json()
          const liqs = data.liquidations || []
          setLiquidations(liqs)
          
          // Calculate intelligence
          const longLiqs = liqs.filter((l: Liquidation) => l.side === "BUY" || l.side === "LONG")
          const shortLiqs = liqs.filter((l: Liquidation) => l.side === "SELL" || l.side === "SHORT")
          
          const largest = liqs.length > 0
            ? liqs.reduce((max: { symbol: string; value: number }, l: Liquidation) => {
                const value = l.price * l.quantity
                return value > max.value ? { symbol: l.symbol, value } : max
              }, { symbol: liqs[0].symbol, value: liqs[0].price * liqs[0].quantity })
            : { symbol: "N/A", value: 0 }
          
          setIntelligence({
            total_liquidations_24h: liqs.length,
            long_liquidations: longLiqs.length,
            short_liquidations: shortLiqs.length,
            largest_liquidation: largest,
            liquidation_trend: longLiqs.length > shortLiqs.length ? "increasing" : "decreasing",
          })
        }
      } catch (error) {
        console.error("Failed to fetch liquidations:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 10000) // Update every 10 seconds
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      {/* Market Intelligence Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Total Liquidations (24h)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {intelligence?.total_liquidations_24h || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-red-500" />
              Long Liquidations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">
              {intelligence?.long_liquidations || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              Short Liquidations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">
              {intelligence?.short_liquidations || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Largest Liquidation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold">
              {intelligence?.largest_liquidation.symbol || "N/A"}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              ${intelligence?.largest_liquidation.value.toLocaleString(undefined, { maximumFractionDigits: 0 }) || "0"}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Market Sentiment */}
      <Card>
        <CardHeader>
          <CardTitle>Market Sentiment Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <div>
                <p className="text-sm font-medium">Liquidation Trend</p>
                <p className="text-xs text-muted-foreground">
                  {intelligence && intelligence.long_liquidations > intelligence.short_liquidations
                    ? "More longs being liquidated - potential bearish signal"
                    : intelligence && intelligence.short_liquidations > intelligence.long_liquidations
                    ? "More shorts being liquidated - potential bullish signal"
                    : "Balanced liquidations"}
                </p>
              </div>
              <Badge 
                variant={
                  intelligence?.liquidation_trend === "increasing" ? "destructive" :
                  intelligence?.liquidation_trend === "decreasing" ? "default" : "secondary"
                }
              >
                {intelligence?.liquidation_trend?.toUpperCase() || "STABLE"}
              </Badge>
            </div>

            {intelligence && intelligence.total_liquidations_24h > 0 && (
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-red-500/10 rounded border border-red-500/20">
                  <p className="text-xs text-muted-foreground">Long/Short Ratio</p>
                  <p className="text-lg font-bold">
                    {(intelligence.long_liquidations / intelligence.short_liquidations || 0).toFixed(2)}
                  </p>
                </div>
                <div className="p-3 bg-blue-500/10 rounded border border-blue-500/20">
                  <p className="text-xs text-muted-foreground">Liquidation Intensity</p>
                  <p className="text-lg font-bold">
                    {intelligence.total_liquidations_24h > 50 ? "HIGH" :
                     intelligence.total_liquidations_24h > 20 ? "MEDIUM" : "LOW"}
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Recent Liquidations */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Liquidations</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading liquidations...</p>
          ) : liquidations.length === 0 ? (
            <p className="text-sm text-muted-foreground">No recent liquidations</p>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Side</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>Quantity</TableHead>
                    <TableHead>Value</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {liquidations.slice(0, 20).map((liq, index) => (
                    <TableRow key={index}>
                      <TableCell className="text-xs font-mono">
                        {new Date(liq.timestamp).toLocaleTimeString()}
                      </TableCell>
                      <TableCell className="font-mono font-semibold">{liq.symbol}</TableCell>
                      <TableCell>
                        <Badge 
                          variant={liq.side === "BUY" || liq.side === "LONG" ? "destructive" : "default"}
                        >
                          {liq.side}
                        </Badge>
                      </TableCell>
                      <TableCell>${liq.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</TableCell>
                      <TableCell>{liq.quantity.toFixed(4)}</TableCell>
                      <TableCell className="font-semibold">
                        ${(liq.price * liq.quantity).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

