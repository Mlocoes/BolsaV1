"""
Módulo de Utilidades

Este módulo contiene utilidades generales y configuraciones para BolsaV1.
"""

from .config import Config, KNOWN_TICKERS, DEV_CONFIG, PROD_CONFIG
from .database import init_database, test_connection
from .logging_config import setup_logging, get_logger
from .helpers import (
    format_currency,
    format_percentage,
    format_number,
    format_date,
    get_color_for_value,
    get_icon_for_trend,
    safe_float_conversion,
    safe_int_conversion,
    calculate_percentage_change,
    validate_ticker_format,
    truncate_string,
    create_summary_stats
)

# Exportar todas las utilidades
__all__ = [
    'Config',
    'KNOWN_TICKERS',
    'DEV_CONFIG',
    'PROD_CONFIG',
    'init_database',
    'test_connection',
    'setup_logging',
    'get_logger',
    'format_currency',
    'format_percentage',
    'format_number',
    'format_date',
    'get_color_for_value',
    'get_icon_for_trend',
    'safe_float_conversion',
    'safe_int_conversion',
    'calculate_percentage_change',
    'validate_ticker_format',
    'truncate_string',
    'create_summary_stats'
]