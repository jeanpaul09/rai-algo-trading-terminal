"use client"

// BULLETPROOF Chart - Fixed Line by Line
import { useEffect, useRef, useState } from "react"
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
  const chartRef = useRef<any>(null)
  const seriesRef = useRef<any>(null)
  const priceLinesRef = useRef<any[]>([])
  const [chartError, setChartError] = useState<string | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  const [libraryLoaded, setLibraryLoaded] = useState(false)
  const initAttemptedRef = useRef(false) // Track if we've attempted initialization

  const filteredAnnotations = strategyFilter
    ? annotations.filter((a) => a.strategy === strategyFilter)
    : annotations

  // Load lightweight-charts library dynamically - RUNS FIRST
  useEffect(() => {
    if (libraryLoaded) return

    async function loadLibrary() {
      try {
        const lwc = await import("lightweight-charts")
        if (typeof window !== 'undefined') {
          (window as any).LightweightCharts = lwc
        }
        setLibraryLoaded(true)
        console.log('✅ Lightweight-charts library loaded')
      } catch (error) {
        console.error('❌ Failed to load lightweight-charts:', error)
        setChartError(`Failed to load chart library: ${error instanceof Error ? error.message : 'Unknown error'}`)
      }
    }

    loadLibrary()
  }, [libraryLoaded])

  // Initialize chart - ONLY RUNS ONCE when library is loaded
  useEffect(() => {
    // Don't initialize if library isn't loaded
    if (!libraryLoaded) {
      console.log('⏳ Waiting for library to load...')
      return
    }

    // Don't initialize if already initialized
    if (isInitialized) {
      console.log('✅ Chart already initialized')
      return
    }

    // Don't initialize if container ref doesn't exist
    if (!chartContainerRef.current) {
      console.log('⏳ Waiting for container ref...')
      return
    }

    const container = chartContainerRef.current

    // Check dimensions
    const containerWidth = container.clientWidth
    const containerHeight = container.clientHeight || height || 500
    
    console.log(`Container check: ${containerWidth}x${containerHeight}`)

    // If width is 0, wait a bit and retry (but only once)
    if (containerWidth === 0 && !initAttemptedRef.current) {
      console.log('⚠️ Container has zero width, waiting 200ms...')
      const timeout = setTimeout(() => {
        if (chartContainerRef.current && chartContainerRef.current.clientWidth > 0) {
          console.log(`✅ Container now has width: ${chartContainerRef.current.clientWidth}`)
          initAttemptedRef.current = false // Reset to allow retry
        } else {
          console.error('❌ Container still has zero width after wait')
          setChartError('Chart container has no width - check CSS/layout')
        }
      }, 200)
      return () => clearTimeout(timeout)
    }

    // Prevent double initialization
    if (initAttemptedRef.current) {
      console.log('⏳ Initialization already attempted, skipping...')
      return
    }

    initAttemptedRef.current = true

    async function initChart() {
      try {
        console.log('🚀 Starting chart initialization...')
        
        const { createChart, ColorType } = await import("lightweight-charts")
        
        // Get final dimensions
        const finalWidth = container.clientWidth || 800
        const finalHeight = height || 500

        if (finalWidth <= 0 || finalHeight <= 0) {
          throw new Error(`Invalid dimensions: ${finalWidth}x${finalHeight}`)
        }

        console.log(`Creating chart with dimensions: ${finalWidth}x${finalHeight}`)
        
        // Create chart with minimal options first to avoid assertion errors
        const chart = createChart(container, {
          layout: {
            background: { type: ColorType.Solid, color: "#000000" },
            textColor: "#d1d5db",
            fontSize: 12,
          },
          grid: {
            vertLines: { color: "#1f2937", visible: true },
            horzLines: { color: "#1f2937", visible: true },
          },
          width: finalWidth,
          height: finalHeight,
          timeScale: {
            timeVisible: true,
            secondsVisible: false,
          },
          rightPriceScale: {
            visible: true,
          },
        })

        chartRef.current = chart
        console.log('✅ Chart object created')

        // Add candlestick series - this is where assertion errors happen
        let candlestickSeries
        try {
          console.log('Adding candlestick series...')
          candlestickSeries = chart.addSeries('Candlestick', {
            upColor: "#10b981",
            downColor: "#ef4444",
            borderVisible: false,
            wickUpColor: "#10b981",
            wickDownColor: "#ef4444",
          })
          
          if (!candlestickSeries) {
            throw new Error('addSeries returned null/undefined')
          }
          
          console.log('✅ Candlestick series created')
        } catch (seriesError: any) {
          console.error('❌ Error creating series:', seriesError)
          // Try with absolutely minimal options
          try {
            console.log('Retrying with minimal options...')
            candlestickSeries = chart.addSeries('Candlestick', {})
            if (!candlestickSeries) {
              throw new Error('Minimal addSeries also returned null')
            }
            console.log('✅ Series created with minimal options')
          } catch (retryError: any) {
            console.error('❌ Retry failed:', retryError)
            throw new Error(`Cannot create chart series: ${retryError?.message || String(retryError)}`)
          }
        }

        seriesRef.current = candlestickSeries
        setIsInitialized(true)
        setChartError(null)
        console.log('✅ Chart fully initialized and ready for data')

        // Handle resize
        const handleResize = () => {
          if (container && chartRef.current) {
            try {
              chartRef.current.applyOptions({ width: container.clientWidth })
            } catch (e) {
              console.warn('Resize error:', e)
            }
          }
        }

        window.addEventListener("resize", handleResize)

        return () => {
          window.removeEventListener("resize", handleResize)
          try {
            if (chartRef.current) {
              chartRef.current.remove()
            }
          } catch (e) {
            console.warn('Cleanup error:', e)
          }
        }
      } catch (error) {
        console.error("❌ Chart initialization error:", error)
        const errorMsg = error instanceof Error ? error.message : String(error)
        setChartError(`Chart initialization failed: ${errorMsg}`)
        initAttemptedRef.current = false // Allow retry
      }
    }

    initChart()

    // Cleanup function
    return () => {
      if (chartRef.current) {
        try {
          chartRef.current.remove()
        } catch (e) {
          // Ignore cleanup errors
        }
        chartRef.current = null
        seriesRef.current = null
      }
    }
  }, [libraryLoaded, isInitialized, height]) // Only depend on libraryLoaded, isInitialized, height

  // Update data when it changes - RUNS WHEN DATA CHANGES
  useEffect(() => {
    // Can't update if series isn't ready
    if (!seriesRef.current) {
      if (data.length > 0) {
        console.log('⏳ Waiting for chart series to be ready before setting data...')
      }
      return
    }

    // Can't update if no data
    if (!data || data.length === 0) {
      return
    }

    try {
      console.log(`📊 Updating chart with ${data.length} candles`)
      
      // Format data for lightweight-charts
      const formattedData = data
        .map((d, index) => {
          // Convert time to Unix timestamp (seconds)
          let timeValue: number
          if (typeof d.time === 'number') {
            timeValue = d.time
          } else if (typeof d.time === 'string') {
            const parsed = parseInt(d.time)
            timeValue = isNaN(parsed) ? Math.floor(Date.now() / 1000) - (data.length - index) * 3600 : parsed
          } else {
            timeValue = Math.floor(Date.now() / 1000) - (data.length - index) * 3600
          }

          // Validate OHLC
          const open = Number(d.open)
          const high = Number(d.high)
          const low = Number(d.low)
          const close = Number(d.close)

          // Skip invalid candles
          if (!open || !high || !low || !close || isNaN(open) || isNaN(high) || isNaN(low) || isNaN(close)) {
            return null
          }

          // Ensure valid OHLC relationships
          if (high < low || open <= 0 || close <= 0) {
            return null
          }

          return {
            time: timeValue as any,
            open: open,
            high: Math.max(high, open, close, low),
            low: Math.min(low, open, close, high),
            close: close,
          }
        })
        .filter((d): d is { time: number; open: number; high: number; low: number; close: number } => d !== null)

      if (formattedData.length === 0) {
        console.error('❌ No valid candles after formatting!')
        setChartError('All candles were invalid - check data format')
        return
      }

      console.log(`✅ Setting ${formattedData.length} valid candles`)
      console.log('First candle:', formattedData[0])
      console.log('Last candle:', formattedData[formattedData.length - 1])
      
      // Set data
      seriesRef.current.setData(formattedData)
      setChartError(null)
      console.log('✅ Data set on chart')
      
      // Fit content to show candles - CRITICAL
      requestAnimationFrame(() => {
        try {
          if (chartRef.current?.timeScale) {
            const timeScale = chartRef.current.timeScale()
            if (timeScale && typeof timeScale.fitContent === 'function') {
              timeScale.fitContent()
              console.log('✅ Chart fitted to content - candles should be visible')
            }
          }
        } catch (e) {
          console.error('❌ Error fitting content:', e)
        }
      })
    } catch (error) {
      console.error("❌ Error updating chart data:", error)
      setChartError(`Data update failed: ${error instanceof Error ? error.message : String(error)}`)
    }
  }, [data]) // Only depend on data

  // Add annotations - RUNS WHEN ANNOTATIONS CHANGE
  useEffect(() => {
    if (!seriesRef.current || !showAnnotations || !isInitialized) return

    const series = seriesRef.current

    // Clear existing price lines
    priceLinesRef.current.forEach((line) => {
      try {
        if (series.removePriceLine) {
          series.removePriceLine(line)
        }
      } catch (e) {
        // Ignore
      }
    })
    priceLinesRef.current = []

    if (!filteredAnnotations || filteredAnnotations.length === 0) {
      if (series.setMarkers) {
        try {
          series.setMarkers([])
        } catch (e) {
          // Ignore
        }
      }
      return
    }

    // Add markers
    try {
      const markers = filteredAnnotations
        .filter((a) => a.type === "entry" || a.type === "exit")
        .map((a) => ({
          time: Number(a.timestamp),
          position: (a.type === "entry" ? 'belowBar' : 'aboveBar') as 'aboveBar' | 'belowBar',
          color: a.type === "entry" ? "#10b981" : "#ef4444",
          shape: (a.type === "entry" ? 'arrowUp' : 'arrowDown') as 'arrowUp' | 'arrowDown',
          text: a.label || a.type.toUpperCase(),
        }))

      if (markers.length > 0 && series.setMarkers) {
        series.setMarkers(markers)
        console.log(`✅ Added ${markers.length} markers`)
      }
    } catch (e) {
      console.error("Error setting markers:", e)
    }

    // Add price lines
    filteredAnnotations.forEach((annotation) => {
      if (annotation.type === "tp" || annotation.type === "sl") {
        try {
          if (series.createPriceLine && typeof series.createPriceLine === 'function') {
            const priceLine = series.createPriceLine({
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

  // Render
  return (
    <Card className="w-full bg-black border border-gray-800">
      <div className="p-4 border-b border-gray-800 flex items-center justify-between bg-gray-900/50">
        <div className="flex items-center gap-4">
          <h3 className="font-semibold text-white">{symbol}</h3>
          <div className="text-sm text-gray-400">
            {data.length} candles • {filteredAnnotations.length} annotations
          </div>
          {chartError && (
            <div className="text-xs text-red-400 bg-red-900/30 px-2 py-1 rounded">
              Error
            </div>
          )}
        </div>
      </div>
      {chartError ? (
        <div className="p-8 text-center flex flex-col items-center justify-center gap-4" style={{ height: `${height}px` }}>
          <div className="text-destructive font-bold">⚠️ Chart Error</div>
          <div className="text-sm text-muted-foreground max-w-md font-mono text-left">{chartError}</div>
          <div className="text-xs text-muted-foreground space-y-1">
            <p>Data: {data.length} candles</p>
            <p>Library: {libraryLoaded ? '✅' : '❌'}</p>
            <p>Initialized: {isInitialized ? '✅' : '❌'}</p>
            <p>Series: {seriesRef.current ? '✅' : '❌'}</p>
            <p>Container: {chartContainerRef.current ? '✅' : '❌'}</p>
            {chartContainerRef.current && (
              <p>Dimensions: {chartContainerRef.current.clientWidth}x{chartContainerRef.current.clientHeight}</p>
            )}
          </div>
          <button
            onClick={() => {
              setChartError(null)
              setIsInitialized(false)
              setLibraryLoaded(false)
              initAttemptedRef.current = false
            }}
            className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
          >
            Retry
          </button>
        </div>
      ) : !libraryLoaded ? (
        <div className="p-8 text-center text-muted-foreground flex items-center justify-center" style={{ height: `${height}px` }}>
          <div>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
            <p>Loading chart library...</p>
          </div>
        </div>
      ) : !data || data.length === 0 ? (
        <div className="p-8 text-center text-muted-foreground flex items-center justify-center" style={{ height: `${height}px` }}>
          <div>
            <p className="mb-2">⏳ Waiting for chart data...</p>
            <p className="text-xs">Library: ✅ | Initialized: {isInitialized ? '✅' : '⏳'}</p>
          </div>
        </div>
      ) : (
        <div 
          ref={chartContainerRef} 
          className="w-full bg-black" 
          style={{ height: `${height}px`, minHeight: `${height}px`, width: '100%' }}
        />
      )}
    </Card>
  )
}
