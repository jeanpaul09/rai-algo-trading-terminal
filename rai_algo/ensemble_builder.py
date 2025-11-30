"""
AGENT 5 — ENSEMBLE BUILDER

Takes a list of strategies with backtest results and combines them into robust ensembles.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json


@dataclass
class StrategyBacktest:
    """Backtest results for a single strategy."""
    name: str
    returns: np.ndarray  # Daily/period returns
    sharpe: float
    max_drawdown: float
    volatility: float
    total_return: float
    win_rate: Optional[float] = None
    avg_win: Optional[float] = None
    avg_loss: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class EnsembleBuilder:
    """
    Builds robust trading strategy ensembles from individual strategy backtests.
    
    Features:
    - Identifies complementary strategies (low correlation)
    - Constructs weighted blends
    - Volatility-adjusted allocation
    - Regime switching (momentum vs mean reversion)
    - Portfolio-level performance evaluation
    """
    
    def __init__(
        self,
        strategies: List[StrategyBacktest],
        risk_free_rate: float = 0.0,
        min_correlation: float = -0.3,
        max_correlation: float = 0.7,
        max_exposure: float = 0.4,  # Max weight per strategy
    ):
        """
        Initialize ensemble builder.
        
        Args:
            strategies: List of strategy backtest results
            risk_free_rate: Risk-free rate for Sharpe calculation
            min_correlation: Minimum acceptable correlation (for diversification)
            max_correlation: Maximum acceptable correlation (to avoid redundancy)
            max_exposure: Maximum weight per strategy (exposure limit)
        """
        self.strategies = strategies
        self.risk_free_rate = risk_free_rate
        self.min_correlation = min_correlation
        self.max_correlation = max_correlation
        self.max_exposure = max_exposure
        
        # Validate all returns have same length
        if strategies:
            lengths = [len(s.returns) for s in strategies]
            if len(set(lengths)) > 1:
                raise ValueError("All strategy returns must have the same length")
    
    def compute_correlation_matrix(self) -> np.ndarray:
        """Compute correlation matrix between all strategies."""
        n = len(self.strategies)
        corr_matrix = np.eye(n)
        
        for i in range(n):
            for j in range(i + 1, n):
                corr = np.corrcoef(
                    self.strategies[i].returns,
                    self.strategies[j].returns
                )[0, 1]
                corr_matrix[i, j] = corr
                corr_matrix[j, i] = corr
        
        return corr_matrix
    
    def identify_complementary_strategies(
        self,
        corr_matrix: np.ndarray,
        threshold: float = 0.5
    ) -> List[Tuple[int, int]]:
        """
        Identify pairs of strategies with low correlation (complementary).
        
        Returns list of (i, j) pairs where correlation is below threshold.
        """
        complementary = []
        n = len(self.strategies)
        
        for i in range(n):
            for j in range(i + 1, n):
                if abs(corr_matrix[i, j]) < threshold:
                    complementary.append((i, j))
        
        return complementary
    
    def volatility_adjusted_weights(
        self,
        target_volatility: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Compute volatility-adjusted weights (inverse volatility weighting).
        
        Strategies with lower volatility get higher weights.
        """
        # Inverse volatility weights
        inv_vol = np.array([1.0 / max(s.volatility, 0.01) for s in self.strategies])
        weights = inv_vol / inv_vol.sum()
        
        # Apply exposure limits
        weights = np.clip(weights, 0, self.max_exposure)
        weights = weights / weights.sum()  # Renormalize
        
        # Adjust to target volatility if specified
        if target_volatility:
            portfolio_vol = np.sqrt(
                np.sum([w * s.volatility**2 for w, s in zip(weights, self.strategies)])
            )
            if portfolio_vol > 0:
                scale = target_volatility / portfolio_vol
                weights = weights * scale
                weights = weights / weights.sum()
        
        return {
            self.strategies[i].name: float(weights[i])
            for i in range(len(self.strategies))
        }
    
    def sharpe_optimized_weights(
        self,
        corr_matrix: np.ndarray
    ) -> Dict[str, float]:
        """
        Optimize weights to maximize Sharpe ratio.
        
        Uses mean-variance optimization with Sharpe ratio objective.
        """
        n = len(self.strategies)
        
        # Expected returns (annualized)
        returns = np.array([s.total_return for s in self.strategies])
        
        # Covariance matrix
        cov_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                cov_matrix[i, j] = (
                    corr_matrix[i, j] * 
                    self.strategies[i].volatility * 
                    self.strategies[j].volatility
                )
        
        # Mean-variance optimization (simplified)
        # Maximize: (w^T * r - rf) / sqrt(w^T * C * w)
        # Using iterative optimization
        
        # Start with equal weights
        weights = np.ones(n) / n
        
        # Simple gradient ascent (iterative improvement)
        for _ in range(100):
            portfolio_return = np.dot(weights, returns) - self.risk_free_rate
            portfolio_vol = np.sqrt(weights @ cov_matrix @ weights)
            
            if portfolio_vol < 1e-6:
                break
            
            sharpe = portfolio_return / portfolio_vol
            
            # Gradient approximation
            grad = (returns - self.risk_free_rate) / portfolio_vol - (
                sharpe * (cov_matrix @ weights) / portfolio_vol
            )
            
            # Update with step size
            step = 0.01
            new_weights = weights + step * grad
            new_weights = np.clip(new_weights, 0, self.max_exposure)
            new_weights = new_weights / new_weights.sum()
            
            # Check if improvement
            new_sharpe = (
                (np.dot(new_weights, returns) - self.risk_free_rate) /
                np.sqrt(new_weights @ cov_matrix @ new_weights)
            )
            
            if new_sharpe > sharpe:
                weights = new_weights
            else:
                break
        
        return {
            self.strategies[i].name: float(weights[i])
            for i in range(len(self.strategies))
        }
    
    def regime_detection(
        self,
        returns: np.ndarray,
        lookback: int = 20
    ) -> str:
        """
        Detect market regime: 'trending' or 'mean_reverting'.
        
        Uses rolling statistics to determine if market is trending or mean-reverting.
        """
        if len(returns) < lookback:
            return "neutral"
        
        recent = returns[-lookback:]
        
        # Calculate momentum and mean reversion indicators
        momentum = np.mean(recent[-5:]) - np.mean(recent[:5])
        volatility = np.std(recent)
        autocorr = np.corrcoef(recent[:-1], recent[1:])[0, 1] if len(recent) > 1 else 0
        
        # Trending: positive momentum, low mean reversion
        # Mean reverting: negative autocorrelation, high volatility
        if momentum > 0.01 and abs(autocorr) < 0.3:
            return "trending"
        elif autocorr < -0.2 or volatility > np.std(returns) * 1.5:
            return "mean_reverting"
        else:
            return "neutral"
    
    def regime_switching_weights(
        self,
        corr_matrix: np.ndarray,
        portfolio_returns: np.ndarray
    ) -> Dict[str, Dict[str, float]]:
        """
        Create regime-dependent weights.
        
        Returns weights for different regimes:
        - trending: Favor momentum strategies
        - mean_reverting: Favor mean reversion strategies
        """
        regime = self.regime_detection(portfolio_returns)
        
        # Classify strategies by type (if metadata available)
        momentum_strategies = []
        mean_reversion_strategies = []
        
        for i, strategy in enumerate(self.strategies):
            strategy_type = strategy.metadata.get("type", "unknown") if strategy.metadata else "unknown"
            if "momentum" in strategy_type.lower() or "trend" in strategy_type.lower():
                momentum_strategies.append(i)
            elif "mean" in strategy_type.lower() or "revert" in strategy_type.lower():
                mean_reversion_strategies.append(i)
        
        # Default: use all strategies if classification unavailable
        if not momentum_strategies and not mean_reversion_strategies:
            momentum_strategies = list(range(len(self.strategies)))
            mean_reversion_strategies = list(range(len(self.strategies)))
        
        weights_trending = self.sharpe_optimized_weights(corr_matrix)
        weights_mean_reverting = self.sharpe_optimized_weights(corr_matrix)
        
        # Adjust based on regime
        if regime == "trending":
            # Boost momentum strategies
            for i in momentum_strategies:
                name = self.strategies[i].name
                weights_trending[name] = weights_trending.get(name, 0) * 1.5
            # Reduce mean reversion
            for i in mean_reversion_strategies:
                name = self.strategies[i].name
                weights_mean_reverting[name] = weights_mean_reverting.get(name, 0) * 0.5
        elif regime == "mean_reverting":
            # Boost mean reversion strategies
            for i in mean_reversion_strategies:
                name = self.strategies[i].name
                weights_mean_reverting[name] = weights_mean_reverting.get(name, 0) * 1.5
            # Reduce momentum
            for i in momentum_strategies:
                name = self.strategies[i].name
                weights_trending[name] = weights_trending.get(name, 0) * 0.5
        
        # Normalize
        total_trending = sum(weights_trending.values())
        total_mean_reverting = sum(weights_mean_reverting.values())
        
        if total_trending > 0:
            weights_trending = {k: v / total_trending for k, v in weights_trending.items()}
        if total_mean_reverting > 0:
            weights_mean_reverting = {k: v / total_mean_reverting for k, v in weights_mean_reverting.items()}
        
        return {
            "trending": weights_trending,
            "mean_reverting": weights_mean_reverting,
            "neutral": self.sharpe_optimized_weights(corr_matrix)
        }
    
    def compute_portfolio_metrics(
        self,
        weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Compute portfolio-level performance metrics.
        
        Returns:
            Dictionary with sharpe, max_drawdown, volatility, total_return
        """
        # Get weight array
        weight_array = np.array([
            weights.get(s.name, 0.0) for s in self.strategies
        ])
        
        # Portfolio returns
        portfolio_returns = np.sum(
            [weight_array[i] * self.strategies[i].returns 
             for i in range(len(self.strategies))],
            axis=0
        )
        
        # Portfolio metrics
        total_return = np.prod(1 + portfolio_returns) - 1
        volatility = np.std(portfolio_returns) * np.sqrt(252)  # Annualized
        mean_return = np.mean(portfolio_returns) * 252  # Annualized
        
        sharpe = (mean_return - self.risk_free_rate) / volatility if volatility > 0 else 0
        
        # Max drawdown
        cumulative = np.cumprod(1 + portfolio_returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(np.min(drawdown))
        
        return {
            "sharpe": float(sharpe),
            "max_drawdown": float(max_drawdown),
            "volatility": float(volatility),
            "total_return": float(total_return)
        }
    
    def remove_harmful_strategies(
        self,
        initial_weights: Dict[str, float],
        threshold_improvement: float = 0.05
    ) -> Tuple[List[str], Dict[str, float]]:
        """
        Remove strategies that hurt the ensemble.
        
        Tests removing each strategy and keeps only those that improve Sharpe.
        """
        base_metrics = self.compute_portfolio_metrics(initial_weights)
        base_sharpe = base_metrics["sharpe"]
        
        # Test removing each strategy
        to_remove = []
        improved_weights = initial_weights.copy()
        
        for strategy in self.strategies:
            if strategy.name not in improved_weights:
                continue
            
            # Test without this strategy
            test_weights = improved_weights.copy()
            removed_weight = test_weights.pop(strategy.name)
            
            if not test_weights:
                continue
            
            # Renormalize
            total = sum(test_weights.values())
            if total > 0:
                test_weights = {k: v / total for k, v in test_weights.items()}
            else:
                continue
            
            # Compute metrics without this strategy
            test_metrics = self.compute_portfolio_metrics(test_weights)
            test_sharpe = test_metrics["sharpe"]
            
            # Remove if it improves Sharpe
            if test_sharpe > base_sharpe + threshold_improvement:
                to_remove.append(strategy.name)
                improved_weights = test_weights
                base_sharpe = test_sharpe
        
        return to_remove, improved_weights
    
    def build_ensemble(
        self,
        method: str = "sharpe_optimized",
        remove_harmful: bool = True,
        target_volatility: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Build the final ensemble.
        
        Args:
            method: Weighting method ('sharpe_optimized', 'volatility_adjusted', 'equal')
            remove_harmful: Whether to remove strategies that hurt performance
            target_volatility: Target portfolio volatility (for volatility_adjusted)
        
        Returns:
            Dictionary with ensemble configuration
        """
        if not self.strategies:
            raise ValueError("No strategies provided")
        
        # Compute correlation matrix
        corr_matrix = self.compute_correlation_matrix()
        
        # Get initial weights
        if method == "sharpe_optimized":
            weights = self.sharpe_optimized_weights(corr_matrix)
        elif method == "volatility_adjusted":
            weights = self.volatility_adjusted_weights(target_volatility)
        else:  # equal
            n = len(self.strategies)
            weights = {s.name: 1.0 / n for s in self.strategies}
        
        # Remove harmful strategies
        removed = []
        if remove_harmful:
            removed, weights = self.remove_harmful_strategies(weights)
        
        # Compute portfolio metrics
        portfolio_returns = np.sum(
            [weights.get(s.name, 0.0) * s.returns for s in self.strategies],
            axis=0
        )
        metrics = self.compute_portfolio_metrics(weights)
        
        # Regime switching weights
        regime_weights = self.regime_switching_weights(corr_matrix, portfolio_returns)
        current_regime = self.regime_detection(portfolio_returns)
        
        # Correlation dictionary (for output)
        correlations = {}
        strategy_names = [s.name for s in self.strategies]
        for i, name1 in enumerate(strategy_names):
            correlations[name1] = {}
            for j, name2 in enumerate(strategy_names):
                correlations[name1][name2] = float(corr_matrix[i, j])
        
        # Build output
        ensemble_members = [
            name for name in weights.keys() 
            if weights.get(name, 0) > 0.001  # Only include non-zero weights
        ]
        
        return {
            "ensemble_members": ensemble_members,
            "weights": {k: round(v, 4) for k, v in weights.items() if v > 0.001},
            "portfolio_sharpe": f"{metrics['sharpe']:.4f}",
            "portfolio_drawdown": f"{metrics['max_drawdown']:.4f}",
            "correlations": correlations,
            "regime_map": current_regime,
            "execution_rules": self._generate_execution_rules(
                weights, regime_weights, current_regime, removed
            )
        }
    
    def _generate_execution_rules(
        self,
        weights: Dict[str, float],
        regime_weights: Dict[str, Dict[str, float]],
        current_regime: str,
        removed: List[str]
    ) -> str:
        """Generate human-readable execution rules."""
        rules = []
        
        rules.append(f"Primary allocation method: Sharpe-optimized weights")
        rules.append(f"Current market regime: {current_regime}")
        
        if removed:
            rules.append(f"Removed strategies (harmful to ensemble): {', '.join(removed)}")
        
        rules.append("\nWeight allocation:")
        for name, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            if weight > 0.001:
                rules.append(f"  - {name}: {weight:.2%}")
        
        rules.append("\nRegime-based adjustments:")
        for regime, reg_weights in regime_weights.items():
            rules.append(f"  {regime}:")
            for name, weight in sorted(reg_weights.items(), key=lambda x: x[1], reverse=True):
                if weight > 0.001:
                    rules.append(f"    - {name}: {weight:.2%}")
        
        return "\n".join(rules)


def build_ensemble_from_backtests(
    backtest_results: List[Dict[str, Any]],
    method: str = "sharpe_optimized",
    risk_free_rate: float = 0.0,
    remove_harmful: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to build ensemble from backtest result dictionaries.
    
    Expected backtest_results format:
    [
        {
            "name": "strategy_name",
            "returns": [0.01, -0.02, 0.03, ...],  # List of period returns
            "sharpe": 1.5,
            "max_drawdown": 0.15,
            "volatility": 0.20,
            "total_return": 0.25,
            "metadata": {"type": "momentum"}  # Optional
        },
        ...
    ]
    """
    # Convert to StrategyBacktest objects
    strategies = []
    for result in backtest_results:
        strategies.append(StrategyBacktest(
            name=result["name"],
            returns=np.array(result["returns"]),
            sharpe=result.get("sharpe", 0.0),
            max_drawdown=result.get("max_drawdown", 0.0),
            volatility=result.get("volatility", 0.0),
            total_return=result.get("total_return", 0.0),
            win_rate=result.get("win_rate"),
            avg_win=result.get("avg_win"),
            avg_loss=result.get("avg_loss"),
            metadata=result.get("metadata", {})
        ))
    
    # Build ensemble
    builder = EnsembleBuilder(
        strategies=strategies,
        risk_free_rate=risk_free_rate
    )
    
    return builder.build_ensemble(method=method, remove_harmful=remove_harmful)


