"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { CorrelationMatrix } from "@/lib/types"
import { cn } from "@/lib/utils"

interface CorrelationMatrixProps {
  data: CorrelationMatrix
  height?: number
}

export function CorrelationMatrixChart({
  data,
  height = 400,
}: CorrelationMatrixProps) {
  const { strategies, correlations } = data

  const getColor = (value: number) => {
    if (value >= 0.7) return "bg-green-600"
    if (value >= 0.3) return "bg-green-400"
    if (value >= -0.3) return "bg-gray-600"
    if (value >= -0.7) return "bg-red-400"
    return "bg-red-600"
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Strategy Correlation Matrix</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-auto" style={{ height }}>
          <div className="inline-block min-w-full">
            <table className="border-collapse">
              <thead>
                <tr>
                  <th className="p-2 text-xs text-muted-foreground text-left sticky left-0 bg-card z-10">
                    Strategy
                  </th>
                  {strategies.map((strategy) => (
                    <th
                      key={strategy}
                      className="p-2 text-xs text-muted-foreground text-center min-w-[80px]"
                    >
                      {strategy.substring(0, 10)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {strategies.map((strategy, i) => (
                  <tr key={strategy}>
                    <td className="p-2 text-xs sticky left-0 bg-card z-10 border-r border-border">
                      {strategy.substring(0, 15)}
                    </td>
                    {correlations[i].map((corr, j) => (
                      <td
                        key={j}
                        className={cn(
                          "p-2 text-center text-xs text-white",
                          getColor(corr),
                          i === j && "font-bold"
                        )}
                      >
                        {corr.toFixed(2)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}


