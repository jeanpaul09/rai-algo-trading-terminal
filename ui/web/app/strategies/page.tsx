"use client"

import { Topbar } from "@/components/layout/topbar"
import { StrategiesTable } from "@/components/tables/strategies-table"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useEffect, useState } from "react"
import { fetchStrategies } from "@/lib/api"
import type { Strategy } from "@/lib/types"

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadStrategies = async () => {
      try {
        const data = await fetchStrategies()
        setStrategies(data)
      } catch (error) {
        console.error("Failed to load strategies:", error)
      } finally {
        setLoading(false)
      }
    }
    loadStrategies()
  }, [])

  return (
    <div className="flex flex-col h-full">
      <Topbar title="Strategy Lab" />
      <div className="flex-1 p-6 space-y-6">
        {/* Filters */}
        <div className="flex gap-4 items-center">
          <Input
            placeholder="Search strategies..."
            className="max-w-sm"
          />
          <Select>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="deployed">Deployed</SelectItem>
              <SelectItem value="validated">Validated</SelectItem>
              <SelectItem value="experimental">Experimental</SelectItem>
            </SelectContent>
          </Select>
          <Select>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by market" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Markets</SelectItem>
              <SelectItem value="crypto">Crypto</SelectItem>
              <SelectItem value="stocks">Stocks</SelectItem>
              <SelectItem value="prediction">Prediction Markets</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Strategies Table */}
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading strategies...</p>
        ) : (
          <StrategiesTable strategies={strategies} />
        )}
      </div>
    </div>
  )
}
