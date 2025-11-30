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
import { TrendingDown, TrendingUp, AlertCircle } from "lucide-react"
import { format } from "date-fns"

interface Liquidation {
  symbol: string
  side: string
  order_type: string
  price: number
  quantity: number
  timestamp: string
}

export function LiquidationsViewer() {
  const [liquidations, setLiquidations] = useState<Liquidation[]>([])
  const [openInterest, setOpenInterest] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        const response = await fetch(`${API_BASE_URL}/api/liquidations?exchange=binance`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          // Don't cache
          cache: "no-store",
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        setLiquidations(data.liquidations || [])
        setOpenInterest(data.open_interest || {})
        setError(null)
      } catch (error: any) {
        console.error("Failed to fetch liquidations:", error)
        setError(error.message || "Failed to connect to API server")
        // Keep showing old data if available
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const longLiquidations = liquidations.filter((l) => l.side === "BUY" || l.side === "LONG")
  const shortLiquidations = liquidations.filter((l) => l.side === "SELL" || l.side === "SHORT")

  return (
    <Card>
      <CardHeader>
        <CardTitle>Liquidations (Real Data)</CardTitle>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded flex items-center gap-2 text-sm text-red-400">
            <AlertCircle className="h-4 w-4" />
            <span>API Error: {error}. Make sure API server is running: <code className="bg-black/20 px-1 rounded">python3 api_server.py</code></span>
          </div>
        )}
        
        {loading && !liquidations.length ? (
          <p className="text-sm text-muted-foreground">Loading real liquidation data from Binance...</p>
        ) : (
          <div className="space-y-4">
            {/* Open Interest Summary */}
            {Object.keys(openInterest).length > 0 && (
              <div className="grid grid-cols-3 gap-2 p-3 bg-muted rounded">
                {Object.entries(openInterest).map(([symbol, data]: [string, any]) => (
                  <div key={symbol}>
                    <p className="text-xs text-muted-foreground">{symbol}</p>
                    <p className="text-sm font-semibold">
                      ${(data.open_interest / 1e6).toFixed(1)}M
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Liquidation Stats */}
            <div className="flex gap-4">
              <div className="flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-red-500" />
                <span className="text-sm">
                  Long: <strong>{longLiquidations.length}</strong>
                </span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-500" />
                <span className="text-sm">
                  Short: <strong>{shortLiquidations.length}</strong>
                </span>
              </div>
            </div>

            {/* Liquidations Table */}
            <div className="rounded-md border max-h-96 overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Side</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>Quantity</TableHead>
                    <TableHead>Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {liquidations.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center text-muted-foreground">
                        {error ? "API server not running" : "No liquidations data available"}
                      </TableCell>
                    </TableRow>
                  ) : (
                    liquidations.slice(0, 20).map((liq, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-mono text-sm">{liq.symbol}</TableCell>
                        <TableCell>
                          <Badge
                            variant={liq.side === "BUY" || liq.side === "LONG" ? "destructive" : "default"}
                          >
                            {liq.side}
                          </Badge>
                        </TableCell>
                        <TableCell>${liq.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</TableCell>
                        <TableCell>{liq.quantity.toFixed(4)}</TableCell>
                        <TableCell className="text-xs text-muted-foreground">
                          {format(new Date(liq.timestamp), "HH:mm:ss")}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
