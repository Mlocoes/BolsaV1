"""
Servicio de Cotizaciones - Multi-Usuario (FASE 3)

Este módulo contiene la lógica de negocio para obtener cotizaciones de activos
financieros con soporte multi-usuario y cache personalizado por usuario.
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
from ..utils.auth import StreamlitAuth
from ..utils.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)

# Cache global para cotizaciones (en memoria) - organizado por usuario
cotizacoes_cache = {}
cache_config = Config.get_cache_config()
cache_timeout = cache_config['timeout']


class CotacaoService:
    """Servicio para obtener cotizaciones de activos financieros con soporte multi-usuario"""
    
    @staticmethod
    def _get_current_user_id() -> int:
        """
        Obtiene el ID del usuario actual autenticado
        
        Returns:
            int: ID del usuario actual
            
        Raises:
            Exception: Si no hay usuario autenticado
        """
        if not StreamlitAuth.is_authenticated():
            raise Exception("Usuario no autenticado")
        
        user = StreamlitAuth.get_current_user()
        if not user:
            raise Exception("No se pudo obtener información del usuario")
        
        return user['id']
    
    @staticmethod
    def limpar_cache_antigo():
        """Limpia entradas de cache expiradas para todos los usuarios"""
        global cotizacoes_cache
        agora = datetime.now()
        users_to_clean = []
        
        for user_id in cotizacoes_cache.keys():
            keys_expiradas = []
            for key, (timestamp, _) in cotizacoes_cache[user_id].items():
                if (agora - timestamp).seconds > cache_timeout:
                    keys_expiradas.append(key)
            
            for key in keys_expiradas:
                del cotizacoes_cache[user_id][key]
            
            # Si el cache del usuario está vacío, marcarlo para eliminación
            if not cotizacoes_cache[user_id]:
                users_to_clean.append(user_id)
        
        # Limpiar caches de usuarios vacíos
        for user_id in users_to_clean:
            del cotizacoes_cache[user_id]
        
        if users_to_clean:
            logger.info(f"Limpeza de cache: {len(users_to_clean)} caches de usuários removidos")
    
    @staticmethod
    def obter_ultima_cotacao_bd(ticker: str) -> Optional[dict]:
        """
        Obtiene la última cotización guardada en BD como fallback del usuario actual
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            Optional[dict]: Datos de cotización desde BD o None
        """
        session = SessionLocal()
        try:
            # Obtener usuario actual
            user_id = CotacaoService._get_current_user_id()
            
            # Buscar el ativo por ticker del usuario
            ativo = session.query(Ativo).filter(
                Ativo.ticker == ticker,
                Ativo.user_id == user_id
            ).first()
            
            if not ativo:
                logger.warning(f"Ativo {ticker} não encontrado para usuario {user_id}")
                return None
            
            # Buscar el precio más reciente del usuario
            ultimo_preco = session.query(PrecoDiario).filter(
                PrecoDiario.ativo_id == ativo.id,
                PrecoDiario.user_id == user_id
            ).order_by(PrecoDiario.data.desc()).first()
            
            if not ultimo_preco:
                logger.warning(f"Nenhum preço histórico encontrado para {ticker} do usuario {user_id}")
                return None
            
            # Buscar precio anterior para calcular variación
            preco_anterior = session.query(PrecoDiario).filter(
                PrecoDiario.ativo_id == ativo.id,
                PrecoDiario.user_id == user_id,
                PrecoDiario.data < ultimo_preco.data
            ).order_by(PrecoDiario.data.desc()).first()
            
            preco_anterior_valor = float(preco_anterior.preco_fechamento) if preco_anterior else float(ultimo_preco.preco_fechamento)
            
            logger.info(f"Usuario {user_id} usando última cotação da BD para {ticker}: {ultimo_preco.preco_fechamento} ({ultimo_preco.data})")
            
            return {
                'ticker': ticker,
                'preco_atual': float(ultimo_preco.preco_fechamento),
                'abertura': float(ultimo_preco.preco_fechamento),  # Aproximación
                'fechamento_anterior': preco_anterior_valor,
                'variacao_dia': float(ultimo_preco.preco_fechamento) - preco_anterior_valor,
                'variacao_pct': round(((float(ultimo_preco.preco_fechamento) - preco_anterior_valor) / preco_anterior_valor) * 100, 2) if preco_anterior_valor > 0 else 0,
                'volume': 0,  # No tenemos volume histórico
                'data': ultimo_preco.data,
                'fonte': 'BD_FALLBACK_USER'  # Indicador de que es fallback del usuario
            }
        except Exception as e:
            logger.error(f"Erro ao obter última cotação da BD para {ticker} usuario {user_id}: {e}", exc_info=True)
            return None
        finally:
            session.close()
    
    @staticmethod
    def obter_cotacao_atual(ticker: str) -> Optional[dict]:
        """
        Obtiene la cotización actual de un ticker con cache por usuario y fallback a BD
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            Optional[dict]: Datos de cotización o None
        """
        global cotizacoes_cache
        
        try:
            # Obtener usuario actual
            user_id = CotacaoService._get_current_user_id()
            
            # Limpiar cache expirado
            CotacaoService.limpar_cache_antigo()
            
            # Inicializar cache del usuario si no existe
            if user_id not in cotizacoes_cache:
                cotizacoes_cache[user_id] = {}
            
            # Verificar cache del usuario primero
            cache_key = f"{ticker}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            if cache_key in cotizacoes_cache[user_id]:
                cached_time, cached_data = cotizacoes_cache[user_id][cache_key]
                if (datetime.now() - cached_time).seconds < cache_timeout:
                    logger.info(f"Usuario {user_id} usando cotação em cache para {ticker}")
                    cached_data['fonte'] = 'CACHE_USER'
                    return cached_data
            
            logger.info(f"Usuario {user_id} obtendo cotação para {ticker}")
            
            # Rate limiting: delay aleatorio para evitar exceso de requests
            yahoo_config = Config.get_yahoo_config()
            delay = random.uniform(yahoo_config['request_delay_min'], yahoo_config['request_delay_max'])
            time.sleep(delay)
            
            stock = yf.Ticker(ticker)
            
            # Usar timeout más bajo y menos datos para reducir rate limiting
            hist = stock.history(period="5d", timeout=yahoo_config['yahoo_timeout'])
            
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
            
            # Guardar en cache del usuario
            cotizacoes_cache[user_id][cache_key] = (datetime.now(), cotacao)
            
            logger.info(f"Usuario {user_id} obteve cotação do Yahoo Finance para {ticker}: {cotacao['preco_atual']}")
            return cotacao
            
        except Exception as e:
            logger.warning(f"Erro no Yahoo Finance para {ticker}: {e}. Tentando fallback da BD...")
            
            # Fallback: usar última cotación del usuario desde BD
            cotacao_bd = CotacaoService.obter_ultima_cotacao_bd(ticker)
            if cotacao_bd:
                st.info(f"📊 {ticker}: Usando tu cotización de BD ({cotacao_bd['data']}) - API temporalmente limitada")
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
        Guarda el precio diario actual en la BD para el usuario actual
        
        Args:
            ativo_id: ID del activo
            ticker: Símbolo del ticker
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        session = SessionLocal()
        try:
            # Obtener usuario actual
            user_id = CotacaoService._get_current_user_id()
            
            # Obtener cotización actual
            cotacao = CotacaoService.obter_cotacao_atual(ticker)
            if not cotacao:
                logger.warning(f"Não foi possível obter cotação para salvar preço de {ticker} para usuario {user_id}")
                return False
            
            # Verificar si ya existe precio para hoy del usuario
            hoje = datetime.now().date()
            preco_existente = session.query(PrecoDiario).filter(
                PrecoDiario.ativo_id == ativo_id,
                PrecoDiario.data == hoje,
                PrecoDiario.user_id == user_id
            ).first()
            
            if preco_existente:
                # Actualizar precio existente
                preco_existente.preco_fechamento = cotacao['preco_atual']
                logger.info(f"Preço atualizado para {ticker} usuario {user_id}: {cotacao['preco_atual']}")
            else:
                # Crear nuevo registro para el usuario
                novo_preco = PrecoDiario(
                    ativo_id=ativo_id,
                    data=hoje,
                    preco_fechamento=cotacao['preco_atual'],
                    user_id=user_id  # Asignar al usuario actual
                )
                session.add(novo_preco)
                logger.info(f"Novo preço salvo para {ticker} usuario {user_id}: {cotacao['preco_atual']}")
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao salvar preço diário para {ticker}: {e}", exc_info=True)
            return False
        finally:
            session.close()
    
    @staticmethod
    def obter_historico_usuario(ticker: str, dias: int = 30) -> pd.DataFrame:
        """
        Obtiene el histórico de precios de un ticker del usuario actual desde la BD
        
        Args:
            ticker: Símbolo del ticker
            dias: Número de días de histórico
            
        Returns:
            pd.DataFrame: DataFrame con el histórico de precios del usuario
        """
        session = SessionLocal()
        try:
            user_id = CotacaoService._get_current_user_id()
            
            # Buscar el activo del usuario
            ativo = session.query(Ativo).filter(
                Ativo.ticker == ticker,
                Ativo.user_id == user_id
            ).first()
            
            if not ativo:
                logger.warning(f"Ativo {ticker} não encontrado para usuario {user_id}")
                return pd.DataFrame()
            
            # Obtener histórico del usuario
            data_inicio = datetime.now() - timedelta(days=dias)
            precos = session.query(PrecoDiario).filter(
                PrecoDiario.ativo_id == ativo.id,
                PrecoDiario.user_id == user_id,
                PrecoDiario.data >= data_inicio.date()
            ).order_by(PrecoDiario.data).all()
            
            if not precos:
                logger.warning(f"Nenhum histórico encontrado para {ticker} usuario {user_id}")
                return pd.DataFrame()
            
            # Convertir a DataFrame
            data = {
                'Date': [p.data for p in precos],
                'Close': [float(p.preco_fechamento) for p in precos]
            }
            
            df = pd.DataFrame(data)
            df.set_index('Date', inplace=True)
            
            logger.info(f"Histórico obtido para {ticker} usuario {user_id}: {len(df)} dias")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao obter histórico de BD para {ticker}: {e}")
            return pd.DataFrame()
        finally:
            session.close()
    
    @staticmethod
    def get_cache_stats(user_id: int = None) -> dict:
        """
        Obtiene estadísticas del cache de cotizaciones
        
        Args:
            user_id: ID del usuario (si no se especifica, usa el usuario actual)
            
        Returns:
            dict: Estadísticas del cache
        """
        try:
            if user_id is None:
                user_id = CotacaoService._get_current_user_id()
            
            global cotizacoes_cache
            
            if user_id not in cotizacoes_cache:
                return {
                    'total_entries': 0,
                    'user_id': user_id,
                    'cache_size_kb': 0
                }
            
            user_cache = cotizacoes_cache[user_id]
            total_entries = len(user_cache)
            
            # Estimar tamaño del cache (aproximado)
            cache_size = sum(len(str(data)) for _, data in user_cache.values())
            
            return {
                'total_entries': total_entries,
                'user_id': user_id,
                'cache_size_kb': round(cache_size / 1024, 2)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de cache: {e}")
            return {
                'total_entries': 0,
                'user_id': user_id,
                'cache_size_kb': 0
            }