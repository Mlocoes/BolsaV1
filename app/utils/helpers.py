"""
Utilidades de Formateo y Helpers

Este módulo contiene funciones utilitarias para formatear datos y
otras operaciones auxiliares.
"""

import pandas as pd
from typing import Union, Optional
from datetime import datetime, date


def format_currency(valor: Union[float, int], simbolo: str = "$") -> str:
    """
    Formatea un valor monetario
    
    Args:
        valor: Valor a formatear
        simbolo: Símbolo de moneda
        
    Returns:
        str: Valor formateado como moneda
    """
    try:
        return f"{simbolo}{valor:,.2f}"
    except (ValueError, TypeError):
        return f"{simbolo}0.00"


def format_percentage(valor: Union[float, int], decimales: int = 2) -> str:
    """
    Formatea un valor como porcentaje
    
    Args:
        valor: Valor a formatear
        decimales: Número de decimales
        
    Returns:
        str: Valor formateado como porcentaje
    """
    try:
        return f"{valor:.{decimales}f}%"
    except (ValueError, TypeError):
        return "0.00%"


def format_number(valor: Union[float, int], decimales: int = 0) -> str:
    """
    Formatea un número con separadores de miles
    
    Args:
        valor: Valor a formatear
        decimales: Número de decimales
        
    Returns:
        str: Número formateado
    """
    try:
        if decimales == 0:
            return f"{int(valor):,}"
        else:
            return f"{valor:,.{decimales}f}"
    except (ValueError, TypeError):
        return "0"


def format_date(fecha: Union[datetime, date, str], formato: str = "%Y-%m-%d") -> str:
    """
    Formatea una fecha
    
    Args:
        fecha: Fecha a formatear
        formato: Formato de salida
        
    Returns:
        str: Fecha formateada
    """
    try:
        if isinstance(fecha, str):
            # Intentar parsear la fecha
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        elif isinstance(fecha, datetime):
            fecha = fecha.date()
        
        return fecha.strftime(formato)
    except (ValueError, TypeError, AttributeError):
        return str(fecha) if fecha else "N/A"


def get_color_for_value(valor: Union[float, int], positivo_es_bueno: bool = True) -> str:
    """
    Retorna un color basado en el valor (positivo/negativo)
    
    Args:
        valor: Valor a evaluar
        positivo_es_bueno: Si True, positivo es verde, negativo es rojo
        
    Returns:
        str: Color en formato Streamlit
    """
    try:
        if valor > 0:
            return "normal" if positivo_es_bueno else "inverse"
        elif valor < 0:
            return "inverse" if positivo_es_bueno else "normal"
        else:
            return "normal"
    except (ValueError, TypeError):
        return "normal"


def get_icon_for_trend(valor: Union[float, int]) -> str:
    """
    Retorna un ícono basado en la tendencia del valor
    
    Args:
        valor: Valor a evaluar
        
    Returns:
        str: Ícono emoji
    """
    try:
        if valor > 0:
            return "📈"
        elif valor < 0:
            return "📉"
        else:
            return "➡️"
    except (ValueError, TypeError):
        return "➡️"


def safe_float_conversion(valor: any, default: float = 0.0) -> float:
    """
    Convierte un valor a float de manera segura
    
    Args:
        valor: Valor a convertir
        default: Valor por defecto si falla la conversión
        
    Returns:
        float: Valor convertido o default
    """
    try:
        return float(valor)
    except (ValueError, TypeError):
        return default


def safe_int_conversion(valor: any, default: int = 0) -> int:
    """
    Convierte un valor a int de manera segura
    
    Args:
        valor: Valor a convertir
        default: Valor por defecto si falla la conversión
        
    Returns:
        int: Valor convertido o default
    """
    try:
        return int(valor)
    except (ValueError, TypeError):
        return default


def calculate_percentage_change(valor_inicial: float, valor_final: float) -> float:
    """
    Calcula el cambio porcentual entre dos valores
    
    Args:
        valor_inicial: Valor inicial
        valor_final: Valor final
        
    Returns:
        float: Cambio porcentual
    """
    try:
        if valor_inicial == 0:
            return 0.0
        return ((valor_final - valor_inicial) / valor_inicial) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


def validate_ticker_format(ticker: str) -> bool:
    """
    Valida que un ticker tenga el formato correcto
    
    Args:
        ticker: Ticker a validar
        
    Returns:
        bool: True si el formato es válido
    """
    if not isinstance(ticker, str):
        return False
    
    ticker = ticker.strip().upper()
    
    # Debe tener entre 1 y 5 caracteres alfabéticos
    return ticker.isalpha() and 1 <= len(ticker) <= 5


def truncate_string(texto: str, longitud: int = 50, sufijo: str = "...") -> str:
    """
    Trunca una cadena si excede la longitud máxima
    
    Args:
        texto: Texto a truncar
        longitud: Longitud máxima
        sufijo: Sufijo a agregar si se trunca
        
    Returns:
        str: Texto truncado si es necesario
    """
    if not isinstance(texto, str):
        texto = str(texto)
    
    if len(texto) <= longitud:
        return texto
    
    return texto[:longitud - len(sufijo)] + sufijo


def create_summary_stats(values: list) -> dict:
    """
    Crea estadísticas resumidas de una lista de valores
    
    Args:
        values: Lista de valores numéricos
        
    Returns:
        dict: Estadísticas resumidas
    """
    try:
        if not values:
            return {
                'count': 0,
                'mean': 0,
                'median': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'sum': 0
            }
        
        df = pd.Series(values)
        return {
            'count': len(values),
            'mean': df.mean(),
            'median': df.median(),
            'std': df.std(),
            'min': df.min(),
            'max': df.max(),
            'sum': df.sum()
        }
    except Exception:
        return {
            'count': 0,
            'mean': 0,
            'median': 0,
            'std': 0,
            'min': 0,
            'max': 0,
            'sum': 0
        }