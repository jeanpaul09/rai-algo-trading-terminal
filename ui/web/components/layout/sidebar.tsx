"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Activity, FlaskConical, LineChart, Radio, Terminal } from "lucide-react"
import { cn } from "@/lib/utils"

const navigation = [
  { name: "Dashboard", href: "/", icon: Activity },
  { name: "Terminal", href: "/terminal", icon: Terminal },
  { name: "Strategies", href: "/strategies", icon: FlaskConical },
  { name: "Experiments", href: "/experiments", icon: LineChart },
  { name: "Live", href: "/live", icon: Radio },
  { name: "Liquidations", href: "/liquidations", icon: Activity },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-screen w-64 flex-col border-r border-border bg-card">
      <div className="flex h-16 items-center border-b border-border px-6">
        <h1 className="text-xl font-bold">RAI-ALGO</h1>
        <span className="ml-2 text-xs text-muted-foreground">QUANT LAB</span>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}

