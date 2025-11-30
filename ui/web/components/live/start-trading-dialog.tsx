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
import { RadioGroup, Radio } from "@/components/ui/radio"
import { Play, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface StartTradingDialogProps {
  strategyName?: string
  onComplete?: () => void
}

export function StartTradingDialog({ strategyName, onComplete }: StartTradingDialogProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()
  
  const [formData, setFormData] = useState({
    strategy_name: strategyName || "",
    symbol: "BTC/USD",
    exchange: "binance",
    dry_run: "true",
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${API_BASE_URL}/api/live/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          dry_run: formData.dry_run === "true",
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to start trading")
      }

      const data = await response.json()
      
      toast({
        title: "Trading Started",
        description: `Trader ID: ${data.trader_id}`,
      })

      setOpen(false)
      if (onComplete) {
        onComplete()
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to start trading",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="default">
          <Play className="h-4 w-4 mr-2" />
          Start Live Trading
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Start Live Trading</DialogTitle>
          <DialogDescription>
            Deploy this strategy for live trading
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="strategy_name">Strategy</Label>
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
            <Label htmlFor="symbol">Symbol</Label>
            <Input
              id="symbol"
              value={formData.symbol}
              onChange={(e) =>
                setFormData({ ...formData, symbol: e.target.value })
              }
              placeholder="BTC/USD"
              required
            />
          </div>
          <div>
            <Label>Mode</Label>
            <RadioGroup
              value={formData.dry_run}
              onValueChange={(value) =>
                setFormData({ ...formData, dry_run: value })
              }
            >
              <div className="flex items-center space-x-2">
                <Radio value="true" id="dry-run" />
                <Label htmlFor="dry-run">Dry Run (Test Mode)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Radio value="false" id="live" />
                <Label htmlFor="live">Live Trading</Label>
              </div>
            </RadioGroup>
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
                  Start
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

