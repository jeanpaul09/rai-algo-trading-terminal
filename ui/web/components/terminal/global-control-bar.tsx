"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { AlertTriangle, Power, PowerOff, Activity, Wifi, WifiOff } from "lucide-react"
import type { AgentStatus, WalletInfo } from "@/lib/types"
import { Card } from "@/components/ui/card"

interface GlobalControlBarProps {
  agentStatus: AgentStatus
  walletInfo?: WalletInfo
  onModeChange: (mode: "OFF" | "DEMO" | "LIVE") => void
  onEmergencyStop: () => void
  onToggleAgent: () => void
}

export function GlobalControlBar({
  agentStatus,
  walletInfo,
  onModeChange,
  onEmergencyStop,
  onToggleAgent,
}: GlobalControlBarProps) {
  const getModeColor = (mode: string) => {
    switch (mode) {
      case "LIVE":
        return "bg-red-500/20 text-red-500 border-red-500/50"
      case "DEMO":
        return "bg-yellow-500/20 text-yellow-500 border-yellow-500/50"
      case "OFF":
        return "bg-gray-500/20 text-gray-500 border-gray-500/50"
      default:
        return "bg-gray-500/20 text-gray-500 border-gray-500/50"
    }
  }

  return (
    <Card className="border-b rounded-none border-x-0 border-t-0">
      <div className="p-4 flex items-center justify-between">
        {/* Left: Agent Status */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <Button
              variant={agentStatus.isActive ? "default" : "outline"}
              size="sm"
              onClick={onToggleAgent}
              className="gap-2"
            >
              {agentStatus.isActive ? (
                <>
                  <Power className="h-4 w-4" />
                  ON
                </>
              ) : (
                <>
                  <PowerOff className="h-4 w-4" />
                  OFF
                </>
              )}
            </Button>

            <Select
              value={agentStatus.mode}
              onValueChange={(value) => onModeChange(value as "OFF" | "DEMO" | "LIVE")}
            >
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="OFF">OFF</SelectItem>
                <SelectItem value="DEMO">DEMO</SelectItem>
                <SelectItem value="LIVE">LIVE</SelectItem>
              </SelectContent>
            </Select>

            <Badge className={getModeColor(agentStatus.mode)} variant="outline">
              {agentStatus.mode}
            </Badge>
          </div>

          {/* Connection Status */}
          <div className="flex items-center gap-2 text-sm">
            {agentStatus.connected ? (
              <>
                <Wifi className="h-4 w-4 text-green-500" />
                <span className="text-muted-foreground">Connected</span>
              </>
            ) : (
              <>
                <WifiOff className="h-4 w-4 text-red-500" />
                <span className="text-muted-foreground">Disconnected</span>
              </>
            )}
          </div>

          {/* Environment */}
          <div className="text-sm">
            <span className="text-muted-foreground">Env:</span>
            <Badge
              variant="outline"
              className={
                agentStatus.environment === "mainnet"
                  ? "ml-2 border-red-500/50 text-red-500"
                  : "ml-2 border-yellow-500/50 text-yellow-500"
              }
            >
              {agentStatus.environment.toUpperCase()}
            </Badge>
          </div>
        </div>

        {/* Center: Wallet Info */}
        {walletInfo && (
          <div className="flex items-center gap-6 text-sm">
            <div>
              <span className="text-muted-foreground">Balance:</span>
              <span className="ml-2 font-semibold">
                ${walletInfo.balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Margin:</span>
              <span className="ml-2 font-semibold">
                ${walletInfo.marginUsed.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                {" / "}
                <span className="text-muted-foreground">
                  ${walletInfo.marginAvailable.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">PnL:</span>
              <span
                className={`ml-2 font-semibold ${
                  walletInfo.unrealizedPnL >= 0 ? "text-green-500" : "text-red-500"
                }`}
              >
                {walletInfo.unrealizedPnL >= 0 ? "+" : ""}
                ${walletInfo.unrealizedPnL.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
          </div>
        )}

        {/* Right: Emergency Controls */}
        <div className="flex items-center gap-3">
          {agentStatus.mode === "LIVE" && (
            <Button
              variant="destructive"
              size="sm"
              onClick={onEmergencyStop}
              className="gap-2"
            >
              <AlertTriangle className="h-4 w-4" />
              EMERGENCY STOP
            </Button>
          )}
          <div className="text-xs text-muted-foreground">
            Last update: {new Date(agentStatus.lastUpdate).toLocaleTimeString()}
          </div>
        </div>
      </div>
    </Card>
  )
}

