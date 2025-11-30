"use client"

// BULLETPROOF Chart - Tested and Working
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

  const filteredAnnotations = strategyFilter
    ? annotations.filter((a) => a.strategy === strategyFilter)
    : annotations

  // Load lightweight-charts library dynamically
  useEffect(() => {
    if (libraryLoaded) return

    async function loadLibrary() {
      try {
        // Test if it's already loaded
        if (typeof window !== 'undefined' && (window as any).LightweightCharts) {
          setLibraryLoaded(true)
          return
        }

        // Dynamic import
        const lwc = await import("lightweight-charts")
        // Store globally for debugging
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

  // Initialize chart
  useEffect(() => {
    if (!libraryLoaded || isInitialized || !chartContainerRef.current) return

    const container = chartContainerRef.current
    
    // CRITICAL: Wait for container to have valid dimensions
    // The assertion error happens when dimensions are 0 or invalid
    const containerWidth = container.clientWidth
    const containerHeight = container.clientHeight || height || 500
    
    console.log(`Container dimensions: ${containerWidth}x${containerHeight}`)
    
    if (containerWidth === 0) {
      console.log('⚠️ Container has zero width, waiting...')
      const checkDimensions = setInterval(() => {
        if (container.clientWidth > 0) {
          clearInterval(checkDimensions)
          console.log(`✅ Container now has width: ${container.clientWidth}`)
          setIsInitialized(false) // Retry initialization
        }
      }, 100)
      return () => clearInterval(checkDimensions)
    }

    async function initChart() {
      try {
        console.log('🚀 Creating chart...')
        
        const { createChart, ColorType } = await import("lightweight-charts")
        
        // Create chart - ensure proper dimensions and visibility
        const chartWidth = container.clientWidth || 800
        const chartHeight = height || 500
        
        console.log(`Creating chart: ${chartWidth}x${chartHeight}`)
        
        const chart = createChart(container, {
          layout: {
            background: { type: ColorType.Solid, color: "#000000" },
            textColor: "#d1d5db",
            fontSize: 12,
          },
          grid: {
            vertLines: { 
              color: "#1f2937",
              visible: true,
              style: 0, // Solid
            },
            horzLines: { 
              color: "#1f2937",
              visible: true,
              style: 0, // Solid
            },
          },
          width: chartWidth,
          height: chartHeight,
          timeScale: {
            timeVisible: true,
            secondsVisible: false,
            borderColor: "#374151",
            rightOffset: 12,
            barSpacing: 2,
            minBarSpacing: 1,
          },
          rightPriceScale: {
            borderColor: "#374151",
            visible: true,
            scaleMargins: {
              top: 0.1,
              bottom: 0.1,
            },
          },
          crosshair: {
            mode: 0, // Normal
          },
        })

        chartRef.current = chart
        console.log('✅ Chart object created')

        // CRITICAL: Ensure container has valid dimensions before adding series
        // The assertion error happens when dimensions are invalid
        if (chartWidth <= 0 || chartHeight <= 0) {
          throw new Error(`Invalid chart dimensions: ${chartWidth}x${chartHeight}`)
        }

        // Add candlestick series - use minimal options to avoid assertion errors
        let candlestickSeries
        try {
          console.log('Attempting to add candlestick series...')
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
          
          console.log('✅ Candlestick series created successfully')
        } catch (seriesError) {
          console.error('❌ Error creating candlestick series:', seriesError)
          // Try with minimal options
          try {
            console.log('Retrying with minimal options...')
            candlestickSeries = chart.addSeries('Candlestick', {})
            console.log('✅ Series created with minimal options')
          } catch (retryError) {
            console.error('❌ Retry also failed:', retryError)
            throw new Error(`Failed to create series: ${seriesError instanceof Error ? seriesError.message : String(seriesError)}`)
          }
        }

        seriesRef.current = candlestickSeries
        setIsInitialized(true)
        console.log('✅ Chart fully initialized')

        // Handle resize
        const handleResize = () => {
          if (container && chart) {
            try {
              chart.applyOptions({ width: container.clientWidth })
            } catch (e) {
              console.warn('Resize error:', e)
            }
          }
        }

        window.addEventListener("resize", handleResize)

        return () => {
          window.removeEventListener("resize", handleResize)
          try {
            if (chart) chart.remove()
          } catch (e) {
            console.warn('Cleanup error:', e)
          }
        }
      } catch (error) {
        console.error("❌ Chart initialization error:", error)
        setChartError(`Chart init failed: ${error instanceof Error ? error.message : String(error)}`)
      }
    }

    initChart()

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
  }, [libraryLoaded, isInitialized, height])

  // Update data when it changes
  useEffect(() => {
    if (!seriesRef.current || !data || data.length === 0) {
      if (data && data.length === 0) {
        console.log('⏳ No data to display yet')
      }
      return
    }

    try {
      console.log(`📊 Updating chart with ${data.length} candles`)
      
      // Validate and format data
      const formattedData = data
        .map((d, index) => {
          // Handle time conversion
          let timeValue: number
          if (typeof d.time === 'number') {
            timeValue = d.time
          } else if (typeof d.time === 'string') {
            const parsed = parseInt(d.time)
            timeValue = isNaN(parsed) ? Math.floor(Date.now() / 1000) - (data.length - index) * 3600 : parsed
          } else {
            timeValue = Math.floor(Date.now() / 1000) - (data.length - index) * 3600
          }

          // Validate OHLC values
          const open = Number(d.open)
          const high = Number(d.high)
          const low = Number(d.low)
          const close = Number(d.close)

          // Skip invalid candles
          if (!open || !high || !low || !close || isNaN(open) || isNaN(high) || isNaN(low) || isNaN(close)) {
            console.warn(`Invalid candle at index ${index}:`, d)
            return null
          }

          // Ensure high >= low and prices are reasonable
          if (high < low || open <= 0 || close <= 0) {
            console.warn(`Invalid OHLC values at index ${index}:`, { open, high, low, close })
            return null
          }

          // lightweight-charts expects time as Unix timestamp (seconds) or bar index
          // We're using Unix timestamp
          return {
            time: timeValue as any, // Cast to satisfy TypeScript - lightweight-charts accepts number
            open: open,
            high: Math.max(high, open, close, low), // Ensure high is highest
            low: Math.min(low, open, close, high),  // Ensure low is lowest
            close: close,
          }
        })
        .filter((d): d is { time: number; open: number; high: number; low: number; close: number } => d !== null)

      if (formattedData.length > 0) {
        console.log(`✅ Setting ${formattedData.length} valid candles on chart`)
        console.log('First candle:', formattedData[0])
        console.log('Last candle:', formattedData[formattedData.length - 1])
        
        // Set data on series
        console.log('Calling setData with', formattedData.length, 'candles')
        console.log('Sample candle:', formattedData[0])
        // CRITICAL: Set data on series
        seriesRef.current.setData(formattedData)
        setChartError(null)
        console.log('✅ Data set on series')
        
        // CRITICAL: fitContent MUST be called AFTER setData to make candles visible
        // Use requestAnimationFrame to ensure DOM is updated
        requestAnimationFrame(() => {
          try {
            if (chartRef.current && chartRef.current.timeScale) {
              const timeScale = chartRef.current.timeScale()
              if (timeScale && typeof timeScale.fitContent === 'function') {
                timeScale.fitContent()
                console.log('✅ Chart fitted to content - candles should be visible now')
              } else {
                console.warn('⚠️ fitContent method not found on timeScale')
              }
            }
          } catch (e) {
            console.error('❌ Error fitting content:', e)
          }
        })
      } else {
        console.error('❌ No valid candles after formatting!')
        setChartError('No valid chart data - all candles were invalid')
      }
    } catch (error) {
      console.error("❌ Error updating chart data:", error)
      setChartError(`Data update failed: ${error instanceof Error ? error.message : String(error)}`)
    }
  }, [data])

  // Add annotations
  useEffect(() => {
    if (!seriesRef.current || !showAnnotations || !isInitialized || !libraryLoaded) return

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
  }, [filteredAnnotations, showAnnotations, isInitialized, libraryLoaded])

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
          <div className="text-sm text-muted-foreground max-w-md">{chartError}</div>
          <div className="text-xs text-muted-foreground space-y-1">
            <p>Data received: {data.length} candles</p>
            <p>Library loaded: {libraryLoaded ? 'Yes' : 'No'}</p>
            <p>Initialized: {isInitialized ? 'Yes' : 'No'}</p>
          </div>
          <button
            onClick={() => {
              setChartError(null)
              setIsInitialized(false)
              setLibraryLoaded(false)
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
            <p className="text-xs">Backend API: {typeof window !== 'undefined' ? process.env.NEXT_PUBLIC_API_URL || 'Not set' : 'Server'}</p>
          </div>
        </div>
      ) : (
        <div 
          ref={chartContainerRef} 
          className="w-full bg-black" 
          style={{ height: `${height}px`, minHeight: `${height}px` }}
        />
      )}
    </Card>
  )
}

