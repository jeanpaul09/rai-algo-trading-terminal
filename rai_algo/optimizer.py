"""
Parameter optimization engine for RAI-ALGO framework.
"""
import itertools
from typing import List, Dict, Any, Callable, Optional
import numpy as np

from rai_algo.base import BaseStrategy
from rai_algo.backtest import BacktestEngine
from rai_algo.data_types import MarketData, BacktestResult, OptimizationResult


class Optimizer:
    """
    Parameter optimization engine using grid search.
    """
    
    def __init__(
        self,
        backtest_engine: BacktestEngine,
        objective: str = "sharpe_ratio",  # or "total_return", "profit_factor", etc.
    ):
        """
        Initialize optimizer.
        
        Args:
            backtest_engine: BacktestEngine instance
            objective: Objective metric to maximize ('sharpe_ratio', 'total_return_pct', 'profit_factor', etc.)
        """
        self.backtest_engine = backtest_engine
        self.objective = objective
    
    def optimize(
        self,
        strategy_class: type[BaseStrategy],
        market_data: List[MarketData],
        parameter_grid: Dict[str, List[Any]],
        strategy_name: str = "Strategy",
        verbose: bool = False,
    ) -> OptimizationResult:
        """
        Optimize strategy parameters using grid search.
        
        Args:
            strategy_class: Strategy class (not instance)
            market_data: Historical market data for backtesting
            parameter_grid: Dictionary mapping parameter names to lists of values to test
                          e.g., {'stop_loss_pct': [0.01, 0.02, 0.03], 'take_profit_pct': [0.05, 0.10]}
            strategy_name: Name for the strategy
            verbose: Print progress if True
            
        Returns:
            OptimizationResult with best parameters and results
        """
        # Generate all parameter combinations
        param_names = list(parameter_grid.keys())
        param_values = list(parameter_grid.values())
        param_combinations = list(itertools.product(*param_values))
        
        if verbose:
            print(f"Testing {len(param_combinations)} parameter combinations...")
        
        all_results: List[tuple[Dict[str, Any], BacktestResult]] = []
        best_score = float('-inf')
        best_params = None
        best_backtest = None
        
        for i, param_combo in enumerate(param_combinations):
            # Create parameter dictionary
            params = dict(zip(param_names, param_combo))
            
            # Create strategy instance with these parameters
            strategy = strategy_class(strategy_name, params)
            
            # Run backtest
            try:
                result = self.backtest_engine.run(strategy, market_data, verbose=False)
                
                # Calculate objective score
                score = self._get_objective_score(result)
                
                all_results.append((params, result))
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    best_backtest = result
                
                if verbose and (i + 1) % 10 == 0:
                    print(f"Progress: {i + 1}/{len(param_combinations)} combinations tested")
            
            except Exception as e:
                if verbose:
                    print(f"Error testing parameters {params}: {e}")
                continue
        
        if best_backtest is None:
            raise ValueError("No valid parameter combinations found")
        
        return OptimizationResult(
            best_parameters=best_params,
            best_score=best_score,
            best_backtest=best_backtest,
            all_results=all_results,
        )
    
    def _get_objective_score(self, result: BacktestResult) -> float:
        """Get objective score from backtest result."""
        if self.objective == "sharpe_ratio":
            return result.sharpe_ratio
        elif self.objective == "total_return_pct":
            return result.total_return_pct
        elif self.objective == "profit_factor":
            return result.profit_factor
        elif self.objective == "win_rate":
            return result.win_rate
        elif self.objective == "compound_return":
            # Compound return = (1 + return_pct/100) ^ (252 / avg_days_per_trade)
            if result.avg_trade_duration > 0:
                trades_per_year = (365 * 24) / result.avg_trade_duration
                return ((1 + result.total_return_pct / 100) ** (252 / trades_per_year) - 1) * 100
            return result.total_return_pct
        else:
            raise ValueError(f"Unknown objective: {self.objective}")
    
    def optimize_with_constraints(
        self,
        strategy_class: type[BaseStrategy],
        market_data: List[MarketData],
        parameter_grid: Dict[str, List[Any]],
        constraints: Dict[str, Callable[[BacktestResult], bool]],
        strategy_name: str = "Strategy",
        verbose: bool = False,
    ) -> OptimizationResult:
        """
        Optimize with constraints (e.g., max_drawdown < 20%, win_rate > 0.5).
        
        Args:
            strategy_class: Strategy class
            market_data: Historical market data
            parameter_grid: Parameter grid to search
            constraints: Dictionary mapping constraint names to validation functions
                        e.g., {'max_dd': lambda r: r.max_drawdown_pct < 20}
            strategy_name: Strategy name
            verbose: Print progress
            
        Returns:
            OptimizationResult with best parameters that meet constraints
        """
        # Generate all parameter combinations
        param_names = list(parameter_grid.keys())
        param_values = list(parameter_grid.values())
        param_combinations = list(itertools.product(*param_values))
        
        if verbose:
            print(f"Testing {len(param_combinations)} parameter combinations with constraints...")
        
        all_results: List[tuple[Dict[str, Any], BacktestResult]] = []
        best_score = float('-inf')
        best_params = None
        best_backtest = None
        
        for i, param_combo in enumerate(param_combinations):
            params = dict(zip(param_names, param_combo))
            strategy = strategy_class(strategy_name, params)
            
            try:
                result = self.backtest_engine.run(strategy, market_data, verbose=False)
                
                # Check constraints
                meets_all_constraints = all(
                    constraint(result) for constraint in constraints.values()
                )
                
                if not meets_all_constraints:
                    if verbose:
                        print(f"Parameters {params} failed constraints, skipping...")
                    continue
                
                score = self._get_objective_score(result)
                all_results.append((params, result))
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    best_backtest = result
                
                if verbose and (i + 1) % 10 == 0:
                    print(f"Progress: {i + 1}/{len(param_combinations)} combinations tested")
            
            except Exception as e:
                if verbose:
                    print(f"Error testing parameters {params}: {e}")
                continue
        
        if best_backtest is None:
            raise ValueError("No parameter combinations met the constraints")
        
        return OptimizationResult(
            best_parameters=best_params,
            best_score=best_score,
            best_backtest=best_backtest,
            all_results=all_results,
        )

