"""
Servicio de Cotizaciones

Este módulo contiene la lógica de negocio para obtener cotizaciones de activos
financieros desde Yahoo Finance con sistema de cache y fallback a BD.
"""

import logging
import time
import random
import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from ..models import SessionLocal, Ativo, PrecoDiario
from ..utils import Config

# Configurar logger
logger = logging.getLogger(__name__)

# Cache global para cotizaciones (en memoria)
cotizacoes_cache = {}
cache_config = Config.get_cache_config()
cache_timeout = cache_config['timeout']


class CotacaoService:
    """Servicio para obtener cotizaciones de activos financieros"""
    
    @staticmethod
    def limpar_cache_antigo():
        """Limpia entradas de cache expiradas"""
        global cotizacoes_cache
        agora = datetime.now()
        keys_expiradas = []
        
        for key, (timestamp, _) in cotizacoes_cache.items():
            if (agora - timestamp).seconds > cache_timeout:
                keys_expiradas.append(key)
        
        for key in keys_expiradas:
            del cotizacoes_cache[key]
        
        if keys_expiradas:
            logger.info(f"Limpeza de cache: {len(keys_expiradas)} entradas removidas")
    
    @staticmethod
    def obter_ultima_cotacao_bd(ticker: str) -> Optional[dict]:
        """
        Obtiene la última cotización guardada en BD como fallback
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            Optional[dict]: Datos de cotización desde BD o None
        """
        session = SessionLocal()
        try:
            # Buscar el ativo por ticker
            ativo = session.query(Ativo).filter(Ativo.ticker == ticker).first()
            if not ativo:
                logger.warning(f"Ativo não encontrado para ticker {ticker}")
                return None
            
            # Buscar el precio más reciente
            ultimo_preco = session.query(PrecoDiario).filter(
                PrecoDiario.ativo_id == ativo.id
            ).order_by(PrecoDiario.data.desc()).first()
            
            if not ultimo_preco:
                logger.warning(f"Nenhum preço histórico encontrado para {ticker}")
                return None
            
            # Buscar precio anterior para calcular variación
            preco_anterior = session.query(PrecoDiario).filter(
                PrecoDiario.ativo_id == ativo.id,
                PrecoDiario.data < ultimo_preco.data
            ).order_by(PrecoDiario.data.desc()).first()
            
            preco_anterior_valor = float(preco_anterior.preco_fechamento) if preco_anterior else float(ultimo_preco.preco_fechamento)
            
            logger.info(f"Usando última cotação da BD para {ticker}: {ultimo_preco.preco_fechamento} ({ultimo_preco.data})")
            
            return {
                'ticker': ticker,
                'preco_atual': float(ultimo_preco.preco_fechamento),
                'abertura': float(ultimo_preco.preco_fechamento),  # Aproximación
                'fechamento_anterior': preco_anterior_valor,
                'variacao_dia': float(ultimo_preco.preco_fechamento) - preco_anterior_valor,
                'variacao_pct': round(((float(ultimo_preco.preco_fechamento) - preco_anterior_valor) / preco_anterior_valor) * 100, 2) if preco_anterior_valor > 0 else 0,
                'volume': 0,  # Não temos volume histórico
                'data': ultimo_preco.data,
                'fonte': 'BD_FALLBACK'  # Indicador de que é fallback
            }
        except Exception as e:
            logger.error(f"Erro ao obter última cotação da BD para {ticker}: {e}", exc_info=True)
            return None
        finally:
            session.close()
    
    @staticmethod
    def obter_cotacao_atual(ticker: str) -> Optional[dict]:
        """
        Obtiene la cotización actual de un ticker con fallback a BD
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            Optional[dict]: Datos de cotización o None
        """
        # Limpiar cache expirado
        CotacaoService.limpar_cache_antigo()
        
        # Verificar cache primero
        cache_key = f"{ticker}_{datetime.now().strftime('%Y%m%d_%H%M')}"  # Cache por ticker y hora
        if cache_key in cotizacoes_cache:
            cached_time, cached_data = cotizacoes_cache[cache_key]
            if (datetime.now() - cached_time).seconds < cache_timeout:
                logger.info(f"Usando cotação em cache para {ticker}")
                cached_data['fonte'] = 'CACHE_LOCAL'
                return cached_data
        
        logger.info(f"Obtendo cotação para {ticker}")
        
        try:
            # Rate limiting: delay aleatorio para evitar exceso de requests
            yahoo_config = Config.get_yahoo_config()
            delay = random.uniform(yahoo_config['delay_min'], yahoo_config['delay_max'])
            time.sleep(delay)
            
            stock = yf.Ticker(ticker)
            
            # Usar timeout más bajo y menos datos para reducir rate limiting
            hist = stock.history(period="5d", timeout=yahoo_config['timeout'])
            
            if hist.empty:
                logger.warning(f"Histórico vazio do Yahoo Finance para {ticker}")
                raise Exception("Histórico vazio")
            
            ultimo = hist.iloc[-1]
            anterior = hist.iloc[-2] if len(hist) > 1 else ultimo
            
            cotacao = {
                'ticker': ticker,
                'preco_atual': round(ultimo['Close'], 4),
                'abertura': round(ultimo['Open'], 4),
                'fechamento_anterior': round(anterior['Close'], 4),
                'variacao_dia': round(ultimo['Close'] - anterior['Close'], 4),
                'variacao_pct': round(((ultimo['Close'] - anterior['Close']) / anterior['Close']) * 100, 2),
                'volume': int(ultimo['Volume']),
                'data': ultimo.name.date(),
                'fonte': 'YAHOO_FINANCE'
            }
            
            # Guardar en cache exitoso
            cotizacoes_cache[cache_key] = (datetime.now(), cotacao)
            
            logger.info(f"Cotação obtida do Yahoo Finance para {ticker}: {cotacao['preco_atual']}")
            return cotacao
            
        except Exception as e:
            logger.warning(f"Erro no Yahoo Finance para {ticker}: {e}. Tentando fallback da BD...")
            
            # Fallback: usar última cotação da BD
            cotacao_bd = CotacaoService.obter_ultima_cotacao_bd(ticker)
            if cotacao_bd:
                st.info(f"📊 {ticker}: Usando cotización de BD ({cotacao_bd['data']}) - API temporalmente limitada")
                return cotacao_bd
            else:
                logger.error(f"Falha total ao obter cotação para {ticker}")
                # Crear una cotización de emergencia
                st.error(f"❌ No hay conexión. Usando valores por defecto para {ticker}")
                return {
                    'ticker': ticker,
                    'preco_atual': 100.00,  # Valor por defecto
                    'abertura': 100.00,
                    'fechamento_anterior': 100.00,
                    'variacao_dia': 0.00,
                    'variacao_pct': 0.00,
                    'volume': 0,
                    'data': datetime.now().date(),
                    'fonte': 'VALOR_PADRAO'
                }
    
    @staticmethod
    def obter_historico(ticker: str, dias: int = 30) -> pd.DataFrame:
        """
        Obtiene el histórico de precios de un ticker
        
        Args:
            ticker: Símbolo del ticker
            dias: Número de días de histórico
            
        Returns:
            pd.DataFrame: DataFrame con el histórico de precios
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{dias}d")
            return hist
        except Exception as e:
            logger.error(f"Erro ao obter histórico para {ticker}: {e}")
            return pd.DataFrame()  # DataFrame vacío en caso de error
    
    @staticmethod
    def salvar_preco_diario(ativo_id: int, ticker: str) -> bool:
        """
        Guarda el precio diario actual en la BD
        
        Args:
            ativo_id: ID del activo
            ticker: Símbolo del ticker
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        session = SessionLocal()
        try:
            # Obtener cotización actual
            cotacao = CotacaoService.obter_cotacao_atual(ticker)
            if not cotacao:
                logger.warning(f"Não foi possível obter cotação para salvar preço de {ticker}")
                return False
            
            # Verificar si ya existe precio para hoy
            hoje = datetime.now().date()
            preco_existente = session.query(PrecoDiario).filter(
                PrecoDiario.ativo_id == ativo_id,
                PrecoDiario.data == hoje
            ).first()
            
            if preco_existente:
                # Actualizar precio existente
                preco_existente.preco_fechamento = cotacao['preco_atual']
                logger.info(f"Preço atualizado para {ticker}: {cotacao['preco_atual']}")
            else:
                # Crear nuevo registro
                novo_preco = PrecoDiario(
                    ativo_id=ativo_id,
                    data=hoje,
                    preco_fechamento=cotacao['preco_atual']
                )
                session.add(novo_preco)
                logger.info(f"Novo preço salvo para {ticker}: {cotacao['preco_atual']}")
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao salvar preço diário para {ticker}: {e}", exc_info=True)
            return False
        finally:
            session.close()