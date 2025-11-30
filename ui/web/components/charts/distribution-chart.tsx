"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"

interface DistributionChartProps {
  data: number[]
  height?: number
  title?: string
}

export function DistributionChart({
  data,
  height = 300,
  title = "Return Distribution",
}: DistributionChartProps) {
  // Bin the data into histogram buckets
  const min = Math.min(...data)
  const max = Math.max(...data)
  const bucketCount = 20
  const bucketSize = (max - min) / bucketCount

  const buckets = Array.from({ length: bucketCount }, (_, i) => ({
    range: `${(min + i * bucketSize).toFixed(2)}%`,
    count: 0,
    start: min + i * bucketSize,
    end: min + (i + 1) * bucketSize,
  }))

  data.forEach((value) => {
    const bucketIndex = Math.min(
      Math.floor((value - min) / bucketSize),
      bucketCount - 1
    )
    buckets[bucketIndex].count++
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={buckets}>
            <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.25 0 0)" />
            <XAxis
              dataKey="range"
              stroke="oklch(0.60 0 0)"
              style={{ fontSize: "11px" }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis
              stroke="oklch(0.60 0 0)"
              style={{ fontSize: "12px" }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "oklch(0.15 0 0)",
                border: "1px solid oklch(0.25 0 0)",
                borderRadius: "6px",
              }}
            />
            <Bar
              dataKey="count"
              fill="oklch(0.70 0.15 250)"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}


