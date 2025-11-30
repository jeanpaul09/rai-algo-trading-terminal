import { Topbar } from "@/components/layout/topbar"
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
import { EquityCurve } from "@/components/charts/equity-curve"
import { AlertCircle, CheckCircle2, AlertTriangle } from "lucide-react"
import { fetchLiveStatus } from "@/lib/api"
import { format } from "date-fns"

export default async function LivePage() {
  // REAL DATA ONLY - throw error if backend unavailable
  const liveStatus = await fetchLiveStatus();

  // Generate equity curve from positions and PnL data
  // For now, use empty array - can be populated from trading history
  const liveEquityCurve: Array<{ timestamp: string; equity: number }> = []
  
  // If we have positions, we can estimate equity curve
  if (liveStatus.positions && liveStatus.positions.length > 0) {
    // Simple equity calculation from positions
    const baseEquity = liveStatus.equity
    liveEquityCurve.push({
      timestamp: new Date().toISOString(),
      equity: baseEquity
    })
  }

  const getRiskStatusIcon = (status: string) => {
    switch (status) {
      case "CRITICAL":
        return AlertCircle
      case "WARNING":
        return AlertTriangle
      default:
        return CheckCircle2
    }
  }

  const getRiskStatusColor = (status: string) => {
    switch (status) {
      case "CRITICAL":
        return "text-red-500"
      case "WARNING":
        return "text-yellow-500"
      default:
        return "text-green-500"
    }
  }

  const RiskIcon = getRiskStatusIcon(liveStatus.risk_status)
  const riskColor = getRiskStatusColor(liveStatus.risk_status)

  return (
    <div className="flex flex-col h-full">
      <Topbar title="Live Trading Lab" />
      <div className="flex-1 p-6 space-y-6">
        {/* Live PnL & Equity */}
        <Card>
          <CardHeader>
            <CardTitle>Live PnL & Equity</CardTitle>
          </CardHeader>
          <CardContent>
            <EquityCurve data={liveEquityCurve} height={250} />
            <div className="grid grid-cols-2 gap-4 mt-4">
              <div>
                <p className="text-xs text-muted-foreground">Current Equity</p>
                <p className="text-2xl font-bold">
                  ${liveStatus.equity.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Daily PnL</p>
                <p
                  className={`text-2xl font-bold ${
                    liveStatus.daily_pnl >= 0 ? "text-green-500" : "text-red-500"
                  }`}
                >
                  {liveStatus.daily_pnl >= 0 ? "+" : ""}
                  ${liveStatus.daily_pnl.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Risk Status */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  Overall Status
                </span>
                <div className="flex items-center gap-2">
                  <RiskIcon className={`h-5 w-5 ${riskColor}`} />
                  <span className={`font-semibold ${riskColor}`}>
                    {liveStatus.risk_status}
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground">
                    Total Exposure
                  </p>
                  <p className="text-lg font-semibold">
                    ${liveStatus.total_exposure.toLocaleString()}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Max: ${liveStatus.max_exposure.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">
                    Current Drawdown
                  </p>
                  <p className="text-lg font-semibold text-red-500">
                    {(liveStatus.current_drawdown * 100).toFixed(2)}%
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Max Allowed:{" "}
                    {(liveStatus.max_drawdown_allowed * 100).toFixed(2)}%
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Open Positions */}
        <Card>
          <CardHeader>
            <CardTitle>Open Positions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Exchange</TableHead>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Side</TableHead>
                    <TableHead>Size</TableHead>
                    <TableHead>Entry Price</TableHead>
                    <TableHead>Mark Price</TableHead>
                    <TableHead>Unrealized PnL</TableHead>
                    <TableHead>Leverage</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {liveStatus.positions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center text-muted-foreground">
                        No open positions
                      </TableCell>
                    </TableRow>
                  ) : (
                    liveStatus.positions.map((position, index) => (
                      <TableRow key={index}>
                        <TableCell>{position.exchange}</TableCell>
                        <TableCell className="font-mono">
                          {position.symbol}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              position.side === "long" ? "default" : "secondary"
                            }
                          >
                            {position.side}
                          </Badge>
                        </TableCell>
                        <TableCell>{position.size}</TableCell>
                        <TableCell>${position.entry_price.toLocaleString()}</TableCell>
                        <TableCell>${position.mark_price.toLocaleString()}</TableCell>
                        <TableCell
                          className={
                            position.unrealized_pnl >= 0
                              ? "text-green-500"
                              : "text-red-500"
                          }
                        >
                          {position.unrealized_pnl >= 0 ? "+" : ""}
                          ${position.unrealized_pnl.toLocaleString(undefined, {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}
                        </TableCell>
                        <TableCell>
                          {position.leverage ? `${position.leverage}x` : "—"}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        {/* Venue Overview */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {liveStatus.venue_overview.map((venue) => (
            <Card key={venue.venue}>
              <CardHeader>
                <CardTitle>{venue.venue}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div>
                    <p className="text-xs text-muted-foreground">
                      Notional Exposure
                    </p>
                    <p className="text-lg font-semibold">
                      ${venue.notional_exposure.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">PnL</p>
                    <p
                      className={`text-lg font-semibold ${
                        venue.pnl >= 0 ? "text-green-500" : "text-red-500"
                      }`}
                    >
                      {venue.pnl >= 0 ? "+" : ""}
                      ${venue.pnl.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </p>
                  </div>
                  {venue.funding_impact !== undefined && (
                    <div>
                      <p className="text-xs text-muted-foreground">
                        Funding Impact
                      </p>
                      <p className="text-sm font-semibold">
                        ${venue.funding_impact.toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}


