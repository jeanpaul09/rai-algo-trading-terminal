"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { EquityCurve } from "@/components/charts/equity-curve"
import { DrawdownCurve } from "@/components/charts/drawdown-curve"
import type { EquityPoint, DrawdownPoint } from "@/lib/types"

interface PerformancePanelProps {
  equityCurve: EquityPoint[]
  drawdownCurve: DrawdownPoint[]
}

export function PerformancePanel({
  equityCurve,
  drawdownCurve,
}: PerformancePanelProps) {
  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <EquityCurve data={equityCurve} />
        <DrawdownCurve data={drawdownCurve} />
      </div>
    </div>
  )
}


