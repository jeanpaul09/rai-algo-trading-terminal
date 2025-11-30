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
import type { Experiment } from "@/lib/types"
import Link from "next/link"
import { format } from "date-fns"

interface ExperimentsTableProps {
  experiments: Experiment[]
}

export function ExperimentsTable({ experiments }: ExperimentsTableProps) {
  const getStatusColor = (status: Experiment["status"]) => {
    switch (status) {
      case "completed":
        return "default"
      case "running":
        return "secondary"
      case "failed":
        return "destructive"
      default:
        return "outline"
    }
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Strategy</TableHead>
            <TableHead>Market</TableHead>
            <TableHead>Period</TableHead>
            <TableHead>Sharpe</TableHead>
            <TableHead>Max DD</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {experiments.map((experiment) => (
            <TableRow key={experiment.id}>
              <TableCell className="font-mono text-xs">
                <Link
                  href={`/experiments/${experiment.id}`}
                  className="hover:underline"
                >
                  {experiment.id}
                </Link>
              </TableCell>
              <TableCell>{experiment.strategy_name}</TableCell>
              <TableCell>{experiment.market}</TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {format(new Date(experiment.start_date), "MMM dd")} -{" "}
                {format(new Date(experiment.end_date), "MMM dd, yyyy")}
              </TableCell>
              <TableCell>
                {experiment.metrics.sharpe.toFixed(2)}
              </TableCell>
              <TableCell>
                {(experiment.metrics.max_drawdown * 100).toFixed(2)}%
              </TableCell>
              <TableCell>
                <Badge variant={getStatusColor(experiment.status)}>
                  {experiment.status}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}


