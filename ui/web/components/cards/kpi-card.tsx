"use client"

import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"

interface KPICardProps {
  label: string
  value: string | number
  trend?: "up" | "down" | "neutral"
  trendValue?: string
  className?: string
}

export function KPICard({
  label,
  value,
  trend = "neutral",
  trendValue,
  className,
}: KPICardProps) {
  const TrendIcon =
    trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus

  return (
    <Card className={cn("", className)}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground mb-1">{label}</p>
            <p className="text-3xl font-bold">{value}</p>
          </div>
          {trend !== "neutral" && (
            <div
              className={cn(
                "flex items-center gap-1 text-sm",
                trend === "up" && "text-green-500",
                trend === "down" && "text-red-500"
              )}
            >
              <TrendIcon className="h-4 w-4" />
              {trendValue && <span>{trendValue}</span>}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}


