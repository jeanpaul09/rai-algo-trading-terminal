"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts"
import type { EquityPoint } from "@/lib/types"
import { format } from "date-fns"

interface EquityCurveProps {
  data: EquityPoint[]
  height?: number
  showReferenceLine?: boolean
  referenceValue?: number
}

export function EquityCurve({
  data,
  height = 300,
  showReferenceLine = false,
  referenceValue,
}: EquityCurveProps) {
  const formattedData = data.map((point) => ({
    ...point,
    date: format(new Date(point.timestamp), "MMM dd"),
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Equity Curve</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={formattedData}>
            <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.25 0 0)" />
            <XAxis
              dataKey="date"
              stroke="oklch(0.60 0 0)"
              style={{ fontSize: "12px" }}
            />
            <YAxis
              stroke="oklch(0.60 0 0)"
              style={{ fontSize: "12px" }}
              tickFormatter={(value) => `$${value.toLocaleString()}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "oklch(0.15 0 0)",
                border: "1px solid oklch(0.25 0 0)",
                borderRadius: "6px",
              }}
              formatter={(value: number) => [
                `$${value.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}`,
                "Equity",
              ]}
            />
            {showReferenceLine && referenceValue && (
              <ReferenceLine
                y={referenceValue}
                stroke="oklch(0.60 0 0)"
                strokeDasharray="2 2"
              />
            )}
            <Line
              type="monotone"
              dataKey="equity"
              stroke="oklch(0.70 0.15 250)"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}


