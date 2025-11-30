"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CorrelationMatrixChart } from "@/components/charts/correlation-matrix"
import type { CorrelationMatrix, MarketExposure } from "@/lib/types"
import { AlertCircle, CheckCircle2, AlertTriangle } from "lucide-react"

interface RiskPanelProps {
  correlationMatrix: CorrelationMatrix
  marketExposure: MarketExposure[]
  currentDrawdown: number
  maxDrawdownAllowed: number
}

export function RiskPanel({
  correlationMatrix,
  marketExposure,
  currentDrawdown,
  maxDrawdownAllowed,
}: RiskPanelProps) {
  const drawdownPercent = Math.abs(currentDrawdown * 100)
  const maxDrawdownPercent = Math.abs(maxDrawdownAllowed * 100)
  const drawdownRatio = drawdownPercent / maxDrawdownPercent

  const getRiskStatus = () => {
    if (drawdownRatio >= 0.9) return { status: "CRITICAL", icon: AlertCircle, color: "text-red-500" }
    if (drawdownRatio >= 0.7) return { status: "WARNING", icon: AlertTriangle, color: "text-yellow-500" }
    return { status: "OK", icon: CheckCircle2, color: "text-green-500" }
  }

  const riskStatus = getRiskStatus()
  const StatusIcon = riskStatus.icon

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Risk Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  Current Drawdown
                </span>
                <div className="flex items-center gap-2">
                  <StatusIcon className={`h-5 w-5 ${riskStatus.color}`} />
                  <span className={`font-semibold ${riskStatus.color}`}>
                    {riskStatus.status}
                  </span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Drawdown: {drawdownPercent.toFixed(2)}%</span>
                  <span>Max: {maxDrawdownPercent.toFixed(2)}%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all"
                    style={{ width: `${Math.min(drawdownRatio * 100, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Market Exposure</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {marketExposure.map((market) => (
                <div key={market.market} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>{market.market}</span>
                    <span>{market.percentage.toFixed(1)}%</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary"
                      style={{ width: `${market.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <CorrelationMatrixChart data={correlationMatrix} />
    </div>
  )
}


