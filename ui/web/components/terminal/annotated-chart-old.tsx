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
  console.log('📊 AnnotatedChart render:', { 
    dataLength: data?.length || 0, 
    annotationsLength: annotations?.length || 0,
    symbol,
    height 
  })
  
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null)
  const priceLinesRef = useRef<any[]>([])
  const [chartError, setChartError] = useState<string | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  const [debugInfo, setDebugInfo] = useState<string[]>([])
  
  const addDebug = (msg: string) => {
    console.log(`🔍 [Chart Debug] ${msg}`)
    setDebugInfo(prev => [...prev.slice(-9), `${new Date().toLocaleTimeString()}: ${msg}`])
  }

  // Filter annotations by strategy if filter is set
  const filteredAnnotations = strategyFilter
    ? annotations.filter((a) => a.strategy === strategyFilter)
    : annotations

  // Initialize chart - ONLY ONCE
  useEffect(() => {
    addDebug('Init effect started')
    
    if (isInitialized) {
      addDebug('Already initialized, skipping')
      return // Don't re-initialize
    }
    
    if (!chartContainerRef.current) {
      addDebug('Container ref is null')
      return
    }

    const container = chartContainerRef.current
    addDebug(`Container found: ${container ? 'yes' : 'no'}`)
    addDebug(`Container dimensions: ${container.clientWidth}x${container.clientHeight}`)

    // Wait for container to have dimensions
    if (container.clientWidth === 0) {
      addDebug('Container has no width, waiting 100ms...')
      const timer = setTimeout(() => {
        if (container && container.clientWidth > 0) {
          addDebug(`Container now has width: ${container.clientWidth}`)
          setIsInitialized(false) // Retry
        } else {
          addDebug('Container still has no width after wait')
        }
      }, 100)
      return () => clearTimeout(timer)
    }

    try {
      addDebug('Attempting to create chart...')
      console.log('🚀 Creating chart...')
      
      // Check if lightweight-charts is available
      if (typeof createChart === 'undefined') {
        const error = 'createChart is undefined - lightweight-charts not loaded'
        addDebug(error)
        setChartError(error)
        return
      }
      
      addDebug('createChart function available')
      
      // Create chart
      const chart = createChart(container, {
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

      addDebug('Chart object created')
      
      // Check if addSeries exists
      if (typeof chart.addSeries !== 'function') {
        const error = 'chart.addSeries is not a function'
        addDebug(error)
        addDebug(`Chart methods: ${Object.getOwnPropertyNames(chart).filter(m => m.includes('Series') || m.includes('add')).join(', ')}`)
        setChartError(error)
        return
      }
      
      addDebug('addSeries method available')
      
      // Add candlestick series using v5 API
      try {
        const candlestickSeries = chart.addSeries('Candlestick', {
          upColor: "#10b981",
          downColor: "#ef4444",
          borderVisible: false,
          wickUpColor: "#10b981",
          wickDownColor: "#ef4444",
        })
        
        addDebug('Candlestick series created')
        
        if (!candlestickSeries) {
          const error = 'addSeries returned null/undefined'
          addDebug(error)
          setChartError(error)
          return
        }

        seriesRef.current = candlestickSeries
        setIsInitialized(true)
        addDebug('Chart initialization complete')
        console.log('✅ Chart created successfully')
      } catch (seriesError) {
        const error = `Failed to create series: ${seriesError instanceof Error ? seriesError.message : String(seriesError)}`
        addDebug(error)
        setChartError(error)
        console.error('❌ Error creating series:', seriesError)
        return
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
      const errorMsg = error instanceof Error ? error.message : String(error)
      addDebug(`Error caught: ${errorMsg}`)
      addDebug(`Error stack: ${error instanceof Error ? error.stack : 'N/A'}`)
      console.error("❌ Error creating chart:", error)
      setChartError(`Chart error: ${errorMsg}`)
    }
  }, [height, isInitialized])

  // Update data when it changes
  useEffect(() => {
    addDebug(`Data update effect: series=${!!seriesRef.current}, dataLength=${data?.length || 0}`)
    
    if (!seriesRef.current) {
      addDebug('No series ref, cannot update data')
      return
    }
    
    if (!data || data.length === 0) {
      addDebug(`No data to update (length: ${data?.length || 0})`)
      if (data && data.length === 0) {
        console.log('⏳ Waiting for chart data...')
      }
      return
    }

    try {
      addDebug(`Processing ${data.length} candles...`)
      console.log(`📊 Updating chart with ${data.length} candles...`)
      
      // Log first candle for debugging
      if (data.length > 0) {
        addDebug(`First candle: ${JSON.stringify(data[0])}`)
      }
      
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

      addDebug(`Formatted ${formattedData.length} valid candles`)
      
      if (formattedData.length > 0) {
        if (!seriesRef.current || typeof seriesRef.current.setData !== 'function') {
          const error = 'Series ref invalid or setData not available'
          addDebug(error)
          setChartError(error)
          return
        }
        
        addDebug('Calling setData...')
        seriesRef.current.setData(formattedData)
        setChartError(null)
        addDebug('Data set successfully')
        console.log(`✅ Chart updated with ${formattedData.length} valid candles`)
      } else {
        addDebug('No valid candles after filtering')
        console.warn('⚠️ No valid candles after filtering')
        setChartError('No valid chart data available - all candles filtered out')
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error)
      addDebug(`Data update error: ${errorMsg}`)
      console.error("❌ Error updating chart data:", error)
      setChartError(`Data error: ${errorMsg}`)
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
        <div className="p-8 text-center text-muted-foreground flex flex-col items-center justify-center gap-4" style={{ height: `${height}px` }}>
          <div className="max-w-2xl">
            <p className="text-destructive mb-2 font-bold">⚠️ Chart Error</p>
            <p className="text-sm mb-4">{chartError}</p>
            <div className="text-xs space-y-1 text-left bg-gray-900 p-4 rounded border border-gray-800">
              <p><strong>Debug Info:</strong></p>
              <p>Data: {data.length} candles available</p>
              <p>Container: {chartContainerRef.current ? 'Found' : 'Not found'}</p>
              <p>Initialized: {isInitialized ? 'Yes' : 'No'}</p>
              <p>Series: {seriesRef.current ? 'Created' : 'Not created'}</p>
              {data.length > 0 && (
                <div className="mt-2">
                  <p><strong>First candle:</strong></p>
                  <pre className="text-xs overflow-auto">{JSON.stringify(data[0], null, 2)}</pre>
                </div>
              )}
              {debugInfo.length > 0 && (
                <div className="mt-2">
                  <p><strong>Debug log:</strong></p>
                  <div className="max-h-32 overflow-y-auto text-xs">
                    {debugInfo.map((msg, i) => <p key={i}>{msg}</p>)}
                  </div>
                </div>
              )}
            </div>
            <button 
              onClick={() => {
                setChartError(null)
                setIsInitialized(false)
                addDebug('Manual reset triggered')
              }}
              className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Reset Chart
            </button>
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

