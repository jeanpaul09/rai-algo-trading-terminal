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

interface Position {
  trader_id: string
  symbol: string
  side: string
  size: number
  entry_price: number
  current_price: number
  pnl: number
}

export function PositionsViewer() {
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        const cleanBaseUrl = (API_BASE_URL || "").replace(/\/+$/, "")
        const url = `${cleanBaseUrl}/api/positions`.replace(/([^:]\/)\/+/g, "$1")
        const response = await fetch(url)
        if (response.ok) {
          const data = await response.json()
          setPositions(data || [])
        }
      } catch (error) {
        console.error("Failed to fetch positions:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 2000) // Update every 2 seconds
    return () => clearInterval(interval)
  }, [])

  const totalPnL = positions.reduce((sum, p) => sum + (p.pnl || 0), 0)
  const longPositions = positions.filter((p) => p.side === "long" || p.side === "BUY")
  const shortPositions = positions.filter((p) => p.side === "short" || p.side === "SELL")

  return (
    <Card>
      <CardHeader>
        <CardTitle>Open Positions</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading...</p>
        ) : (
          <div className="space-y-4">
            {/* Summary */}
            <div className="grid grid-cols-3 gap-4 p-3 bg-muted rounded">
              <div>
                <p className="text-xs text-muted-foreground">Total Positions</p>
                <p className="text-lg font-semibold">{positions.length}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Long / Short</p>
                <p className="text-lg font-semibold">
                  {longPositions.length} / {shortPositions.length}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Total PnL</p>
                <p className={`text-lg font-semibold ${totalPnL >= 0 ? "text-green-500" : "text-red-500"}`}>
                  {totalPnL >= 0 ? "+" : ""}${totalPnL.toFixed(2)}
                </p>
              </div>
            </div>

            {/* Positions Table */}
            <div className="rounded-md border max-h-96 overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Side</TableHead>
                    <TableHead>Size</TableHead>
                    <TableHead>Entry</TableHead>
                    <TableHead>Current</TableHead>
                    <TableHead>PnL</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {positions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-muted-foreground">
                        No open positions
                      </TableCell>
                    </TableRow>
                  ) : (
                    positions.map((pos, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-mono">{pos.symbol}</TableCell>
                        <TableCell>
                          <Badge variant={pos.side === "long" || pos.side === "BUY" ? "default" : "secondary"}>
                            {pos.side}
                          </Badge>
                        </TableCell>
                        <TableCell>{pos.size.toFixed(4)}</TableCell>
                        <TableCell>${pos.entry_price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</TableCell>
                        <TableCell>${pos.current_price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</TableCell>
                        <TableCell className={pos.pnl >= 0 ? "text-green-500" : "text-red-500"}>
                          {pos.pnl >= 0 ? "+" : ""}${pos.pnl.toFixed(2)}
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


