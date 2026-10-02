import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import axios from 'axios'
import type {
  StrategyResponse,
  StrategyListResponse,
  StrategyCreate,
  StrategyUpdate,
  StrategyVersionResponse,
  BacktestCreate,
  BacktestResponse,
  BacktestMetrics,
  Trade,
  MarketResponse,
  Candle,
  MCPTool,
  MCPToolCall,
  MCPToolResult,
} from '../types/strategy'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    })

    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // Add auth token if available
        const token = localStorage.getItem('access_token')
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          localStorage.removeItem('access_token')
          window.location.href = '/login'
        }
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
      }
    )
  }

  // Strategies
  async listStrategies(page = 1, pageSize = 20, market?: string): Promise<StrategyListResponse> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
    if (market) params.append('market', market)
    const response = await this.client.get<StrategyListResponse>(`/strategies?${params}`)
    return response.data
  }

  async getStrategy(id: string): Promise<StrategyResponse> {
    const response = await this.client.get<StrategyResponse>(`/strategies/${id}`)
    return response.data
  }

  async createStrategy(data: StrategyCreate): Promise<StrategyResponse> {
    const response = await this.client.post<StrategyResponse>('/strategies', data)
    return response.data
  }

  async updateStrategy(id: string, data: StrategyUpdate): Promise<StrategyResponse> {
    const response = await this.client.patch<StrategyResponse>(`/strategies/${id}`, data)
    return response.data
  }

  async deleteStrategy(id: string): Promise<void> {
    await this.client.delete(`/strategies/${id}`)
  }

  async cloneStrategy(id: string, name: string): Promise<StrategyResponse> {
    const response = await this.client.post<StrategyResponse>(`/strategies/${id}/clone`, null, {
      params: { name },
    })
    return response.data
  }

  async getStrategyVersions(id: string): Promise<StrategyVersionResponse[]> {
    const response = await this.client.get<StrategyVersionResponse[]>(`/strategies/${id}/versions`)
    return response.data
  }

  async validateStrategy(id: string): Promise<{ valid: boolean; errors: string[] }> {
    const response = await this.client.post<{ valid: boolean; errors: string[] }>(`/strategies/${id}/validate`)
    return response.data
  }

  // Backtests
  async listBacktests(strategyId?: string, status?: string): Promise<BacktestResponse[]> {
    const params = new URLSearchParams()
    if (strategyId) params.append('strategy_id', strategyId)
    if (status) params.append('status', status)
    params.append('limit', '50')
    const response = await this.client.get<BacktestResponse[]>(`/backtests?${params}`)
    return response.data
  }

  async getBacktest(id: string): Promise<BacktestResponse> {
    const response = await this.client.get<BacktestResponse>(`/backtests/${id}`)
    return response.data
  }

  async createBacktest(data: BacktestCreate): Promise<BacktestResponse> {
    const response = await this.client.post<BacktestResponse>('/backtests', data)
    return response.data
  }

  async getBacktestTrades(id: string): Promise<Trade[]> {
    const response = await this.client.get<Trade[]>(`/backtests/${id}/trades`)
    return response.data
  }

  async getBacktestMetrics(id: string): Promise<BacktestMetrics> {
    const response = await this.client.get<BacktestMetrics>(`/backtests/${id}/metrics`)
    return response.data
  }

  // Markets
  async listMarkets(): Promise<MarketResponse[]> {
    const response = await this.client.get<MarketResponse[]>('/markets')
    return response.data
  }

  async getMarket(symbol: string): Promise<MarketResponse> {
    const response = await this.client.get<MarketResponse>(`/markets/${symbol}`)
    return response.data
  }

  async getMarketData(
    symbol: string,
    timeframe: string,
    startDate?: string,
    endDate?: string,
    limit = 1000
  ): Promise<{ symbol: string; timeframe: string; candles: Candle[] }> {
    const params = new URLSearchParams({ timeframe, limit: String(limit) })
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const response = await this.client.get<{ symbol: string; timeframe: string; candles: Candle[] }>(
      `/markets/${symbol}/data?${params}`
    )
    return response.data
  }

  // MCP
  async listMcpTools(): Promise<MCPTool[]> {
    const response = await this.client.get<MCPTool[]>('/mcp/tools')
    return response.data
  }

  async callMcpTool(call: MCPToolCall): Promise<MCPToolResult> {
    const response = await this.client.post<MCPToolResult>('/mcp/tools/call', call)
    return response.data
  }
}

export const api = new ApiClient()