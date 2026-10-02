"""Indicator parameter definitions and utilities for Strategy Lab"""

from typing import Any
from .schemas import IndicatorDefinition, IndicatorParameter, IndicatorInput, IndicatorOutput, IndicatorCategory, BUILT_IN_INDICATORS


def get_indicator_by_id(indicator_id: str) -> IndicatorDefinition | None:
    """Get indicator definition by ID"""
    for indicator in BUILT_IN_INDICATORS:
        if indicator.id == indicator_id:
            return indicator
    return None


def get_indicators_by_category(category: IndicatorCategory) -> list[IndicatorDefinition]:
    """Get all indicators in a category"""
    return [i for i in BUILT_IN_INDICATORS if i.category == category]


def list_indicator_ids() -> list[str]:
    """List all available indicator IDs"""
    return [i.id for i in BUILT_IN_INDICATORS]


def validate_indicator_params(indicator_id: str, params: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate parameters for an indicator"""
    indicator = get_indicator_by_id(indicator_id)
    if not indicator:
        return False, [f"Unknown indicator: {indicator_id}"]

    errors = []
    for param in indicator.parameters:
        value = params.get(param.name)
        
        if param.required and value is None:
            errors.append(f"Required parameter missing: {param.name}")
            continue
            
        if value is None:
            continue
            
        if param.type == "integer":
            if not isinstance(value, int):
                errors.append(f"Parameter {param.name} must be an integer")
            elif param.min is not None and value < param.min:
                errors.append(f"Parameter {param.name} must be >= {param.min}")
            elif param.max is not None and value > param.max:
                errors.append(f"Parameter {param.name} must be <= {param.max}")
                
        elif param.type == "number":
            if not isinstance(value, (int, float)):
                errors.append(f"Parameter {param.name} must be a number")
            elif param.min is not None and value < param.min:
                errors.append(f"Parameter {param.name} must be >= {param.min}")
            elif param.max is not None and value > param.max:
                errors.append(f"Parameter {param.name} must be <= {param.max}")
                
        elif param.type == "select":
            if param.options and value not in param.options:
                errors.append(f"Parameter {param.name} must be one of: {', '.join(param.options)}")

    return len(errors) == 0, errors


# Default parameters for each indicator
DEFAULT_INDICATOR_PARAMS: dict[str, dict[str, Any]] = {
    "sma": {"period": 20},
    "ema": {"period": 20},
    "rsi": {"period": 14},
    "macd": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
    "atr": {"period": 14},
    "bollinger_bands": {"period": 20, "std_dev": 2.0},
}


def get_default_params(indicator_id: str) -> dict[str, Any]:
    """Get default parameters for an indicator"""
    return DEFAULT_INDICATOR_PARAMS.get(indicator_id, {})


def merge_params(indicator_id: str, user_params: dict[str, Any]) -> dict[str, Any]:
    """Merge user parameters with defaults"""
    defaults = get_default_params(indicator_id)
    merged = defaults.copy()
    merged.update(user_params)
    return merged