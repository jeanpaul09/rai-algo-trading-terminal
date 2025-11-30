"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ExperimentsTable } from "@/components/tables/experiments-table"
import type { Experiment } from "@/lib/types"

interface ExperimentsPanelProps {
  experiments: Experiment[]
}

export function ExperimentsPanel({ experiments }: ExperimentsPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Experiments</CardTitle>
      </CardHeader>
      <CardContent>
        <ExperimentsTable experiments={experiments.slice(0, 10)} />
      </CardContent>
    </Card>
  )
}


