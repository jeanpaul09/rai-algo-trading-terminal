"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Settings, Play, Square, TrendingUp, TrendingDown } from "lucide-react"
import type { StrategyControl } from "@/lib/types"
import { ScrollArea } from "@/components/ui/scroll-area"

interface StrategyControlPanelProps {
  strategies: StrategyControl[]
  onModeChange: (strategyName: string, mode: "OFF" | "DEMO" | "LIVE") => void
  onEditParameters: (strategyName: string) => void
  onTriggerBacktest: (strategyName: string) => void
}

export function StrategyControlPanel({
  strategies,
  onModeChange,
  onEditParameters,
  onTriggerBacktest,
}: StrategyControlPanelProps) {
  const getModeColor = (mode: string) => {
    switch (mode) {
      case "LIVE":
        return "bg-red-500/20 text-red-500 border-red-500/50"
      case "DEMO":
        return "bg-yellow-500/20 text-yellow-500 border-yellow-500/50"
      case "OFF":
        return "bg-gray-500/20 text-gray-500 border-gray-500/50"
      default:
        return "bg-gray-500/20 text-gray-500 border-gray-500/50"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "in-position":
        return <TrendingUp className="h-4 w-4 text-green-500" />
      case "scanning":
        return <Play className="h-4 w-4 text-blue-500 animate-pulse" />
      case "cooling-down":
        return <Square className="h-4 w-4 text-yellow-500" />
      case "error":
        return <TrendingDown className="h-4 w-4 text-red-500" />
      default:
        return <Square className="h-4 w-4 text-gray-500" />
    }
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="border-b pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Strategy Control</CardTitle>
          <Badge variant="outline">{strategies.length} strategies</Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 p-0">
        <ScrollArea className="h-full">
          <div className="p-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Strategy</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Mode</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Exposure</TableHead>
                  <TableHead>Last PnL</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {strategies.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground">
                      No strategies configured
                    </TableCell>
                  </TableRow>
                ) : (
                  strategies.map((strategy) => (
                    <TableRow key={strategy.name}>
                      <TableCell>
                        <div>
                          <div className="font-semibold">{strategy.name}</div>
                          <div className="text-xs text-muted-foreground">
                            {strategy.description}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs">
                          {strategy.category}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Select
                          value={strategy.mode}
                          onValueChange={(value) =>
                            onModeChange(strategy.name, value as "OFF" | "DEMO" | "LIVE")
                          }
                        >
                          <SelectTrigger className="w-24 h-8">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="OFF">OFF</SelectItem>
                            <SelectItem value="DEMO">DEMO</SelectItem>
                            <SelectItem value="LIVE">LIVE</SelectItem>
                          </SelectContent>
                        </Select>
                        <Badge
                          className={`mt-1 ${getModeColor(strategy.mode)}`}
                          variant="outline"
                        >
                          {strategy.mode}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(strategy.status)}
                          <span className="text-sm capitalize">
                            {strategy.status.replace("-", " ")}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {strategy.currentExposure !== undefined ? (
                          <span className="text-sm font-mono">
                            ${strategy.currentExposure.toLocaleString(undefined, {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}
                          </span>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {strategy.lastPnL !== undefined ? (
                          <span
                            className={`text-sm font-semibold ${
                              strategy.lastPnL >= 0 ? "text-green-500" : "text-red-500"
                            }`}
                          >
                            {strategy.lastPnL >= 0 ? "+" : ""}
                            ${strategy.lastPnL.toLocaleString(undefined, {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}
                          </span>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onEditParameters(strategy.name)}
                          >
                            <Settings className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onTriggerBacktest(strategy.name)}
                          >
                            Backtest
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}

