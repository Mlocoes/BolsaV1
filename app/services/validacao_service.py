"""
Servicio de Validación

Este módulo contiene la lógica para validar tickers y activos financieros.
"""

import logging
import time
import random
import yfinance as yf
from ..utils import KNOWN_TICKERS, Config

# Configurar logger
logger = logging.getLogger(__name__)


def validar_ticker(ticker: str) -> dict:
    """
    Valida que un ticker existe en Yahoo Finance y retorna información básica
    
    Args:
        ticker: Símbolo del ticker a validar
        
    Returns:
        dict: Resultado de la validación con campos:
            - valido: bool
            - nome: str (nombre del activo)
            - ticker: str (ticker normalizado)
            - fonte: str (fuente de validación)
            - warning: str (opcional, advertencias)
            - erro: str (opcional, errores)
    """
    try:
        logger.info(f"Validando ticker: {ticker}")
        
        # Usar tickers conocidos de la configuración
        tickers_conhecidos = KNOWN_TICKERS
        
        # Normalizar ticker
        ticker_upper = ticker.upper()
        
        # Si es un nombre conocido, convertir a ticker
        if ticker_upper in tickers_conhecidos:
            if len(ticker_upper) > 5:  # Probablemente es un nombre, no ticker
                ticker_real = tickers_conhecidos[ticker_upper]
                if ticker_real in tickers_conhecidos:
                    return {
                        'valido': True,
                        'nome': tickers_conhecidos[ticker_real],
                        'ticker': ticker_real,
                        'fonte': 'LISTA_CONOCIDA'
                    }
        
        # Validación offline para tickers conocidos
        if ticker_upper in tickers_conhecidos:
            logger.info(f"Ticker {ticker_upper} encontrado en lista conocida")
            return {
                'valido': True,
                'nome': tickers_conhecidos[ticker_upper],
                'ticker': ticker_upper,
                'fonte': 'LISTA_CONOCIDA'
            }
        
        # Intentar validación online (con rate limiting)
        yahoo_config = Config.get_yahoo_config()
        delay = random.uniform(yahoo_config['delay_min'], yahoo_config['delay_max'])
        time.sleep(delay)
        
        stock = yf.Ticker(ticker_upper)
        info = stock.info
        
        # Verificar que tengamos información válida
        if not info or 'regularMarketPrice' not in info:
            hist = stock.history(period="1d", timeout=yahoo_config['timeout'])
            if hist.empty:
                logger.warning(f"Ticker {ticker_upper} não retornou dados válidos")
                # Para tickers desconocidos, permitir agregar manualmente
                return {
                    'valido': True,  # Permitir agregar
                    'nome': f'{ticker_upper} (Validação manual)',
                    'ticker': ticker_upper,
                    'fonte': 'MANUAL',
                    'warning': 'Ticker no validado online - se agregará como manual'
                }
        
        nome = info.get('longName') or info.get('shortName') or ticker_upper
        logger.info(f"Ticker {ticker_upper} válido online: {nome}")
        
        return {
            'valido': True,
            'nome': nome,
            'ticker': ticker_upper,
            'fonte': 'YAHOO_FINANCE',
            'info': info
        }
        
    except Exception as e:
        logger.warning(f"Erro na validação do ticker {ticker}: {e}")
        
        # Fallback: permitir agregar ticker manualmente si no se puede validar
        ticker_upper = ticker.upper()
        
        # Verificar si es un formato de ticker válido (1-5 letras mayúsculas)
        if ticker_upper.isalpha() and 1 <= len(ticker_upper) <= 5:
            logger.info(f"Permitindo adicionar {ticker_upper} manualmente due to validation error")
            return {
                'valido': True,
                'nome': f'{ticker_upper} (Adicionado manualmente)',
                'ticker': ticker_upper,
                'fonte': 'MANUAL_FALLBACK',
                'warning': f'No se pudo validar online: {str(e)[:100]}...'
            }
        
        return {
            'valido': False,
            'erro': f'Formato de ticker inválido o error de conexión: {str(e)[:100]}...'
        }