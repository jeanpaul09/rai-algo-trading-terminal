"use client"

// BULLETPROOF Chart Component - Dynamic Import + Error Handling
import { useEffect, useRef, useState } from "react"
import dynamic from "next/dynamic"
import type { OHLCVData, ChartAnnotation } from "@/lib/types"
import { Card } from "@/components/ui/card"

// Dynamically import lightweight-charts to avoid SSR issues
const LightweightCharts = dynamic(() => import("lightweight-charts"), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-full">Loading chart library...</div>
})

interface AnnotatedChartProps {
  data: OHLCVData[]
  annotations?: ChartAnnotation[]
  symbol?: string
  height?: number
  showAnnotations?: boolean
  strategyFilter?: string | null
}

function ChartInner({ 
  data, 
  annotations = [], 
  symbol = "BTC/USD", 
  height = 500,
  showAnnotations = true,
  strategyFilter = null 
}: AnnotatedChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<any>(null)
  const seriesRef = useRef<any>(null)
  const priceLinesRef = useRef<any[]>([])
  const [chartError, setChartError] = useState<string | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)

  const filteredAnnotations = strategyFilter
    ? annotations.filter((a) => a.strategy === strategyFilter)
    : annotations

  // Initialize chart
  useEffect(() => {
    if (isInitialized) return
    if (!chartContainerRef.current) return

    const container = chartContainerRef.current
    if (container.clientWidth === 0) {
      const timer = setTimeout(() => {
        if (container.clientWidth > 0) {
          setIsInitialized(false)
        }
      }, 100)
      return () => clearTimeout(timer)
    }

    let mounted = true

    async function initChart() {
      try {
        console.log('🚀 Initializing chart...')
        
        // Dynamic import
        const { createChart, ColorType } = await import("lightweight-charts")
        
        if (!mounted || !container) return
        
        const chart = createChart(container, {
          layout: {
            background: { type: ColorType.Solid, color: "#000000" },
            textColor: "#d1d5db",
          },
          grid: {
            vertLines: { color: "#1f2937" },
            horzLines: { color: "#1f2937" },
          },
          width: container.clientWidth,
          height: height,
        })

        if (!mounted) {
          chart.remove()
          return
        }

        chartRef.current = chart

        const candlestickSeries = chart.addSeries('Candlestick', {
          upColor: "#10b981",
          downColor: "#ef4444",
          borderVisible: false,
          wickUpColor: "#10b981",
          wickDownColor: "#ef4444",
        })

        seriesRef.current = candlestickSeries
        setIsInitialized(true)
        console.log('✅ Chart initialized')

        const handleResize = () => {
          if (container && chart) {
            chart.applyOptions({ width: container.clientWidth })
          }
        }

        window.addEventListener("resize", handleResize)

        return () => {
          window.removeEventListener("resize", handleResize)
          if (chart) {
            try {
              chart.remove()
            } catch (e) {
              console.warn('Error removing chart:', e)
            }
          }
        }
      } catch (error) {
        console.error("❌ Chart init error:", error)
        setChartError(`Chart error: ${error instanceof Error ? error.message : 'Unknown'}`)
      }
    }

    initChart()

    return () => {
      mounted = false
      if (chartRef.current) {
        try {
          chartRef.current.remove()
        } catch (e) {
          // Ignore
        }
      }
    }
  }, [height, isInitialized])

  // Update data
  useEffect(() => {
    if (!seriesRef.current || !data || data.length === 0) return

    try {
      const formattedData = data
        .map((d) => {
          let timeValue: number
          if (typeof d.time === 'number') {
            timeValue = d.time
          } else if (typeof d.time === 'string') {
            timeValue = parseInt(d.time)
          } else {
            timeValue = Math.floor(Date.now() / 1000)
          }

          return {
            time: timeValue,
            open: Number(d.open) || 0,
            high: Number(d.high) || 0,
            low: Number(d.low) || 0,
            close: Number(d.close) || 0,
          }
        })
        .filter(d => d.open > 0 && d.close > 0 && d.high >= d.low)

      if (formattedData.length > 0 && seriesRef.current) {
        seriesRef.current.setData(formattedData)
        setChartError(null)
        console.log(`✅ Updated chart with ${formattedData.length} candles`)
      }
    } catch (error) {
      console.error("❌ Data update error:", error)
      setChartError(`Data error: ${error instanceof Error ? error.message : 'Unknown'}`)
    }
  }, [data])

  // Update annotations
  useEffect(() => {
    if (!seriesRef.current || !showAnnotations || !isInitialized) return

    const series = seriesRef.current

    // Clear price lines
    priceLinesRef.current.forEach((line) => {
      try {
        series.removePriceLine(line)
      } catch (e) {
        // Ignore
      }
    })
    priceLinesRef.current = []

    // Add markers
    if (filteredAnnotations.length > 0) {
      const markers = filteredAnnotations
        .filter((a) => a.type === "entry" || a.type === "exit")
        .map((a) => ({
          time: Number(a.timestamp),
          position: a.type === "entry" ? 'belowBar' as const : 'aboveBar' as const,
          color: a.type === "entry" ? "#10b981" : "#ef4444",
          shape: a.type === "entry" ? 'arrowUp' as const : 'arrowDown' as const,
          text: a.label || a.type.toUpperCase(),
        }))

      if (markers.length > 0 && 'setMarkers' in series) {
        try {
          (series as any).setMarkers(markers)
        } catch (e) {
          console.error("Marker error:", e)
        }
      }

      // Add price lines
      filteredAnnotations.forEach((annotation) => {
        if ((annotation.type === "tp" || annotation.type === "sl") && 'createPriceLine' in series) {
          try {
            const priceLine = (series as any).createPriceLine({
              price: Number(annotation.price),
              color: annotation.type === "sl" ? "#f59e0b" : "#3b82f6",
              lineWidth: 2,
              lineStyle: annotation.type === "sl" ? 2 : 0,
              axisLabelVisible: true,
              title: `${annotation.type.toUpperCase()}: $${Number(annotation.price).toFixed(2)}`,
            })
            if (priceLine) {
              priceLinesRef.current.push(priceLine)
            }
          } catch (e) {
            console.error(`Price line error for ${annotation.type}:`, e)
          }
        }
      })
    }
  }, [filteredAnnotations, showAnnotations, isInitialized])

  return (
    <>
      {chartError && (
        <div className="absolute top-2 left-2 right-2 p-2 bg-red-900/50 border border-red-500 rounded text-xs text-red-200 z-10">
          Error: {chartError}
        </div>
      )}
      <div ref={chartContainerRef} className="w-full" style={{ height: `${height}px` }} />
    </>
  )
}

export function AnnotatedChart(props: AnnotatedChartProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <Card className="w-full bg-black border border-gray-800">
        <div className="p-4 border-b border-gray-800 bg-gray-900/50">
          <h3 className="font-semibold text-white">{props.symbol}</h3>
        </div>
        <div className="flex items-center justify-center" style={{ height: `${props.height || 500}px` }}>
          <div className="text-muted-foreground">Loading chart...</div>
        </div>
      </Card>
    )
  }

  return (
    <Card className="w-full bg-black border border-gray-800 relative">
      <div className="p-4 border-b border-gray-800 flex items-center justify-between bg-gray-900/50">
        <div className="flex items-center gap-4">
          <h3 className="font-semibold text-white">{props.symbol}</h3>
          <div className="text-sm text-gray-400">
            {props.data.length} candles • {props.annotations?.length || 0} annotations
          </div>
        </div>
      </div>
      {!props.data || props.data.length === 0 ? (
        <div className="p-8 text-center text-muted-foreground flex items-center justify-center" style={{ height: `${props.height || 500}px` }}>
          <div>
            <p className="mb-2">⏳ Loading chart data...</p>
            <p className="text-xs">Waiting for market data from backend</p>
          </div>
        </div>
      ) : (
        <ChartInner {...props} />
      )}
    </Card>
  )
}

