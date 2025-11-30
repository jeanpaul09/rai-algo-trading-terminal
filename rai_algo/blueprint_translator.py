"""
Strategy Blueprint Translator

Converts Strategy Blueprint JSON into production-ready Python strategy code.
"""

import json
from typing import Dict, Any, List
from pathlib import Path
from decimal import Decimal


class BlueprintTranslator:
    """
    Translates Strategy Blueprint JSON into Python strategy code.
    
    Expected Blueprint Structure:
    {
        "name": "strategy_name",
        "description": "Strategy description",
        "parameters": {
            "param1": value1,
            ...
        },
        "indicators": [
            {
                "name": "indicator_name",
                "type": "SMA|EMA|RSI|MACD|...",
                "params": {...}
            }
        ],
        "entry_rules": {
            "long": ["condition1", "condition2"],
            "short": ["condition1", "condition2"]
        },
        "exit_rules": {
            "long": ["condition1"],
            "short": ["condition1"]
        },
        "risk_management": {
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.05,
            "max_position_size": 0.1,
            "risk_per_trade": 0.02
        }
    }
    """
    
    INDICATOR_TEMPLATES = {
        "SMA": """
    def calculate_{name}(self, prices: List[Decimal], period: int) -> Decimal:
        \"\"\"Calculate {name} Simple Moving Average.\"\"\"
        if len(prices) < period:
            return Decimal("0")
        return sum(prices[-period:]) / Decimal(period)
""",
        "EMA": """
    def calculate_{name}(self, prices: List[Decimal], period: int, previous_ema: Optional[Decimal] = None) -> Decimal:
        \"\"\"Calculate {name} Exponential Moving Average.\"\"\"
        if len(prices) < period:
            return Decimal("0")
        multiplier = Decimal("2") / Decimal(period + 1)
        if previous_ema is None:
            sma = sum(prices[-period:]) / Decimal(period)
            return sma
        current_price = prices[-1]
        ema = (current_price - previous_ema) * multiplier + previous_ema
        return ema
""",
        "RSI": """
    def calculate_{name}(self, prices: List[Decimal], period: int = 14) -> Decimal:
        \"\"\"Calculate {name} Relative Strength Index.\"\"\"
        if len(prices) < period + 1:
            return Decimal("50")  # Neutral RSI
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else Decimal("0") for d in deltas[-period:]]
        losses = [-d if d < 0 else Decimal("0") for d in deltas[-period:]]
        avg_gain = sum(gains) / Decimal(period)
        avg_loss = sum(losses) / Decimal(period)
        if avg_loss == 0:
            return Decimal("100")
        rs = avg_gain / avg_loss
        rsi = Decimal("100") - (Decimal("100") / (Decimal("1") + rs))
        return rsi
""",
    }
    
    def __init__(self, blueprint: Dict[str, Any]):
        """
        Initialize translator with blueprint.
        
        Args:
            blueprint: Strategy blueprint dictionary
        """
        self.blueprint = blueprint
        self.validate_blueprint()
    
    def validate_blueprint(self) -> None:
        """Validate blueprint structure."""
        required_keys = ["name"]
        for key in required_keys:
            if key not in self.blueprint:
                raise ValueError(f"Blueprint missing required key: {key}")
    
    def translate(self) -> str:
        """
        Translate blueprint to Python code.
        
        Returns:
            Complete Python strategy code as string
        """
        strategy_name = self.blueprint["name"]
        class_name = self._to_class_name(strategy_name)
        
        code_parts = [
            self._generate_header(),
            self._generate_imports(),
            self._generate_indicator_functions(),
            self._generate_strategy_class(class_name),
        ]
        
        return "\n\n".join(code_parts)
    
    def _to_class_name(self, name: str) -> str:
        """Convert strategy name to class name."""
        return "".join(word.capitalize() for word in name.replace("_", " ").replace("-", " ").split())
    
    def _generate_header(self) -> str:
        """Generate file header with docstring."""
        description = self.blueprint.get("description", "Trading strategy generated from blueprint")
        return f'''"""
{description}

This strategy was automatically generated from a Strategy Blueprint.
"""

from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional

from rai_algo.base import (
    BaseStrategy,
    MarketData,
    IndicatorResult,
    Signal,
    SignalType,
    Position,
)'''
    
    def _generate_imports(self) -> str:
        """Generate imports (already in header)."""
        return ""
    
    def _generate_indicator_functions(self) -> str:
        """Generate indicator calculation functions."""
        indicators = self.blueprint.get("indicators", [])
        functions = []
        
        for indicator in indicators:
            ind_type = indicator.get("type", "").upper()
            ind_name = indicator.get("name", "indicator")
            
            if ind_type in self.INDICATOR_TEMPLATES:
                template = self.INDICATOR_TEMPLATES[ind_type]
                functions.append(template.format(name=ind_name))
            else:
                # Generic indicator placeholder
                functions.append(f'''
    def calculate_{ind_name}(self, market_data: List[MarketData]) -> Decimal:
        \"\"\"Calculate {ind_name} indicator.\"\"\"
        # TODO: Implement {ind_type} indicator logic
        return Decimal("0")
''')
        
        return "\n".join(functions) if functions else ""
    
    def _generate_strategy_class(self, class_name: str) -> str:
        """Generate strategy class code."""
        parts = [
            f"class {class_name}(BaseStrategy):",
            f'    """{self.blueprint.get("description", "Generated strategy")}"""',
            "",
            self._generate_init(),
            self._generate_calculate_indicators(),
            self._generate_generate_signal(),
        ]
        
        return "\n".join(parts)
    
    def _generate_init(self) -> str:
        """Generate __init__ method."""
        params = self.blueprint.get("parameters", {})
        risk_mgmt = self.blueprint.get("risk_management", {})
        
        init_params = []
        for key, value in params.items():
            if isinstance(value, (int, float)):
                init_params.append(f"        {key}: {type(value).__name__} = {value}")
            elif isinstance(value, str):
                init_params.append(f'        {key}: str = "{value}"')
            else:
                init_params.append(f"        {key} = {value}")
        
        risk_params = []
        if "stop_loss_pct" in risk_mgmt:
            risk_params.append(f'stop_loss_pct=Decimal("{risk_mgmt["stop_loss_pct"]}")')
        if "take_profit_pct" in risk_mgmt:
            risk_params.append(f'take_profit_pct=Decimal("{risk_mgmt["take_profit_pct"]}")')
        if "max_position_size" in risk_mgmt:
            risk_params.append(f'max_position_size=Decimal("{risk_mgmt["max_position_size"]}")')
        
        risk_kwargs = ", ".join(risk_params) if risk_params else ""
        
        # Build init params string (avoid backslash in f-string)
        init_params_str = ",\n".join(init_params) if init_params else "        **kwargs"
        param_assignments = self._generate_param_assignments(params)
        
        return f'''    def __init__(
        self,
{init_params_str}
    ):
        """
        Initialize {self.blueprint["name"]} strategy.
        """
        super().__init__(
            name="{self.blueprint["name"]}",
{risk_kwargs if risk_kwargs else ""}
            **kwargs
        )
        # Store parameters
{param_assignments}'''
    
    def _generate_param_assignments(self, params: Dict[str, Any]) -> str:
        """Generate parameter assignment statements."""
        assignments = []
        for key, value in params.items():
            if isinstance(value, str):
                assignments.append(f'        self.{key} = "{value}"')
            else:
                assignments.append(f"        self.{key} = {value}")
        return "\n".join(assignments) if assignments else "        pass"
    
    def _generate_calculate_indicators(self) -> str:
        """Generate calculate_indicators method."""
        indicators = self.blueprint.get("indicators", [])
        
        if not indicators:
            return '''    def calculate_indicators(self, market_data: List[MarketData]) -> Dict[str, IndicatorResult]:
        """
        Calculate technical indicators.
        
        Args:
            market_data: Historical market data
            
        Returns:
            Dictionary of indicator name -> IndicatorResult
        """
        # TODO: Implement indicator calculations
        return {}'''
        
        code = '''    def calculate_indicators(self, market_data: List[MarketData]) -> Dict[str, IndicatorResult]:
        """
        Calculate technical indicators.
        
        Args:
            market_data: Historical market data
            
        Returns:
            Dictionary of indicator name -> IndicatorResult
        """
        if not market_data:
            return {}
        
        closes = [md.close for md in market_data]
        timestamp = market_data[-1].timestamp
        
        indicators = {}
'''
        
        for indicator in indicators:
            ind_name = indicator.get("name", "indicator")
            ind_type = indicator.get("type", "").upper()
            ind_params = indicator.get("params", {})
            
            if ind_type == "SMA":
                period = ind_params.get("period", 14)
                code += f'''        # Calculate {ind_name} (SMA)
        if len(closes) >= {period}:
            indicators["{ind_name}"] = IndicatorResult(
                value=self.calculate_{ind_name}(closes, {period}),
                timestamp=timestamp,
                metadata={{"type": "SMA", "period": {period}}}
            )
        else:
            indicators["{ind_name}"] = IndicatorResult(
                value=Decimal("0"),
                timestamp=timestamp
            )
'''
            elif ind_type == "EMA":
                period = ind_params.get("period", 14)
                code += f'''        # Calculate {ind_name} (EMA)
        if len(closes) >= {period}:
            prev_ema = getattr(self, "prev_ema_{ind_name}", None)
            ema_value = self.calculate_{ind_name}(closes, {period}, prev_ema)
            setattr(self, "prev_ema_{ind_name}", ema_value)
            indicators["{ind_name}"] = IndicatorResult(
                value=ema_value,
                timestamp=timestamp,
                metadata={{"type": "EMA", "period": {period}}}
            )
        else:
            indicators["{ind_name}"] = IndicatorResult(
                value=Decimal("0"),
                timestamp=timestamp
            )
'''
            elif ind_type == "RSI":
                period = ind_params.get("period", 14)
                code += f'''        # Calculate {ind_name} (RSI)
        if len(closes) >= {period} + 1:
            indicators["{ind_name}"] = IndicatorResult(
                value=self.calculate_{ind_name}(closes, {period}),
                timestamp=timestamp,
                metadata={{"type": "RSI", "period": {period}}}
            )
        else:
            indicators["{ind_name}"] = IndicatorResult(
                value=Decimal("50"),
                timestamp=timestamp
            )
'''
            else:
                code += f'''        # Calculate {ind_name} ({ind_type})
        indicators["{ind_name}"] = IndicatorResult(
            value=self.calculate_{ind_name}(market_data),
            timestamp=timestamp,
            metadata={{"type": "{ind_type}"}}
        )
'''
        
        code += "        return indicators"
        return code
    
    def _generate_generate_signal(self) -> str:
        """Generate generate_signal method."""
        entry_rules = self.blueprint.get("entry_rules", {})
        exit_rules = self.blueprint.get("exit_rules", {})
        
        code = '''    def generate_signal(
        self,
        market_data: List[MarketData],
        indicators: Dict[str, IndicatorResult],
        current_position: Optional[Position]
    ) -> Signal:
        """
        Generate trading signal based on entry/exit rules.
        
        Args:
            market_data: Historical market data
            indicators: Calculated indicators
            current_position: Current position (if any)
            
        Returns:
            Trading signal
        """
        if not market_data:
            return Signal(
                signal_type=SignalType.HOLD,
                timestamp=datetime.now(),
                symbol="",
                price=Decimal("0"),
                confidence=Decimal("0"),
                reason="No market data"
            )
        
        current_price = market_data[-1].close
        symbol = market_data[-1].symbol
        timestamp = market_data[-1].timestamp
        
        # Check exit rules first if we have a position
        if current_position:
'''
        
        # Exit rules
        if exit_rules.get("long"):
            code += f'''            if current_position.is_long:
                # Exit long conditions:
                # {", ".join(exit_rules["long"])}
                # TODO: Implement exit logic for long positions
                pass
'''
        
        if exit_rules.get("short"):
            code += f'''            if current_position.is_short:
                # Exit short conditions:
                # {", ".join(exit_rules["short"])}
                # TODO: Implement exit logic for short positions
                pass
'''
        
        # Entry rules
        code += '''
        # Entry rules (only if no position)
        if not current_position:
'''
        
        if entry_rules.get("long"):
            code += f'''            # Long entry conditions:
            # {", ".join(entry_rules["long"])}
            # TODO: Implement long entry logic
            # Example:
            # if condition1 and condition2:
            #     return Signal(
            #         signal_type=SignalType.BUY,
            #         timestamp=timestamp,
            #         symbol=symbol,
            #         price=current_price,
            #         confidence=Decimal("0.7"),
            #         reason="Entry conditions met"
            #     )
'''
        
        if entry_rules.get("short"):
            code += f'''            # Short entry conditions:
            # {", ".join(entry_rules["short"])}
            # TODO: Implement short entry logic
'''
        
        code += '''
        # Default: hold
        return Signal(
            signal_type=SignalType.HOLD,
            timestamp=timestamp,
            symbol=symbol,
            price=current_price,
            confidence=Decimal("0"),
            reason="No entry/exit conditions met"
        )'''
        
        return code
    
    def save_strategy(self, output_path: Path) -> None:
        """
        Save translated strategy to file.
        
        Args:
            output_path: Path to save strategy file
        """
        code = self.translate()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code, encoding="utf-8")
        print(f"Strategy saved to: {output_path}")


def translate_blueprint(blueprint_path: str, output_path: str) -> None:
    """
    Translate a blueprint JSON file to a strategy Python file.
    
    Args:
        blueprint_path: Path to blueprint JSON file
        output_path: Path to save generated strategy file
    """
    with open(blueprint_path, "r") as f:
        blueprint = json.load(f)
    
    translator = BlueprintTranslator(blueprint)
    translator.save_strategy(Path(output_path))


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python blueprint_translator.py <blueprint.json> <output.py>")
        sys.exit(1)
    
    translate_blueprint(sys.argv[1], sys.argv[2])


