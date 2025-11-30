"use client"

// Chart component using lightweight-charts v5.0.9
// CRITICAL: v5 uses addSeries('Candlestick', ...) NOT addCandlestickSeries

import { useEffect, useRef, useState } from "react"
import { 
  createChart, 
  ColorType, 
  IChartApi, 
  ISeriesApi, 
  CandlestickData,
  SeriesMarker
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

  // Filter annotations by strategy if filter is set
  const filteredAnnotations = strategyFilter
    ? annotations.filter((a) => a.strategy === strategyFilter)
    : annotations

  useEffect(() => {
    if (!chartContainerRef.current) return
    
    // Don't initialize chart if no data
    if (!data || data.length === 0) {
      console.log('⏳ Waiting for chart data...')
      setChartError(null) // Clear error, just waiting for data
      return
    }

    // CRITICAL: Prevent any use of addCandlestickSeries (v4 API)
    // This check ensures we fail gracefully if somehow old code is loaded
    if (typeof (window as any).__OLD_CHART_API_LOADED !== 'undefined') {
      console.warn('⚠️ Old chart API detected - using fallback')
      setChartError('Chart library version mismatch - please refresh the page')
      return
    }

    try {
      // Create chart with premium styling
      const chart = createChart(chartContainerRef.current, {
        layout: {
          background: { type: ColorType.Solid, color: "#000000" },
          textColor: "#d1d5db",
          fontSize: 12,
        },
        grid: {
          vertLines: { 
            color: "#1f2937",
            style: 0, // Solid
          },
          horzLines: { 
            color: "#1f2937",
            style: 0, // Solid
          },
        },
        width: chartContainerRef.current.clientWidth,
        height: height,
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
          borderColor: "#374151",
          rightOffset: 12,
        },
        rightPriceScale: {
          borderColor: "#374151",
          scaleMargins: {
            top: 0.1,
            bottom: 0.1,
          },
        },
        crosshair: {
          mode: 0, // Normal
          vertLine: {
            color: "#6b7280",
            width: 1,
            style: 3, // Dashed
          },
          horzLine: {
            color: "#6b7280",
            width: 1,
            style: 3, // Dashed
          },
        },
      })

    chartRef.current = chart

      // Add candlestick series - lightweight-charts v5.0.9 API
      // CRITICAL: v5.0.9 ONLY supports addSeries('Candlestick', options)
      // addCandlestickSeries DOES NOT EXIST in v5 - removed in breaking change
      
      // Defensive check: If addCandlestickSeries exists, we have wrong version
      if (typeof (chart as any).addCandlestickSeries === 'function') {
        console.error('❌ OLD API DETECTED: addCandlestickSeries exists (v4 API)')
        console.error('This build is using the wrong chart library version!')
        setChartError('Chart library version mismatch - cached build detected. Please wait for Vercel to rebuild or hard refresh (Cmd+Shift+R)')
        return
      }

      let candlestickSeries
      try {
        // v5 API: MUST use addSeries('Candlestick', {...})
        const addSeriesFn = (chart as any).addSeries
        if (typeof addSeriesFn === 'function') {
          console.log('✅ Using addSeries (v5.0.9 API) - correct method')
          candlestickSeries = addSeriesFn.call(chart, 'Candlestick', {
            upColor: "#10b981", // Green for bullish
            downColor: "#ef4444", // Red for bearish
            borderVisible: false,
            wickUpColor: "#10b981",
            wickDownColor: "#ef4444",
            priceFormat: {
              type: 'price',
              precision: 2,
              minMove: 0.01,
            },
          })
        } else {
          // If addSeries doesn't exist, log error and show fallback
          const availableMethods = Object.getOwnPropertyNames(chart).filter(m => 
            m.toLowerCase().includes('add') || m.toLowerCase().includes('series')
          )
          console.error('❌ addSeries not found on chart object')
          console.error('Available methods:', availableMethods)
          setChartError('Chart API not available - addSeries method not found')
          return
        }
      } catch (error) {
        console.error('❌ Error creating candlestick series:', error)
        setChartError(`Chart error: ${error instanceof Error ? error.message : 'Unknown error'}`)
        return
      }

      if (!candlestickSeries) {
        console.error('❌ Failed to create candlestick series - method returned undefined')
        setChartError('Failed to create chart series')
        return
      }

      console.log('✅ Candlestick series created successfully')
      seriesRef.current = candlestickSeries

      // Convert data format - only if we have data
      if (data && data.length > 0) {
        const formattedData: CandlestickData[] = data.map((d) => ({
          time: d.time as any,
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
        }))

        candlestickSeries.setData(formattedData)
        console.log(`✅ Chart initialized with ${formattedData.length} candles`)
      } else {
        console.warn('⚠️ Chart created but no data to display yet')
      }

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
      const errorMsg = error instanceof Error ? error.message : 'Unknown error'
      console.error("Error details:", error)
      setChartError(`Chart initialization failed: ${errorMsg}`)
    }
  }, [data, height]) // Re-run when data or height changes

  // Update data when it changes
  useEffect(() => {
    if (!seriesRef.current || !data.length) return

    try {
      const formattedData: CandlestickData[] = data.map((d) => ({
      time: d.time as any,
      open: d.open,
      high: d.high,
      low: d.low,
        close: d.close,
      }))

      seriesRef.current.setData(formattedData)
    } catch (error) {
      console.error("Error updating chart data:", error)
    }
  }, [data])

  // Add annotations - markers and price lines
  useEffect(() => {
    if (!chartRef.current || !seriesRef.current || !showAnnotations) return

    const chart = chartRef.current
    const series = seriesRef.current

    // Clear existing price lines
    if (priceLinesRef.current.length > 0) {
      priceLinesRef.current.forEach((line) => {
        try {
          series.removePriceLine(line)
        } catch (e) {
          // Ignore if already removed
        }
      })
      priceLinesRef.current = []
    }

    // Don't render if no annotations
    if (!filteredAnnotations || filteredAnnotations.length === 0) {
      // Clear markers
      if ('setMarkers' in series) {
        (series as any).setMarkers([])
      }
      return
    }

    // Create markers for entry/exit points
    const markers: SeriesMarker<number>[] = filteredAnnotations
      .filter((annotation) => annotation.type === "entry" || annotation.type === "exit")
      .map((annotation) => {
        const color = annotation.color || getAnnotationColor(annotation.type)
        const shape = getAnnotationShape(annotation.type)
        const position = getAnnotationPosition(annotation.type)

        return {
          time: annotation.timestamp as number,
          position: position as 'aboveBar' | 'belowBar' | 'inBar',
          color: color,
          shape: shape as 'circle' | 'square' | 'arrowUp' | 'arrowDown',
          text: annotation.label || annotation.reason || annotation.type.toUpperCase(),
          size: 2,
        }
      })

    // Set markers on the series
    if ('setMarkers' in series && markers.length > 0) {
      try {
        (series as any).setMarkers(markers)
        console.log(`✅ Added ${markers.length} markers to chart`)
      } catch (error) {
        console.error("Error setting markers:", error)
      }
    }

    // Add price lines for TP/SL/target levels
    filteredAnnotations.forEach((annotation) => {
      if (annotation.type === "tp" || annotation.type === "sl" || annotation.type === "target") {
        const color = annotation.color || getAnnotationColor(annotation.type)
        const lineStyle = annotation.type === "sl" ? 2 : 0 // Dashed for SL, solid for TP
        
        try {
          // Create price line - in v5, price lines are added to the series
          const priceLine = series.createPriceLine({
            price: annotation.price,
            color: color,
            lineWidth: annotation.type === "sl" ? 2 : 2,
            lineStyle: lineStyle, // 0 = solid, 2 = dashed
            axisLabelVisible: true,
            title: annotation.label || `${annotation.type.toUpperCase()}: $${annotation.price.toFixed(2)}`,
          })
          priceLinesRef.current.push(priceLine)
        } catch (error) {
          console.error(`Error creating price line for ${annotation.type}:`, error)
        }
      } else if (annotation.type === "region" && annotation.priceEnd) {
        // For regions, add two price lines
        const color = annotation.color || getAnnotationColor(annotation.type)
        try {
          const line1 = series.createPriceLine({
            price: annotation.price,
            color: color + "80", // Semi-transparent
            lineWidth: 1,
            lineStyle: 2, // Dashed
            axisLabelVisible: true,
            title: annotation.label || "Region Start",
          })
          const line2 = series.createPriceLine({
            price: annotation.priceEnd,
            color: color + "80",
            lineWidth: 1,
            lineStyle: 2,
            axisLabelVisible: true,
            title: "Region End",
          })
          priceLinesRef.current.push(line1, line2)
        } catch (error) {
          console.error("Error creating region lines:", error)
        }
      }
    })

    if (priceLinesRef.current.length > 0) {
      console.log(`✅ Added ${priceLinesRef.current.length} price lines to chart`)
    }

    // Cleanup function
    return () => {
      // Cleanup is handled at the start of the effect
    }
  }, [filteredAnnotations, showAnnotations])

  return (
    <Card className="w-full bg-black border border-gray-800">
      <div className="p-4 border-b border-gray-800 flex items-center justify-between bg-gray-900/50">
        <div className="flex items-center gap-4">
          <h3 className="font-semibold text-white">{symbol}</h3>
          <div className="text-sm text-gray-400">
            {data.length} candles • {filteredAnnotations.length} annotations
          </div>
          {filteredAnnotations.length > 0 && (
            <div className="flex items-center gap-2 text-xs">
              {filteredAnnotations.some(a => a.type === "entry") && (
                <span className="px-2 py-0.5 rounded bg-green-500/20 text-green-400">Entry</span>
              )}
              {filteredAnnotations.some(a => a.type === "tp") && (
                <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">TP</span>
              )}
              {filteredAnnotations.some(a => a.type === "sl") && (
                <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400">SL</span>
              )}
            </div>
          )}
        </div>
        {strategyFilter && (
          <div className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">
            Filtered: {strategyFilter}
          </div>
        )}
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

function getAnnotationColor(type: string): string {
  switch (type) {
    case "entry":
      return "#10b981" // Green
    case "exit":
      return "#ef4444" // Red
    case "tp":
      return "#3b82f6" // Blue
    case "sl":
      return "#f59e0b" // Amber
    case "target":
      return "#8b5cf6" // Purple
    case "region":
      return "#6366f1" // Indigo
    default:
      return "#9ca3af" // Gray
  }
}

function getAnnotationShape(type: string): "circle" | "square" | "arrowUp" | "arrowDown" {
  switch (type) {
    case "entry":
      return "arrowUp"
    case "exit":
      return "arrowDown"
    case "tp":
      return "circle"
    case "sl":
      return "square"
    default:
      return "circle"
  }
}

function getAnnotationPosition(type: string): "aboveBar" | "belowBar" | "inBar" {
  switch (type) {
    case "entry":
      return "belowBar"
    case "exit":
      return "aboveBar"
    case "tp":
    case "sl":
      return "inBar"
    default:
      return "inBar"
  }
}

