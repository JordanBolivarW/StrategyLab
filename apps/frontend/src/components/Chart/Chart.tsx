import { useEffect, useRef, useMemo } from 'react'
import type { IChartApi, ISeriesApi, Time } from 'lightweight-charts';
import { createChart } from 'lightweight-charts'
import type { Candle, Trade, EquityPoint } from '@/types/strategy'

interface ChartProps {
  data: (Candle | EquityPoint)[]
  trades: Trade[]
  seriesType?: 'candlestick' | 'line'
  indicators?: Array<{ name: string; data: Array<{ time: Time; value: number }>; color: string }>
}

export default function Chart({ data, trades, seriesType = 'candlestick', indicators = [] }: ChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | ISeriesApi<'Line'> | null>(null)

  const isCandle = seriesType === 'candlestick'

  const formattedData = useMemo(() => {
    return data.map((item: Candle | EquityPoint) => {
      if (isCandle) {
        return {
          time: item.timestamp as Time,
          open: (item as Candle).open,
          high: (item as Candle).high,
          low: (item as Candle).low,
          close: (item as Candle).close,
        }
      } else {
        return {
          time: item.timestamp as Time,
          value: (item as EquityPoint).equity,
        }
      }
    })
  }, [data, isCandle])

  const tradeMarkers = useMemo(() => {
    return trades.map((trade) => ({
      time: trade.entry_time as Time,
      position: 'belowBar' as const,
      color: trade.type === 'LONG' ? '#10b981' : '#ef4444',
      shape: 'arrowUp' as const,
      text: `${trade.type} @ ${trade.entry_price}`,
    }))
  }, [trades])

  useEffect(() => {
    if (!containerRef.current) return

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: containerRef.current.clientHeight,
      layout: {
        background: { color: '#0f172a' },
        textColor: '#e2e8f0',
      },
      grid: {
        vertLines: { color: '#1e293b' },
        horzLines: { color: '#1e293b' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#334155',
        scaleMargins: { top: 0.1, bottom: 0.1 },
      },
      timeScale: {
        borderColor: '#334155',
        timeVisible: true,
        secondsVisible: false,
      },
    })

    chartRef.current = chart

    let series: ISeriesApi<'Candlestick'> | ISeriesApi<'Line'>
    if (isCandle) {
      series = chart.addCandlestickSeries({
        upColor: '#10b981',
        downColor: '#ef4444',
        borderUpColor: '#10b981',
        borderDownColor: '#ef4444',
        wickUpColor: '#10b981',
        wickDownColor: '#ef4444',
      })
    } else {
      series = chart.addLineSeries({
        color: '#0ea5e9',
        lineWidth: 1,
      })
    }

    seriesRef.current = series
    series.setData(formattedData)

    if (isCandle) {
      series.setMarkers(tradeMarkers)
    }

    // Add indicator series
    indicators.forEach((indicator) => {
      const indicatorSeries = chart.addLineSeries({
        color: indicator.color,
        lineWidth: 1,
      })
      indicatorSeries.setData(indicator.data)
    })

    // Handle resize
    const resizeObserver = new ResizeObserver(() => {
      if (containerRef.current) {
        chart.resize(containerRef.current.clientWidth, containerRef.current.clientHeight)
      }
    })
    resizeObserver.observe(containerRef.current)

    return () => {
      resizeObserver.disconnect()
      chart.remove()
    }
  }, [isCandle, formattedData, indicators, tradeMarkers])

  // Update data when it changes
  useEffect(() => {
    if (seriesRef.current && formattedData.length > 0) {
      seriesRef.current.setData(formattedData)
    }
  }, [formattedData])

  // Update markers when trades change
  useEffect(() => {
    if (seriesRef.current && isCandle) {
      seriesRef.current.setMarkers(tradeMarkers)
    }
  }, [tradeMarkers, isCandle])

  return (
    <div
      ref={containerRef}
      className="chart-container"
      style={{ width: '100%', height: '100%' }}
    />
  )
}