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
import { useEffect, useState } from "react"
import { TrendingUp, TrendingDown, Users, DollarSign, Activity } from "lucide-react"

interface MarketPosition {
  symbol: string
  side: "LONG" | "SHORT" | "long" | "short" | "BUY" | "SELL"
  size: number
  entry_price: number
  current_price: number
  pnl: number
  pnl_pct: number
  leverage?: number
  trader_id?: string
}

interface MarketStats {
  total_long_value: number
  total_short_value: number
  long_short_ratio: number
  total_traders: number
  largest_position: string
}

export function MarketPositionsView() {
  const [positions, setPositions] = useState<MarketPosition[]>([])
  const [stats, setStats] = useState<MarketStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        
        // Fetch positions
        const positionsRes = await fetch(`${API_BASE_URL}/api/positions`, {
          cache: "no-store",
        })
        const positionsData = positionsRes.ok ? await positionsRes.json() : []
        
        // Fetch liquidations for market context
        const liqRes = await fetch(`${API_BASE_URL}/api/liquidations?exchange=binance`, {
          cache: "no-store",
        })
        const liqData = liqRes.ok ? await liqRes.json() : { liquidations: [] }
        
        // Combine and process
        const allPositions: MarketPosition[] = positionsData.positions || []
        
        // Calculate stats
        const longs = allPositions.filter((p: MarketPosition) => p.side === "LONG" || p.side === "long" || p.side === "BUY")
        const shorts = allPositions.filter((p: MarketPosition) => p.side === "SHORT" || p.side === "short" || p.side === "SELL")
        
        const totalLongValue = longs.reduce((sum: number, p: MarketPosition) => sum + (p.size * p.current_price), 0)
        const totalShortValue = shorts.reduce((sum: number, p: MarketPosition) => sum + (p.size * p.current_price), 0)
        
        setStats({
          total_long_value: totalLongValue,
          total_short_value: totalShortValue,
          long_short_ratio: totalShortValue > 0 ? totalLongValue / totalShortValue : 0,
          total_traders: new Set(allPositions.map(p => p.trader_id)).size,
          largest_position: allPositions.length > 0 
            ? allPositions.reduce((max: MarketPosition, p: MarketPosition) => Math.abs(p.size * p.current_price) > Math.abs(max.size * max.current_price) ? p : max, allPositions[0]).symbol
            : "N/A",
        })
        
        setPositions(allPositions)
      } catch (error) {
        console.error("Failed to fetch positions:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const totalPnL = positions.reduce((sum: number, p: MarketPosition) => sum + (p.pnl || 0), 0)

  return (
    <div className="space-y-6">
      {/* Market Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              Total Long Value
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${stats?.total_long_value.toLocaleString(undefined, { maximumFractionDigits: 0 }) || "0"}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-red-500" />
              Total Short Value
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${stats?.total_short_value.toLocaleString(undefined, { maximumFractionDigits: 0 }) || "0"}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Long/Short Ratio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.long_short_ratio.toFixed(2) || "0.00"}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Users className="h-4 w-4" />
              Active Traders
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.total_traders || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Positions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Market Positions (All Traders)</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading positions...</p>
          ) : positions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>No open positions detected</p>
              <p className="text-xs mt-2">Positions will appear here when traders are active</p>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Side</TableHead>
                    <TableHead>Size</TableHead>
                    <TableHead>Entry Price</TableHead>
                    <TableHead>Current Price</TableHead>
                    <TableHead>Leverage</TableHead>
                    <TableHead>PnL</TableHead>
                    <TableHead>PnL %</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {positions.map((pos, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-mono font-semibold">{pos.symbol}</TableCell>
                      <TableCell>
                        <Badge 
                          variant={pos.side === "LONG" || pos.side === "long" ? "default" : "secondary"}
                          className={pos.side === "SHORT" || pos.side === "short" ? "bg-red-500/20 text-red-400" : ""}
                        >
                          {pos.side}
                        </Badge>
                      </TableCell>
                      <TableCell>{pos.size.toFixed(4)}</TableCell>
                      <TableCell>${pos.entry_price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</TableCell>
                      <TableCell>${pos.current_price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</TableCell>
                      <TableCell>{pos.leverage || "1x"}</TableCell>
                      <TableCell className={pos.pnl >= 0 ? "text-green-500 font-semibold" : "text-red-500 font-semibold"}>
                        {pos.pnl >= 0 ? "+" : ""}${pos.pnl.toFixed(2)}
                      </TableCell>
                      <TableCell className={pos.pnl_pct >= 0 ? "text-green-500" : "text-red-500"}>
                        {pos.pnl_pct >= 0 ? "+" : ""}{(pos.pnl_pct * 100).toFixed(2)}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Total PnL Summary */}
      {positions.length > 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Total Market PnL</span>
              <span className={`text-2xl font-bold ${totalPnL >= 0 ? "text-green-500" : "text-red-500"}`}>
                {totalPnL >= 0 ? "+" : ""}${totalPnL.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

