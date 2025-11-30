"use client"

// WORKING Chart Component - Simplified and Robust
import { useEffect, useRef, useState } from "react"
import { 
  createChart, 
  ColorType, 
  IChartApi, 
  ISeriesApi, 
  CandlestickData,
} from "lightweight-charts"
import type { OHLCVData, ChartAnnotation } from "@/lib/types"
import { Card } from "@/components/ui/card"

interface AnnotatedChartProps {
  data: OHLCVData[]
  annotations?: ChartAnnotation[]
  symbol?: string
  height?: number
  showAnnotations?: boolean
  strategyFilter?: string | null
}

export function AnnotatedChart({
  data,
  annotations = [],
  symbol = "BTC/USD",
  height = 500,
  showAnnotations = true,
  strategyFilter = null,
}: AnnotatedChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null)
  const priceLinesRef = useRef<any[]>([])
  const [chartError, setChartError] = useState<string | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)

  // Filter annotations by strategy if filter is set
  const filteredAnnotations = strategyFilter
    ? annotations.filter((a) => a.strategy === strategyFilter)
    : annotations

  // Initialize chart - ONLY ONCE
  useEffect(() => {
    if (isInitialized) return // Don't re-initialize
    if (!chartContainerRef.current) {
      console.log('⏳ Chart container not ready')
      return
    }

    // Wait for container to have dimensions
    if (chartContainerRef.current.clientWidth === 0) {
      const timer = setTimeout(() => {
        if (chartContainerRef.current && chartContainerRef.current.clientWidth > 0) {
          setIsInitialized(false) // Retry
        }
      }, 100)
      return () => clearTimeout(timer)
    }

    try {
      console.log('🚀 Creating chart...')
      
      // Create chart
      const chart = createChart(chartContainerRef.current, {
        layout: {
          background: { type: ColorType.Solid, color: "#000000" },
          textColor: "#d1d5db",
          fontSize: 12,
        },
        grid: {
          vertLines: { color: "#1f2937" },
          horzLines: { color: "#1f2937" },
        },
        width: chartContainerRef.current.clientWidth,
        height: height,
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
        },
      })

      chartRef.current = chart

      // Add candlestick series using v5 API
      const candlestickSeries = (chart as any).addSeries('Candlestick', {
        upColor: "#10b981",
        downColor: "#ef4444",
        borderVisible: false,
        wickUpColor: "#10b981",
        wickDownColor: "#ef4444",
      })

      seriesRef.current = candlestickSeries
      setIsInitialized(true)
      console.log('✅ Chart created successfully')

      // Handle resize
      const handleResize = () => {
        if (chartContainerRef.current && chart) {
          chart.applyOptions({ width: chartContainerRef.current.clientWidth })
        }
      }

      window.addEventListener("resize", handleResize)

      return () => {
        window.removeEventListener("resize", handleResize)
        if (chart) {
          chart.remove()
        }
      }
    } catch (error) {
      console.error("❌ Error creating chart:", error)
      setChartError(`Chart error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }, [height, isInitialized])

  // Update data when it changes
  useEffect(() => {
    if (!seriesRef.current || !data || data.length === 0) {
      if (data && data.length === 0) {
        console.log('⏳ Waiting for chart data...')
      }
      return
    }

    try {
      console.log(`📊 Updating chart with ${data.length} candles...`)
      
      const formattedData: CandlestickData[] = data
        .map((d) => {
          // Handle time - convert to Unix timestamp if needed
          let timeValue: number
          if (typeof d.time === 'number') {
            timeValue = d.time
          } else if (typeof d.time === 'string') {
            timeValue = parseInt(d.time)
          } else {
            timeValue = Date.now() / 1000
          }

          return {
            time: timeValue as any,
            open: Number(d.open) || 0,
            high: Number(d.high) || 0,
            low: Number(d.low) || 0,
            close: Number(d.close) || 0,
          }
        })
        .filter(d => d.open > 0 && d.close > 0 && d.high >= d.low)

      if (formattedData.length > 0) {
        seriesRef.current.setData(formattedData)
        setChartError(null)
        console.log(`✅ Chart updated with ${formattedData.length} valid candles`)
      } else {
        console.warn('⚠️ No valid candles after filtering')
        setChartError('No valid chart data available')
      }
    } catch (error) {
      console.error("❌ Error updating chart data:", error)
      setChartError(`Data error: ${error instanceof Error ? error.message : 'Unknown'}`)
    }
  }, [data])

  // Add annotations (markers and price lines)
  useEffect(() => {
    if (!chartRef.current || !seriesRef.current || !showAnnotations || !isInitialized) return

    const series = seriesRef.current

    // Clear existing price lines
    priceLinesRef.current.forEach((line) => {
      try {
        series.removePriceLine(line)
      } catch (e) {
        // Ignore if already removed
      }
    })
    priceLinesRef.current = []

    if (!filteredAnnotations || filteredAnnotations.length === 0) {
      if ('setMarkers' in series) {
        (series as any).setMarkers([])
      }
      return
    }

    // Add markers for entry/exit
    const markers: any[] = filteredAnnotations
      .filter((a) => a.type === "entry" || a.type === "exit")
      .map((a) => ({
        time: Number(a.timestamp),
        position: a.type === "entry" ? 'belowBar' : 'aboveBar',
        color: a.type === "entry" ? "#10b981" : "#ef4444",
        shape: a.type === "entry" ? 'arrowUp' : 'arrowDown',
        text: a.label || a.type.toUpperCase(),
        size: 2,
      }))

    if ('setMarkers' in series && markers.length > 0) {
      try {
        (series as any).setMarkers(markers)
        console.log(`✅ Added ${markers.length} markers`)
      } catch (e) {
        console.error("Error setting markers:", e)
      }
    }

    // Add price lines for TP/SL
    filteredAnnotations.forEach((annotation) => {
      if (annotation.type === "tp" || annotation.type === "sl") {
        try {
          if (typeof (series as any).createPriceLine === 'function') {
            const priceLine = (series as any).createPriceLine({
              price: Number(annotation.price),
              color: annotation.type === "sl" ? "#f59e0b" : "#3b82f6",
              lineWidth: 2,
              lineStyle: annotation.type === "sl" ? 2 : 0, // Dashed for SL
              axisLabelVisible: true,
              title: `${annotation.type.toUpperCase()}: $${Number(annotation.price).toFixed(2)}`,
            })
            if (priceLine) {
              priceLinesRef.current.push(priceLine)
            }
          }
        } catch (e) {
          console.error(`Error creating price line for ${annotation.type}:`, e)
        }
      }
    })

    if (priceLinesRef.current.length > 0) {
      console.log(`✅ Added ${priceLinesRef.current.length} price lines`)
    }
  }, [filteredAnnotations, showAnnotations, isInitialized])

  return (
    <Card className="w-full bg-black border border-gray-800">
      <div className="p-4 border-b border-gray-800 flex items-center justify-between bg-gray-900/50">
        <div className="flex items-center gap-4">
          <h3 className="font-semibold text-white">{symbol}</h3>
          <div className="text-sm text-gray-400">
            {data.length} candles • {filteredAnnotations.length} annotations
          </div>
        </div>
      </div>
      {chartError ? (
        <div className="p-8 text-center text-muted-foreground flex items-center justify-center" style={{ height: `${height}px` }}>
          <div>
            <p className="text-destructive mb-2">⚠️ Chart Error</p>
            <p className="text-sm">{chartError}</p>
            <p className="text-xs mt-2">Data: {data.length} candles available</p>
          </div>
        </div>
      ) : !data || data.length === 0 ? (
        <div className="p-8 text-center text-muted-foreground flex items-center justify-center" style={{ height: `${height}px` }}>
          <div>
            <p className="mb-2">⏳ Loading chart data...</p>
            <p className="text-xs">Waiting for market data from backend</p>
          </div>
        </div>
      ) : (
        <div ref={chartContainerRef} className="w-full" style={{ height: `${height}px` }} />
      )}
    </Card>
  )
}

