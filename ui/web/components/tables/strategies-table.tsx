"use client"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import type { Strategy } from "@/lib/types"
import Link from "next/link"

interface StrategiesTableProps {
  strategies: Strategy[]
}

export function StrategiesTable({ strategies }: StrategiesTableProps) {
  const getStateColor = (state: Strategy["state"]) => {
    switch (state) {
      case "deployed":
        return "default"
      case "validated":
        return "secondary"
      case "experimental":
        return "outline"
      default:
        return "outline"
    }
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Markets</TableHead>
            <TableHead>State</TableHead>
            <TableHead>Best Sharpe</TableHead>
            <TableHead>Worst DD</TableHead>
            <TableHead>Tags</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {strategies.map((strategy) => (
            <TableRow key={strategy.name}>
              <TableCell className="font-medium">
                <Link
                  href={`/strategies/${encodeURIComponent(strategy.name)}`}
                  className="hover:underline"
                >
                  {strategy.name}
                </Link>
              </TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-1">
                  {strategy.markets.map((market) => (
                    <Badge key={market} variant="outline" className="text-xs">
                      {market}
                    </Badge>
                  ))}
                </div>
              </TableCell>
              <TableCell>
                <Badge variant={getStateColor(strategy.state)}>
                  {strategy.state}
                </Badge>
              </TableCell>
              <TableCell>
                {strategy.best_sharpe
                  ? strategy.best_sharpe.toFixed(2)
                  : "—"}
              </TableCell>
              <TableCell>
                {strategy.worst_drawdown
                  ? `${(strategy.worst_drawdown * 100).toFixed(2)}%`
                  : "—"}
              </TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-1">
                  {strategy.tags.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}


