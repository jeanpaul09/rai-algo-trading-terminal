import { Topbar } from "@/components/layout/topbar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { LiquidationsViewer } from "@/components/liquidations/liquidations-viewer"
import { PositionsViewer } from "@/components/liquidations/positions-viewer"

export default async function LiquidationsPage() {
  return (
    <div className="flex flex-col h-full">
      <Topbar title="Liquidations & Positions" />
      <div className="flex-1 p-6 space-y-6">
        <div className="grid gap-6 lg:grid-cols-2">
          <LiquidationsViewer />
          <PositionsViewer />
        </div>
      </div>
    </div>
  )
}


