"use client"

import { Calendar } from "lucide-react"
import { format } from "date-fns"

interface TopbarProps {
  title?: string
}

export function Topbar({ title }: TopbarProps) {
  return (
    <div className="flex h-16 items-center justify-between border-b border-border bg-card px-6">
      <h2 className="text-2xl font-semibold">{title || "Dashboard"}</h2>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Calendar className="h-4 w-4" />
          <span>{format(new Date(), "MMM dd, yyyy")}</span>
        </div>
      </div>
    </div>
  )
}


