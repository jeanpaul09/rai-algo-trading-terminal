"use client"

import { useEffect, useRef, useState } from "react"
import { 
  createChart, 
  ColorType, 
  IChartApi, 
  ISeriesApi, 
  CandlestickData,
  CandlestickSeriesOptions,
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

  // Filter annotations by strategy if filter is set
  const filteredAnnotations = strategyFilter
    ? annotations.filter((a) => a.strategy === strategyFilter)
    : annotations

  useEffect(() => {
    if (!chartContainerRef.current) return

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "#000000" },
        textColor: "#d1d5db",
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

    // Add candlestick series - lightweight-charts v5 API
    // Note: TypeScript types may not match runtime API, using type assertion
    const candlestickSeries = (chart as any).addCandlestickSeries({
      upColor: "#10b981",
      downColor: "#ef4444",
      borderVisible: false,
      wickUpColor: "#10b981",
      wickDownColor: "#ef4444",
    }) as ISeriesApi<"Candlestick">

    seriesRef.current = candlestickSeries

    // Convert data format
    const formattedData: CandlestickData[] = data.map((d) => ({
      time: d.time as any,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }))

    candlestickSeries.setData(formattedData)

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chart) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }

    window.addEventListener("resize", handleResize)

    return () => {
      window.removeEventListener("resize", handleResize)
      chart.remove()
    }
  }, [])

  // Update data when it changes
  useEffect(() => {
    if (!seriesRef.current || !data.length) return

    const formattedData: CandlestickData[] = data.map((d) => ({
      time: d.time as any,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }))

    seriesRef.current.setData(formattedData)
  }, [data])

  // Add annotations
  useEffect(() => {
    if (!chartRef.current || !seriesRef.current || !showAnnotations || !filteredAnnotations.length) return

    const chart = chartRef.current
    const series = seriesRef.current

    // Create markers array
    const markers: SeriesMarker<number>[] = filteredAnnotations
      .filter((annotation) => annotation.type !== "region")
      .map((annotation) => {
        const color = annotation.color || getAnnotationColor(annotation.type)
        const shape = getAnnotationShape(annotation.type)
        const position = getAnnotationPosition(annotation.type)

        return {
          time: annotation.timestamp as number,
          position: position as 'aboveBar' | 'belowBar' | 'inBar',
          color: color,
          shape: shape as 'circle' | 'square' | 'arrowUp' | 'arrowDown',
          text: annotation.label || annotation.reason || annotation.type,
          size: 1,
        }
      })

    // Set markers on the series (using setMarkers if available, otherwise ignore for now)
    if (markers.length > 0 && 'setMarkers' in series) {
      (series as any).setMarkers(markers)
    }

    // Add price lines for regions and levels
    const priceLines: any[] = []
    
    filteredAnnotations.forEach((annotation) => {
      if (annotation.type === "region" && annotation.priceEnd) {
        // For regions, add two price lines
        const color = annotation.color || getAnnotationColor(annotation.type)
        priceLines.push(
          (chart as any).createPriceLine({
            price: annotation.price,
            color: color + "40",
            lineWidth: 1,
            lineStyle: 2,
            axisLabelVisible: true,
            title: annotation.label || annotation.type,
          })
        )
        priceLines.push(
          (chart as any).createPriceLine({
            price: annotation.priceEnd,
            color: color + "40",
            lineWidth: 1,
            lineStyle: 2,
            axisLabelVisible: false,
          })
        )
      } else if (annotation.type === "tp" || annotation.type === "sl" || annotation.type === "target") {
        // Add price lines for TP/SL/target levels
        const color = annotation.color || getAnnotationColor(annotation.type)
        priceLines.push(
          (chart as any).createPriceLine({
            price: annotation.price,
            color: color,
            lineWidth: 2,
            lineStyle: 0,
            axisLabelVisible: true,
            title: annotation.label || annotation.type.toUpperCase(),
          })
        )
      }
    })

    // Cleanup price lines on unmount or when annotations change
    return () => {
      priceLines.forEach((line) => {
        if ((chart as any).removePriceLine) {
          (chart as any).removePriceLine(line)
        }
      })
      priceLinesRef.current = []
    }
  }, [filteredAnnotations, showAnnotations])

  return (
    <Card className="w-full">
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h3 className="font-semibold">{symbol}</h3>
          <div className="text-sm text-muted-foreground">
            {data.length} candles • {filteredAnnotations.length} annotations
          </div>
        </div>
        {strategyFilter && (
          <div className="text-xs text-muted-foreground">
            Filtered: {strategyFilter}
          </div>
        )}
      </div>
      <div ref={chartContainerRef} className="w-full" style={{ height: `${height}px` }} />
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

