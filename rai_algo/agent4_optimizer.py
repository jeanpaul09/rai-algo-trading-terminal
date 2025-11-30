"""
AGENT 4 — STRATEGY OPTIMIZER

Takes a strategy and backtest results, then optimizes it by:
1. Identifying weaknesses (drawdowns, whipsaws, slippage sensitivity)
2. Running parameter sweeps
3. Proposing optimized versions
"""
import itertools
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from rai_algo.base import BaseStrategy
from rai_algo.backtest import BacktestEngine
from rai_algo.optimizer import Optimizer
from rai_algo.data_types import MarketData, BacktestResult, OptimizationResult


@dataclass
class WeaknessAnalysis:
    """Analysis of strategy weaknesses."""
    high_drawdown: bool
    drawdown_severity: str  # "low", "medium", "high", "critical"
    whipsaw_signals: bool
    slippage_sensitive: bool
    low_win_rate: bool
    poor_profit_factor: bool
    weaknesses: List[str]
    recommendations: List[str]


class Agent4StrategyOptimizer:
    """
    AGENT 4 — STRATEGY OPTIMIZER
    
    Analyzes strategy performance and optimizes parameters.
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0005,
    ):
        """
        Initialize AGENT 4.
        
        Args:
            initial_capital: Starting capital for backtests
            commission: Commission rate per trade
            slippage: Slippage rate
        """
        self.backtest_engine = BacktestEngine(
            initial_capital=initial_capital,
            commission=commission,
            slippage=slippage,
        )
        self.optimizer = Optimizer(self.backtest_engine, objective="sharpe_ratio")
    
    def optimize_strategy(
        self,
        strategy_class: type[BaseStrategy],
        market_data: List[MarketData],
        original_parameters: Optional[Dict[str, Any]] = None,
        strategy_name: str = "Strategy",
        parameter_grid: Optional[Dict[str, List[Any]]] = None,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """
        Complete optimization workflow.
        
        Args:
            strategy_class: Strategy class to optimize
            market_data: Historical market data
            original_parameters: Original strategy parameters (if None, uses defaults)
            strategy_name: Strategy name
            parameter_grid: Custom parameter grid (if None, generates default grid)
            verbose: Print progress
            
        Returns:
            Dictionary with optimization results in the requested format
        """
        # Step 1: Backtest original strategy
        original_params = original_parameters or {}
        original_strategy = strategy_class(strategy_name, original_params.copy())
        original_result = self.backtest_engine.run(original_strategy, market_data, verbose=verbose)
        
        if verbose:
            print("\n" + "="*60)
            print("ORIGINAL STRATEGY BACKTEST RESULTS")
            print("="*60)
            self._print_results(original_result)
        
        # Step 2: Identify weaknesses
        weaknesses = self._identify_weaknesses(original_result)
        
        if verbose:
            print("\n" + "="*60)
            print("WEAKNESS ANALYSIS")
            print("="*60)
            self._print_weaknesses(weaknesses)
        
        # Step 3: Run parameter optimization
        if parameter_grid is None:
            parameter_grid = self._generate_default_parameter_grid(original_params)
        
        if verbose:
            print("\n" + "="*60)
            print("RUNNING PARAMETER OPTIMIZATION")
            print("="*60)
            print(f"Testing {len(list(itertools.product(*parameter_grid.values())))} combinations...")
        
        try:
            opt_result = self.optimizer.optimize(
                strategy_class,
                market_data,
                parameter_grid,
                strategy_name,
                verbose=verbose,
            )
        except Exception as e:
            if verbose:
                print(f"Optimization failed: {e}")
            opt_result = None
        
        # Step 4: Generate recommendations
        recommendations = self._generate_recommendations(
            original_result,
            weaknesses,
            opt_result,
        )
        
        # Step 5: Create optimized strategy variant
        if opt_result:
            optimized_strategy_variant = self._create_optimized_variant(
                strategy_class,
                opt_result.best_parameters,
                strategy_name,
            )
        else:
            optimized_strategy_variant = None
        
        # Step 6: Format output
        output = {
            "original_results": original_result.to_dict(),
            "weakness_analysis": asdict(weaknesses),
            "optimized_parameters": opt_result.best_parameters if opt_result else None,
            "improved_results": opt_result.best_backtest.to_dict() if opt_result else None,
            "recommendations": recommendations,
            "final_strategy_variant": optimized_strategy_variant,
        }
        
        return output
    
    def _identify_weaknesses(self, result: BacktestResult) -> WeaknessAnalysis:
        """Identify weaknesses in strategy performance."""
        weaknesses = []
        recommendations = []
        
        # Check drawdown
        high_drawdown = result.max_drawdown_pct > 20
        if result.max_drawdown_pct > 40:
            drawdown_severity = "critical"
        elif result.max_drawdown_pct > 25:
            drawdown_severity = "high"
        elif result.max_drawdown_pct > 15:
            drawdown_severity = "medium"
        else:
            drawdown_severity = "low"
        
        if high_drawdown:
            weaknesses.append(f"High max drawdown: {result.max_drawdown_pct:.2f}%")
            recommendations.append("Consider tighter stop-loss or position sizing limits")
        
        # Check win rate
        low_win_rate = result.win_rate < 0.40
        if low_win_rate:
            weaknesses.append(f"Low win rate: {result.win_rate*100:.1f}%")
            recommendations.append("Consider improving entry signal quality or adding filters")
        
        # Check profit factor
        poor_profit_factor = result.profit_factor < 1.2
        if poor_profit_factor and result.total_trades > 0:
            weaknesses.append(f"Poor profit factor: {result.profit_factor:.2f}")
            recommendations.append("Work on improving risk/reward ratio (stop-loss vs take-profit)")
        
        # Check for whipsaws (many small trades, low avg duration)
        whipsaw_signals = False
        if result.avg_trade_duration < 1.0 and result.total_trades > 20:
            whipsaw_signals = True
            weaknesses.append(f"Potential whipsaws: Avg trade duration only {result.avg_trade_duration:.2f} hours")
            recommendations.append("Add trend filter or increase signal confirmation requirements")
        
        # Check slippage sensitivity (many trades relative to returns)
        slippage_sensitive = False
        if result.total_trades > 50 and result.total_return_pct < 5:
            slippage_sensitive = True
            weaknesses.append(f"High trade frequency ({result.total_trades} trades) with low returns")
            recommendations.append("Reduce trade frequency or improve signal quality")
        
        # Additional checks
        if result.total_trades == 0:
            weaknesses.append("No trades executed - strategy may be too conservative")
            recommendations.append("Check entry conditions and ensure signals are being generated")
        
        if result.winning_trades > 0 and result.avg_loss > 0:
            risk_reward_ratio = result.avg_win / result.avg_loss if result.avg_loss > 0 else 0
            if risk_reward_ratio < 1.0:
                weaknesses.append(f"Poor risk/reward ratio: {risk_reward_ratio:.2f}")
                recommendations.append("Consider wider take-profit targets relative to stop-loss")
        
        return WeaknessAnalysis(
            high_drawdown=high_drawdown,
            drawdown_severity=drawdown_severity,
            whipsaw_signals=whipsaw_signals,
            slippage_sensitive=slippage_sensitive,
            low_win_rate=low_win_rate,
            poor_profit_factor=poor_profit_factor,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )
    
    def _generate_default_parameter_grid(
        self,
        original_params: Dict[str, Any],
    ) -> Dict[str, List[Any]]:
        """Generate default parameter grid for optimization."""
        grid = {}
        
        # Stop-loss sweep
        if 'stop_loss_pct' in original_params:
            base_sl = original_params['stop_loss_pct']
            grid['stop_loss_pct'] = [
                max(0.005, base_sl * 0.5),
                base_sl * 0.75,
                base_sl,
                base_sl * 1.25,
                min(0.10, base_sl * 1.5),
            ]
        else:
            grid['stop_loss_pct'] = [0.01, 0.02, 0.03, 0.05]
        
        # Take-profit sweep
        if 'take_profit_pct' in original_params:
            base_tp = original_params['take_profit_pct']
            grid['take_profit_pct'] = [
                base_tp * 0.5,
                base_tp * 0.75,
                base_tp,
                base_tp * 1.25,
                base_tp * 1.5,
            ]
        else:
            grid['take_profit_pct'] = [0.03, 0.05, 0.10, 0.15, 0.20]
        
        # Moving average periods (if applicable)
        if 'ma_fast' in original_params:
            base_fast = original_params['ma_fast']
            grid['ma_fast'] = [
                max(5, base_fast - 5),
                base_fast,
                base_fast + 5,
            ]
        
        if 'ma_slow' in original_params:
            base_slow = original_params['ma_slow']
            grid['ma_slow'] = [
                base_slow - 10,
                base_slow,
                base_slow + 10,
            ]
        
        # Volatility filter (if applicable)
        if 'volatility_threshold' in original_params:
            base_vol = original_params['volatility_threshold']
            grid['volatility_threshold'] = [
                base_vol * 0.75,
                base_vol,
                base_vol * 1.25,
            ]
        
        # Trend filter (if applicable)
        if 'trend_strength_threshold' in original_params:
            base_trend = original_params['trend_strength_threshold']
            grid['trend_strength_threshold'] = [
                base_trend * 0.8,
                base_trend,
                base_trend * 1.2,
            ]
        
        return grid
    
    def _generate_recommendations(
        self,
        original_result: BacktestResult,
        weaknesses: WeaknessAnalysis,
        opt_result: Optional[OptimizationResult],
    ) -> str:
        """Generate comprehensive recommendations."""
        recs = []
        
        # Add weakness-based recommendations
        recs.extend(weaknesses.recommendations)
        
        # Compare original vs optimized
        if opt_result:
            opt_result_dict = opt_result.best_backtest.to_dict()
            
            # Check improvements
            if opt_result_dict['sharpe_ratio'] > original_result.sharpe_ratio * 1.1:
                recs.append(
                    f"Optimization improved Sharpe ratio from {original_result.sharpe_ratio:.2f} "
                    f"to {opt_result_dict['sharpe_ratio']:.2f} (+{((opt_result_dict['sharpe_ratio']/original_result.sharpe_ratio - 1)*100):.1f}%)"
                )
            
            if opt_result_dict['max_drawdown_pct'] < original_result.max_drawdown_pct * 0.9:
                recs.append(
                    f"Optimization reduced max drawdown from {original_result.max_drawdown_pct:.2f}% "
                    f"to {opt_result_dict['max_drawdown_pct']:.2f}%"
                )
            
            if opt_result_dict['total_return_pct'] > original_result.total_return_pct * 1.1:
                recs.append(
                    f"Optimization improved returns from {original_result.total_return_pct:.2f}% "
                    f"to {opt_result_dict['total_return_pct']:.2f}%"
                )
            
            recs.append(f"Best parameters found: {json.dumps(opt_result.best_parameters, indent=2)}")
        
        # General recommendations
        if original_result.total_trades < 10:
            recs.append("Strategy may need more data or less restrictive entry conditions")
        
        if original_result.profit_factor > 2.0 and original_result.win_rate > 0.5:
            recs.append("Strategy shows strong performance - consider regime-based activation to trade only in favorable conditions")
        
        return "\n".join(f"- {rec}" for rec in recs)
    
    def _create_optimized_variant(
        self,
        strategy_class: type[BaseStrategy],
        optimized_params: Dict[str, Any],
        strategy_name: str,
    ) -> str:
        """Create optimized strategy variant code."""
        # Create a code snippet showing how to instantiate with optimized parameters
        params_str = json.dumps(optimized_params, indent=2)
        
        code = f"""# Optimized {strategy_name}
# Use these parameters for improved performance

optimized_strategy = {strategy_class.__name__}(
    name="{strategy_name}_optimized",
    parameters={params_str}
)

# Or as a dictionary:
optimized_params = {params_str}
"""
        return code
    
    def _print_results(self, result: BacktestResult):
        """Print backtest results in readable format."""
        print(f"Total Trades: {result.total_trades}")
        print(f"Win Rate: {result.win_rate*100:.2f}%")
        print(f"Total Return: ${result.total_return:.2f} ({result.total_return_pct:.2f}%)")
        print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"Max Drawdown: ${result.max_drawdown:.2f} ({result.max_drawdown_pct:.2f}%)")
        print(f"Profit Factor: {result.profit_factor:.2f}")
        print(f"Avg Win: ${result.avg_win:.2f}")
        print(f"Avg Loss: ${result.avg_loss:.2f}")
        print(f"Avg Trade Duration: {result.avg_trade_duration:.2f} hours")
    
    def _print_weaknesses(self, weaknesses: WeaknessAnalysis):
        """Print weakness analysis."""
        print(f"Drawdown Severity: {weaknesses.drawdown_severity.upper()}")
        print(f"Whipsaw Signals: {'Yes' if weaknesses.whipsaw_signals else 'No'}")
        print(f"Slippage Sensitive: {'Yes' if weaknesses.slippage_sensitive else 'No'}")
        print(f"Low Win Rate: {'Yes' if weaknesses.low_win_rate else 'No'}")
        print(f"Poor Profit Factor: {'Yes' if weaknesses.poor_profit_factor else 'No'}")
        print("\nIdentified Weaknesses:")
        for weakness in weaknesses.weaknesses:
            print(f"  • {weakness}")

