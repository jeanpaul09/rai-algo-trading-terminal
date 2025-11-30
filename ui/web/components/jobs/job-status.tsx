"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Loader2, CheckCircle2, XCircle, Clock } from "lucide-react"
import { useEffect, useState } from "react"

interface Job {
  id: string
  type: string
  status: "queued" | "running" | "completed" | "failed"
  created_at: string
  progress?: string
  result?: any
  error?: string
}

export function JobStatus() {
  const [jobs, setJobs] = useState<Job[]>([])

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        const cleanBaseUrl = (API_BASE_URL || "").replace(/\/+$/, "")
        const url = `${cleanBaseUrl}/api/jobs`.replace(/([^:]\/)\/+/g, "$1")
        const response = await fetch(url)
        if (response.ok) {
          const data = await response.json()
          setJobs(data.slice(0, 5)) // Show last 5 jobs
        }
      } catch (error) {
        console.error("Failed to fetch jobs:", error)
      }
    }

    fetchJobs()
    const interval = setInterval(fetchJobs, 2000) // Poll every 2 seconds
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status: Job["status"]) => {
    switch (status) {
      case "running":
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: Job["status"]) => {
    switch (status) {
      case "running":
        return "secondary"
      case "completed":
        return "default"
      case "failed":
        return "destructive"
      default:
        return "outline"
    }
  }

  if (jobs.length === 0) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Jobs</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {jobs.map((job) => (
            <div
              key={job.id}
              className="flex items-center justify-between p-2 rounded border"
            >
              <div className="flex items-center gap-2">
                {getStatusIcon(job.status)}
                <div>
                  <p className="text-sm font-medium">
                    {job.type === "backtest" ? "Backtest" : "Optimization"}
                  </p>
                  {job.progress && (
                    <p className="text-xs text-muted-foreground">{job.progress}</p>
                  )}
                </div>
              </div>
              <Badge variant={getStatusColor(job.status)}>{job.status}</Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}


