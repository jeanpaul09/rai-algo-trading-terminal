"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Play, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface RunBacktestDialogProps {
  strategyName?: string
  onComplete?: (jobId: string) => void
}

export function RunBacktestDialog({ strategyName, onComplete }: RunBacktestDialogProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()
  
  const [formData, setFormData] = useState({
    strategy_name: strategyName || "",
    market: "BTC/USD",
    start_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
    end_date: new Date().toISOString().split("T")[0],
    initial_capital: "10000",
    data_source: "binance",
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await fetch("/api/backtest/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          initial_capital: parseFloat(formData.initial_capital),
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to start backtest")
      }

      const data = await response.json()
      
      toast({
        title: "Backtest Started",
        description: `Job ID: ${data.job_id}`,
      })

      setOpen(false)
      if (onComplete) {
        onComplete(data.job_id)
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to start backtest",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Play className="h-4 w-4 mr-2" />
          Run Backtest
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Run Backtest</DialogTitle>
          <DialogDescription>
            Configure and run a backtest for this strategy
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="strategy_name">Strategy Name</Label>
              <Input
                id="strategy_name"
                value={formData.strategy_name}
                onChange={(e) =>
                  setFormData({ ...formData, strategy_name: e.target.value })
                }
                required
              />
            </div>
            <div>
              <Label htmlFor="market">Market</Label>
              <Input
                id="market"
                value={formData.market}
                onChange={(e) =>
                  setFormData({ ...formData, market: e.target.value })
                }
                placeholder="BTC/USD"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="start_date">Start Date</Label>
              <Input
                id="start_date"
                type="date"
                value={formData.start_date}
                onChange={(e) =>
                  setFormData({ ...formData, start_date: e.target.value })
                }
                required
              />
            </div>
            <div>
              <Label htmlFor="end_date">End Date</Label>
              <Input
                id="end_date"
                type="date"
                value={formData.end_date}
                onChange={(e) =>
                  setFormData({ ...formData, end_date: e.target.value })
                }
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="initial_capital">Initial Capital</Label>
              <Input
                id="initial_capital"
                type="number"
                value={formData.initial_capital}
                onChange={(e) =>
                  setFormData({ ...formData, initial_capital: e.target.value })
                }
                required
              />
            </div>
            <div>
              <Label htmlFor="data_source">Data Source</Label>
              <Select
                value={formData.data_source}
                onValueChange={(value) =>
                  setFormData({ ...formData, data_source: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="binance">Binance</SelectItem>
                  <SelectItem value="yfinance">Yahoo Finance</SelectItem>
                  <SelectItem value="synthetic">Synthetic</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Start Backtest
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}


