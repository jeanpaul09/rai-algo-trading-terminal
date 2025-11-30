"use client"

import { useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Brain, TrendingUp, AlertCircle, ArrowRight, Settings, DollarSign } from "lucide-react"
import type { BrainFeedEntry } from "@/lib/types"
import { format } from "date-fns"

interface BrainFeedProps {
  entries: BrainFeedEntry[]
  maxEntries?: number
}

export function BrainFeed({ entries, maxEntries = 100 }: BrainFeedProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new entries arrive
  useEffect(() => {
    if (scrollRef.current) {
      const container = scrollRef.current.closest('[data-radix-scroll-area-viewport]') as HTMLElement
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    }
  }, [entries])

  const displayedEntries = entries.slice(-maxEntries)

  const getEntryIcon = (type: string) => {
    switch (type) {
      case "analysis":
        return Brain
      case "signal":
        return TrendingUp
      case "decision":
        return ArrowRight
      case "trade":
        return DollarSign
      case "adjustment":
        return Settings
      case "warning":
        return AlertCircle
      default:
        return Brain
    }
  }

  const getEntryColor = (type: string) => {
    switch (type) {
      case "analysis":
        return "text-blue-500"
      case "signal":
        return "text-green-500"
      case "decision":
        return "text-purple-500"
      case "trade":
        return "text-yellow-500"
      case "adjustment":
        return "text-indigo-500"
      case "warning":
        return "text-red-500"
      default:
        return "text-gray-500"
    }
  }

  const getEntryBadgeVariant = (type: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (type) {
      case "warning":
        return "destructive"
      case "trade":
        return "default"
      case "signal":
        return "secondary"
      default:
        return "outline"
    }
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="border-b pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Agent Brain Feed
          </CardTitle>
          <Badge variant="outline" className="text-xs">
            {entries.length} entries
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 p-0">
        <ScrollArea className="h-full">
          <div className="p-4 space-y-3" ref={scrollRef}>
            {displayedEntries.length === 0 ? (
              <div className="text-center text-muted-foreground py-8 text-sm">
                No brain activity yet. The agent will start logging analysis, signals, and decisions here.
              </div>
            ) : (
              displayedEntries.map((entry) => {
                const Icon = getEntryIcon(entry.type)
                const color = getEntryColor(entry.type)

                return (
                  <div
                    key={entry.id}
                    className="border rounded-lg p-3 hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div className="flex items-center gap-2 flex-1">
                        <Icon className={`h-4 w-4 ${color} flex-shrink-0 mt-0.5`} />
                        <Badge
                          variant={getEntryBadgeVariant(entry.type)}
                          className="text-xs"
                        >
                          {entry.type.toUpperCase()}
                        </Badge>
                        {entry.strategy && (
                          <Badge variant="outline" className="text-xs">
                            {entry.strategy}
                          </Badge>
                        )}
                        <span className="text-xs text-muted-foreground ml-auto">
                          {format(new Date(entry.timestamp), "HH:mm:ss")}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-foreground whitespace-pre-wrap">
                      {entry.content}
                    </p>
                    {entry.data && Object.keys(entry.data).length > 0 && (
                      <div className="mt-2 pt-2 border-t">
                        <div className="text-xs text-muted-foreground space-y-1">
                          {Object.entries(entry.data).map(([key, value]) => (
                            <div key={key} className="flex gap-2">
                              <span className="font-medium">{key}:</span>
                              <span className="font-mono">
                                {typeof value === "object"
                                  ? JSON.stringify(value, null, 2)
                                  : String(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}

