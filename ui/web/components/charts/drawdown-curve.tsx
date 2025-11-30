"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import type { DrawdownPoint } from "@/lib/types"
import { format } from "date-fns"

interface DrawdownCurveProps {
  data: DrawdownPoint[]
  height?: number
}

export function DrawdownCurve({
  data,
  height = 300,
}: DrawdownCurveProps) {
  const formattedData = data.map((point) => ({
    ...point,
    date: format(new Date(point.timestamp), "MMM dd"),
    drawdownPercent: point.drawdown * 100,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Drawdown</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <AreaChart data={formattedData}>
            <defs>
              <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="oklch(0.65 0.20 25)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="oklch(0.65 0.20 25)"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.25 0 0)" />
            <XAxis
              dataKey="date"
              stroke="oklch(0.60 0 0)"
              style={{ fontSize: "12px" }}
            />
            <YAxis
              stroke="oklch(0.60 0 0)"
              style={{ fontSize: "12px" }}
              tickFormatter={(value) => `${value.toFixed(1)}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "oklch(0.15 0 0)",
                border: "1px solid oklch(0.25 0 0)",
                borderRadius: "6px",
              }}
              formatter={(value: number) => [
                `${value.toFixed(2)}%`,
                "Drawdown",
              ]}
            />
            <Area
              type="monotone"
              dataKey="drawdownPercent"
              stroke="oklch(0.65 0.20 25)"
              fill="url(#colorDrawdown)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}


