/**
 * TypeScript types for RAI-ALGO Quant Lab Dashboard
 * These types define the structure of data returned from the Python backend API
 */

export interface EquityPoint {
  timestamp: string;
  equity: number;
  pnl?: number;
}

export interface DrawdownPoint {
  timestamp: string;
  drawdown: number;
}

export interface Strategy {
  name: string;
  description?: string;
  markets: string[];
  state: "experimental" | "validated" | "deployed";
  tags: string[];
  best_sharpe?: number;
  worst_drawdown?: number;
  latest_metrics?: StrategyMetrics;
}

export interface StrategyMetrics {
  sharpe: number;
  sortino: number;
  max_drawdown: number;
  cagr: number;
  hit_rate: number;
  win_rate: number;
  profit_factor?: number;
  total_return?: number;
}

export interface Experiment {
  id: string;
  strategy_name: string;
  market: string;
  start_date: string;
  end_date: string;
  status: "completed" | "running" | "failed";
  parameters: Record<string, any>;
  metrics: StrategyMetrics;
  equity_curve?: EquityPoint[];
  drawdown_curve?: DrawdownPoint[];
  return_distribution?: number[];
}

export interface Overview {
  total_strategies: number;
  deployed_strategies: number;
  best_sharpe: number;
  worst_drawdown: number;
  latest_equity_curve: EquityPoint[];
  daily_pnl?: number;
  btc_price?: number;
  data_source?: string;
}

export interface LivePosition {
  exchange: string;
  symbol: string;
  side: "long" | "short";
  size: number;
  entry_price: number;
  mark_price: number;
  unrealized_pnl: number;
  leverage?: number;
}

export interface LiveStatus {
  equity: number;
  daily_pnl: number;
  total_exposure: number;
  max_exposure: number;
  current_drawdown: number;
  max_drawdown_allowed: number;
  risk_status: "OK" | "WARNING" | "CRITICAL";
  positions: LivePosition[];
  venue_overview: VenueOverview[];
}

export interface VenueOverview {
  venue: string;
  notional_exposure: number;
  pnl: number;
  funding_impact?: number;
}

export interface CorrelationMatrix {
  strategies: string[];
  correlations: number[][];
}

export interface MarketExposure {
  market: string;
  exposure: number;
  percentage: number;
}

// Trading Terminal Types
export type AgentMode = "OFF" | "DEMO" | "LIVE";
export type StrategyMode = "OFF" | "DEMO" | "LIVE";
export type TradingMode = "BACKTEST" | "DEMO" | "LIVE";

export interface AgentStatus {
  mode: AgentMode;
  isActive: boolean;
  environment: "testnet" | "mainnet";
  connected: boolean;
  lastUpdate: string;
}

export interface ChartAnnotation {
  id: string;
  type: "entry" | "exit" | "tp" | "sl" | "target" | "region";
  timestamp: number;
  price: number;
  priceEnd?: number; // For regions
  strategy: string;
  reason?: string;
  label?: string;
  color?: string;
}

export interface BrainFeedEntry {
  id: string;
  timestamp: string;
  type: "analysis" | "signal" | "decision" | "trade" | "adjustment" | "warning";
  strategy?: string;
  content: string;
  data?: Record<string, any>;
}

export interface StrategyControl {
  name: string;
  description: string;
  category: string;
  mode: StrategyMode;
  status: "idle" | "scanning" | "in-position" | "cooling-down" | "error";
  parameters: Record<string, any>;
  metrics?: StrategyMetrics;
  currentExposure?: number;
  lastPnL?: number;
}

export interface AgentCommand {
  id: string;
  timestamp: string;
  command: string;
  response?: string;
  status: "pending" | "processing" | "completed" | "failed";
}

export interface WalletInfo {
  address: string;
  balance: number;
  marginUsed: number;
  marginAvailable: number;
  realizedPnL: number;
  unrealizedPnL: number;
  environment: "testnet" | "mainnet";
}

export interface PerformanceComparison {
  mode: TradingMode;
  equityCurve: EquityPoint[];
  metrics: StrategyMetrics;
  trades: Trade[];
}

export interface Trade {
  id: string;
  timestamp: string;
  strategy: string;
  symbol: string;
  side: "long" | "short";
  entryPrice: number;
  exitPrice?: number;
  size: number;
  pnl?: number;
  mode: TradingMode;
  reason?: string;
}

export interface OHLCVData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

