import streamlit as st
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Numeric, CheckConstraint, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import os
import logging
from typing import List, Optional
import plotly.graph_objects as go
import time
import random

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

# Crear directorio de logs si no existe con permisos correctos
try:
    os.makedirs('logs', exist_ok=True)
    # Asegurar permisos de escritura
    os.chmod('logs', 0o755)
except Exception as e:
    print(f"Warning: No se pudo crear directorio logs: {e}")

# Configurar logging con fallback
handlers = []

try:
    # Intentar crear file handler
    file_handler = logging.FileHandler('logs/bolsa_v1.log', encoding='utf-8')
    handlers.append(file_handler)
except Exception as e:
    print(f"Warning: No se pudo crear archivo de log: {e}")

# Siempre incluir console handler
console_handler = logging.StreamHandler()
handlers.append(console_handler)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=handlers
)

logger = logging.getLogger(__name__)
logger.info("Sistema de logging inicializado")

# Cache para cotizaciones (evita llamadas excesivas a Yahoo Finance)
cotizacoes_cache = {}
cache_timeout = 300  # 5 minutos

def limpar_cache_antigo():
    """Limpia entradas de cache que han expirado"""
    now = datetime.now()
    keys_to_remove = []
    for key, (timestamp, _) in cotizacoes_cache.items():
        if (now - timestamp).seconds > cache_timeout:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del cotizacoes_cache[key]

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

# Para desarrollo local, usar estas credenciales (cambiar según tu configuración)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/stock_management"
)

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# ============================================================================
# MODELOS DE BASE DE DATOS
# ============================================================================

class Ativo(Base):
    """Modelo para activos/valores de bolsa"""
    __tablename__ = "ativos"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, nullable=False)
    nome = Column(String(100))
    ativo = Column(Boolean, default=True)
    
    precos_diarios = relationship("PrecoDiario", back_populates="ativo")
    operacoes = relationship("Operacao", back_populates="ativo")
    posicoes = relationship("Posicao", back_populates="ativo")


class PrecoDiario(Base):
    """Modelo para precios de cierre diarios"""
    __tablename__ = "precos_diarios"
    
    id = Column(Integer, primary_key=True, index=True)
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=False)
    data = Column(Date, nullable=False)
    preco_fechamento = Column(Numeric(12, 4), nullable=False)
    
    ativo = relationship("Ativo", back_populates="precos_diarios")


class Operacao(Base):
    """Modelo para operaciones de compra/venta"""
    __tablename__ = "operacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=False)
    data = Column(Date, nullable=False)
    tipo = Column(String(10), CheckConstraint("tipo IN ('compra','venda')"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco = Column(Numeric(12, 4), nullable=False)
    
    ativo = relationship("Ativo", back_populates="operacoes")


class Posicao(Base):
    """Modelo para posiciones consolidadas"""
    __tablename__ = "posicoes"
    
    id = Column(Integer, primary_key=True, index=True)
    ativo_id = Column(Integer, ForeignKey("ativos.id"), unique=True, nullable=False)
    quantidade_total = Column(Integer, default=0)
    preco_medio = Column(Numeric(12, 4), default=0)
    preco_atual = Column(Numeric(12, 4), default=0)
    resultado_dia = Column(Numeric(12, 4), default=0)
    resultado_acumulado = Column(Numeric(12, 4), default=0)
    
    ativo = relationship("Ativo", back_populates="posicoes")


# ============================================================================
# INICIALIZACIÓN DE BASE DE DATOS
# ============================================================================

def init_database():
    """Crea todas las tablas en la base de datos"""
    try:
        logger.info("Inicializando base de dados...")
        
        # Testar conexão primeiro
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        session.close()
        logger.info("Conexão com PostgreSQL estabelecida com sucesso")
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas/verificadas com sucesso")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao inicializar base de dados: {e}", exc_info=True)
        st.error(f"❌ Error al inicializar base de datos: {e}")
        return False


# ============================================================================
# SERVICIOS - GESTIÓN DE ACTIVOS
# ============================================================================

def validar_ticker(ticker: str) -> dict:
    """Valida que un ticker existe en Yahoo Finance y retorna información básica"""
    try:
        logger.info(f"Validando ticker: {ticker}")
        
        # Lista de tickers conocidos para validación offline
        tickers_conhecidos = {
            'NVDA': 'NVIDIA Corporation',
            'NVIDIA': 'NVDA',  # Redirect common name to ticker
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'GOOG': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'META': 'Meta Platforms Inc.',
            'NFLX': 'Netflix Inc.',
            'AMD': 'Advanced Micro Devices Inc.',
            'INTC': 'Intel Corporation',
            'CRM': 'Salesforce Inc.',
            'PYPL': 'PayPal Holdings Inc.',
            'ADBE': 'Adobe Inc.'
        }
        
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
        delay = random.uniform(1.0, 2.0)
        time.sleep(delay)
        
        stock = yf.Ticker(ticker_upper)
        info = stock.info
        
        # Verificar que tengamos información válida
        if not info or 'regularMarketPrice' not in info:
            hist = stock.history(period="1d", timeout=10)
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


def adicionar_ativo(ticker: str, nome: str = None) -> bool:
    """Añade un nuevo activo a la base de datos"""
    session = SessionLocal()
    logger.info(f"Tentando adicionar ativo: {ticker}")
    
    try:
        ticker = ticker.upper().strip()
        
        # Verificar si ya existe
        existente = session.query(Ativo).filter(Ativo.ticker == ticker).first()
        if existente:
            logger.warning(f"Ticker {ticker} já existe na base de dados")
            st.warning(f"⚠️ El ticker {ticker} ya existe en la base de datos")
            return False
        
        # Validar que el ticker existe en Yahoo Finance
        validacao = validar_ticker(ticker)
        if not validacao['valido']:
            logger.error(f"Ticker {ticker} inválido: {validacao['erro']}")
            st.error(f"❌ {validacao['erro']}")
            return False
        
        # Mostrar warning si la validación fue manual/offline
        if 'warning' in validacao:
            st.warning(f"⚠️ {validacao['warning']}")
        
        # Mostrar info sobre la fuente de validación
        fonte = validacao.get('fonte', 'UNKNOWN')
        if fonte == 'LISTA_CONOCIDA':
            st.info(f"📋 {ticker} validado desde lista de tickers conocidos")
        elif fonte == 'MANUAL' or fonte == 'MANUAL_FALLBACK':
            st.warning(f"🔧 {ticker} agregado manualmente - validación offline")
        
        # Crear nuevo activo
        nuevo_ativo = Ativo(
            ticker=ticker,
            nome=nome or validacao['nome'],
            ativo=True
        )
        session.add(nuevo_ativo)
        session.commit()
        
        logger.info(f"Ativo {ticker} adicionado com sucesso (fonte: {fonte})")
        st.success(f"✅ Activo {ticker} - {validacao['nome']} añadido correctamente")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao adicionar ativo {ticker}: {e}", exc_info=True)
        st.error(f"❌ Error al añadir activo: {e}")
        return False
    finally:
        session.close()


def listar_ativos(apenas_ativos: bool = True) -> List[Ativo]:
    """Lista todos los activos"""
    session = SessionLocal()
    try:
        query = session.query(Ativo)
        if apenas_ativos:
            query = query.filter(Ativo.ativo == True)
        return query.all()
    finally:
        session.close()


def eliminar_ativo(ticker: str) -> bool:
    """Elimina un activo y todos sus datos relacionados"""
    session = SessionLocal()
    logger.info(f"Tentando eliminar ativo: {ticker}")
    
    try:
        ticker = ticker.upper().strip()
        
        # Buscar el activo
        ativo = session.query(Ativo).filter(Ativo.ticker == ticker).first()
        if not ativo:
            logger.warning(f"Ticker {ticker} não encontrado para eliminação")
            st.warning(f"⚠️ El ticker {ticker} no existe en la base de datos")
            return False
        
        # Verificar si tiene operaciones asociadas
        operacoes_count = session.query(Operacao).filter(Operacao.ativo_id == ativo.id).count()
        if operacoes_count > 0:
            st.warning(f"⚠️ El activo {ticker} tiene {operacoes_count} operación(es) registrada(s)")
            
            # Ofrecer opción de eliminación completa
            confirmar = st.checkbox(f"🗑️ Eliminar {ticker} y TODAS sus {operacoes_count} operación(es) asociadas (IRREVERSIBLE)", key=f"confirm_delete_{ticker}")
            
            if not confirmar:
                st.info("💡 Para eliminar un activo con operaciones, debe marcar la casilla de confirmación")
                return False
        
        # Verificar si tiene posición actual
        posicao = session.query(Posicao).filter(Posicao.ativo_id == ativo.id).first()
        if posicao and posicao.quantidade_total > 0:
            st.error(f"❌ No se puede eliminar {ticker}: tiene una posición activa de {posicao.quantidade_total} acciones")
            st.info("💡 Primero debe vender todas las acciones antes de eliminar el activo")
            return False
        
        # Eliminar en cascada (el orden importa por las foreign keys)
        # 1. Operaciones
        operacoes_deleted = session.query(Operacao).filter(Operacao.ativo_id == ativo.id).delete()
        
        # 2. Precios históricos  
        precos_deleted = session.query(PrecoDiario).filter(PrecoDiario.ativo_id == ativo.id).delete()
        
        # 3. Posición
        posicoes_deleted = session.query(Posicao).filter(Posicao.ativo_id == ativo.id).delete()
        
        # 4. Finalmente el activo
        session.delete(ativo)
        session.commit()
        
        logger.info(f"Ativo {ticker} eliminado com sucesso: {operacoes_deleted} operações, {precos_deleted} preços, {posicoes_deleted} posições")
        st.success(f"✅ {ticker} eliminado exitosamente")
        st.info(f"📊 Datos eliminados: {operacoes_deleted} operación(es), {precos_deleted} precio(s), {posicoes_deleted} posición(es)")
        
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao eliminar ativo {ticker}: {e}", exc_info=True)
        st.error(f"❌ Error al eliminar activo: {e}")
        return False
    finally:
        session.close()


def desactivar_ativo(ticker: str) -> bool:
    """Desactiva un activo sin eliminarlo (opción más segura)"""
    session = SessionLocal()
    logger.info(f"Tentando desactivar ativo: {ticker}")
    
    try:
        ticker = ticker.upper().strip()
        
        # Buscar el activo
        ativo = session.query(Ativo).filter(Ativo.ticker == ticker).first()
        if not ativo:
            logger.warning(f"Ticker {ticker} não encontrado para desativação")
            st.warning(f"⚠️ El ticker {ticker} no existe en la base de datos")
            return False
        
        if not ativo.ativo:
            st.info(f"ℹ️ El ticker {ticker} ya está desactivado")
            return True
        
        # Verificar si tiene posición actual
        posicao = session.query(Posicao).filter(Posicao.ativo_id == ativo.id).first()
        if posicao and posicao.quantidade_total > 0:
            st.error(f"❌ No se puede desactivar {ticker}: tiene una posición activa de {posicao.quantidade_total} acciones")
            st.info("💡 Primero debe vender todas las acciones antes de desactivar el activo")
            return False
        
        # Desactivar el activo
        ativo.ativo = False
        session.commit()
        
        logger.info(f"Ativo {ticker} desactivado com sucesso")
        st.success(f"✅ {ticker} desactivado exitosamente (se puede reactivar después)")
        st.info("💡 El activo está oculto pero conserva todos sus datos históricos")
        
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao desactivar ativo {ticker}: {e}", exc_info=True)
        st.error(f"❌ Error al desactivar activo: {e}")
        return False
    finally:
        session.close()


def reactivar_ativo(ticker: str) -> bool:
    """Reactiva un activo previamente desactivado"""
    session = SessionLocal()
    logger.info(f"Tentando reactivar ativo: {ticker}")
    
    try:
        ticker = ticker.upper().strip()
        
        # Buscar el activo (incluir inactivos)
        ativo = session.query(Ativo).filter(Ativo.ticker == ticker).first()
        if not ativo:
            logger.warning(f"Ticker {ticker} não encontrado para reativação")
            st.warning(f"⚠️ El ticker {ticker} no existe en la base de datos")
            return False
        
        if ativo.ativo:
            st.info(f"ℹ️ El ticker {ticker} ya está activo")
            return True
        
        # Reactivar el activo
        ativo.ativo = True
        session.commit()
        
        logger.info(f"Ativo {ticker} reactivado com sucesso")
        st.success(f"✅ {ticker} reactivado exitosamente")
        
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao reactivar ativo {ticker}: {e}", exc_info=True)
        st.error(f"❌ Error al reactivar activo: {e}")
        return False
    finally:
        session.close()


# ============================================================================
# SERVICIOS - COTIZACIONES
# ============================================================================

def obter_ultima_cotacao_bd(ticker: str) -> Optional[dict]:
    """Obtiene la última cotización guardada en BD como fallback"""
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
            'abertura': float(ultimo_preco.preco_fechamento),  # Aproximação
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


def obter_cotacao_atual(ticker: str) -> Optional[dict]:
    """Obtiene la cotización actual de un ticker con fallback a BD"""
    
    # Limpiar cache expirado
    limpar_cache_antigo()
    
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
        delay = random.uniform(1.0, 3.0)  # Aumentado a 1-3 segundos
        time.sleep(delay)
        
        stock = yf.Ticker(ticker)
        
        # Usar timeout más bajo y menos datos para reducir rate limiting
        hist = stock.history(period="5d", timeout=15)
        
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
        cotacao_bd = obter_ultima_cotacao_bd(ticker)
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


def salvar_preco_diario(ativo_id: int, ticker: str) -> bool:
    """Guarda el precio de cierre del día"""
    session = SessionLocal()
    try:
        cotacao = obter_cotacao_atual(ticker)
        if not cotacao:
            return False
        
        # Verificar si ya existe para esta fecha
        hoje = datetime.now().date()
        existente = session.query(PrecoDiario).filter(
            PrecoDiario.ativo_id == ativo_id,
            PrecoDiario.data == hoje
        ).first()
        
        if existente:
            existente.preco_fechamento = cotacao['preco_atual']
        else:
            novo_preco = PrecoDiario(
                ativo_id=ativo_id,
                data=hoje,
                preco_fechamento=cotacao['preco_atual']
            )
            session.add(novo_preco)
        
        session.commit()
        return True
        
    except Exception as e:
        session.rollback()
        st.error(f"Error al guardar precio diario: {e}")
        return False
    finally:
        session.close()


# ============================================================================
# SERVICIOS - OPERACIONES
# ============================================================================

def registrar_operacao(ativo_id: int, data: datetime, tipo: str, quantidade: int, preco: float) -> bool:
    """Registra una operación de compra o venta"""
    session = SessionLocal()
    logger.info(f"Iniciando registro de operação: ativo_id={ativo_id}, tipo={tipo}, quantidade={quantidade}, preco={preco}")
    
    try:
        # VALIDACIÓN: Verificar saldo suficiente para ventas
        if tipo == 'venda':
            posicao_atual = session.query(Posicao).filter(Posicao.ativo_id == ativo_id).first()
            
            if not posicao_atual:
                logger.warning(f"Tentativa de venda sem posição: ativo_id={ativo_id}")
                st.error("❌ Error: No tienes posición en este activo para vender")
                return False
            
            if posicao_atual.quantidade_total < quantidade:
                logger.warning(f"Tentativa de venda com saldo insuficiente: ativo_id={ativo_id}, saldo={posicao_atual.quantidade_total}, tentativa={quantidade}")
                st.error(f"❌ Error: Saldo insuficiente. Tienes {posicao_atual.quantidade_total} acciones, intentas vender {quantidade}")
                return False
        
        nova_operacao = Operacao(
            ativo_id=ativo_id,
            data=data.date(),
            tipo=tipo,
            quantidade=quantidade,
            preco=preco
        )
        session.add(nova_operacao)
        session.commit()
        
        logger.info(f"Operação registrada com sucesso: ID da operação gerada")
        
        # Actualizar posición
        atualizar_posicao(ativo_id)
        
        st.success(f"✅ Operación de {tipo} registrada correctamente")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao registrar operação: {e}", exc_info=True)
        st.error(f"Error al registrar operación: {e}")
        return False
    finally:
        session.close()


def listar_operacoes(ativo_id: Optional[int] = None) -> List[Operacao]:
    """Lista operaciones, opcionalmente filtradas por activo"""
    session = SessionLocal()
    try:
        query = session.query(Operacao).order_by(Operacao.data.desc())
        if ativo_id:
            query = query.filter(Operacao.ativo_id == ativo_id)
        return query.all()
    finally:
        session.close()


# ============================================================================
# SERVICIOS - POSICIONES
# ============================================================================

def atualizar_posicao(ativo_id: int) -> bool:
    """Actualiza la posición consolidada de un activo"""
    session = SessionLocal()
    logger.info(f"Atualizando posição para ativo_id={ativo_id}")
    
    try:
        # Obtener todas las operaciones del activo
        operacoes = session.query(Operacao).filter(Operacao.ativo_id == ativo_id).all()
        logger.info(f"Encontradas {len(operacoes)} operações para ativo {ativo_id}")
        
        quantidade_total = 0
        valor_total = 0
        
        for op in operacoes:
            if op.tipo == 'compra':
                quantidade_total += op.quantidade
                valor_total += op.quantidade * float(op.preco)
            else:  # venda
                quantidade_total -= op.quantidade
                valor_total -= op.quantidade * float(op.preco)
        
        preco_medio = valor_total / quantidade_total if quantidade_total > 0 else 0
        logger.info(f"Posição calculada: quantidade={quantidade_total}, preço_médio={preco_medio:.4f}")
        
        # Obtener precio actual
        ativo = session.query(Ativo).filter(Ativo.id == ativo_id).first()
        if not ativo:
            logger.error(f"Ativo não encontrado: {ativo_id}")
            return False
            
        cotacao = obter_cotacao_atual(ativo.ticker)
        preco_atual = cotacao['preco_atual'] if cotacao else 0
        
        if preco_atual == 0:
            logger.warning(f"Preço atual não disponível para {ativo.ticker}, usando 0")
        
        # Calcular resultados
        resultado_acumulado = (preco_atual - preco_medio) * quantidade_total if quantidade_total > 0 else 0
        
        # Obtener precio de ayer para resultado del día
        ontem = datetime.now().date() - timedelta(days=1)
        preco_ontem = session.query(PrecoDiario).filter(
            PrecoDiario.ativo_id == ativo_id,
            PrecoDiario.data == ontem
        ).first()
        
        resultado_dia = (preco_atual - float(preco_ontem.preco_fechamento)) * quantidade_total if preco_ontem and quantidade_total > 0 else 0
        
        # Actualizar o crear posición
        posicao = session.query(Posicao).filter(Posicao.ativo_id == ativo_id).first()
        
        if posicao:
            logger.info(f"Atualizando posição existente para {ativo.ticker}")
            posicao.quantidade_total = quantidade_total
            posicao.preco_medio = preco_medio
            posicao.preco_atual = preco_atual
            posicao.resultado_dia = resultado_dia
            posicao.resultado_acumulado = resultado_acumulado
        else:
            logger.info(f"Criando nova posição para {ativo.ticker}")
            nova_posicao = Posicao(
                ativo_id=ativo_id,
                quantidade_total=quantidade_total,
                preco_medio=preco_medio,
                preco_atual=preco_atual,
                resultado_dia=resultado_dia,
                resultado_acumulado=resultado_acumulado
            )
            session.add(nova_posicao)
        
        session.commit()
        logger.info(f"Posição atualizada com sucesso para {ativo.ticker}: resultado_acumulado={resultado_acumulado:.2f}")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao atualizar posição do ativo {ativo_id}: {e}", exc_info=True)
        st.error(f"❌ Error al actualizar posición: {e}")
        return False
    finally:
        session.close()


def listar_posicoes() -> List[Posicao]:
    """Lista todas las posiciones con cantidad > 0"""
    session = SessionLocal()
    try:
        return session.query(Posicao).filter(Posicao.quantidade_total > 0).all()
    finally:
        session.close()


# ============================================================================
# SERVICIOS - HISTÓRICO
# ============================================================================

def obter_historico(ticker: str, dias: int = 30) -> pd.DataFrame:
    """Obtiene el histórico de precios de un ticker"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f"{dias}d")
        return hist
    except Exception as e:
        st.error(f"Error al obtener histórico de {ticker}: {e}")
        return pd.DataFrame()


# ============================================================================
# INTERFAZ STREAMLIT
# ============================================================================

def main():
    st.set_page_config(page_title="Sistema de Gestión de Valores", page_icon="📊", layout="wide")
    
    st.title("📊 Sistema de Gestión de Valores Cotizados")
    st.markdown("---")
    
    # Inicializar base de datos
    if 'db_initialized' not in st.session_state:
        if init_database():
            st.session_state.db_initialized = True
        else:
            st.error("❌ No se pudo conectar a la base de datos PostgreSQL")
            st.info("Asegúrate de tener PostgreSQL corriendo y la base de datos 'stock_management' creada")
            st.stop()
    
    # Menú lateral
    menu = st.sidebar.selectbox(
        "📋 Menú",
        ["Valores", "Cotizaciones", "Operaciones", "Posiciones", "Histórico"]
    )
    
    # ========================================================================
    # PANTALLA: VALORES
    # ========================================================================
    if menu == "Valores":
        st.header("📈 Gestión de Valores")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("➕ Añadir Nuevo Valor")
            with st.form("form_nuevo_ativo"):
                ticker_input = st.text_input("Ticker (ej: AAPL, MSFT, GOOGL)", max_chars=10)
                nome_input = st.text_input("Nombre (opcional)")
                submitted = st.form_submit_button("Añadir Valor")
                
                if submitted and ticker_input:
                    adicionar_ativo(ticker_input, nome_input)
        
        with col2:
            st.subheader("💡 Ejemplos de Tickers")
            st.markdown("""
            - **AAPL** - Apple
            - **MSFT** - Microsoft
            - **GOOGL** - Alphabet/Google
            - **TSLA** - Tesla
            - **AMZN** - Amazon
            - **META** - Meta/Facebook
            """)
        
        st.markdown("---")
        st.subheader("📊 Valores Registrados")
        
        ativos = listar_ativos()
        st.write(f"✅ Sistema funcionando: {len(ativos)} activos disponibles")  # Info line
        
        if ativos:
            # Mostrar tabla de activos
            data = []
            for ativo in ativos:
                data.append({
                    'ID': ativo.id,
                    'Ticker': ativo.ticker,
                    'Nombre': ativo.nome,
                    'Activo': '✅' if ativo.ativo else '❌'
                })
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            # Sección de gestión de activos - VERSIÓN COMPLETA
            st.markdown("---")
            st.subheader("🔧 Gestión de Activos")
            
            # Crear tres columnas para las diferentes opciones
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🗑️ Eliminar Activo**")
                with st.form("form_eliminar_ativo"):
                    ticker_eliminar = st.selectbox(
                        "Seleccionar activo para eliminar:",
                        options=[ativo.ticker for ativo in ativos],
                        help="⚠️ CUIDADO: Esto eliminará TODOS los datos relacionados"
                    )
                    submitted_eliminar = st.form_submit_button("🗑️ Eliminar", type="secondary")
                    
                    if submitted_eliminar and ticker_eliminar:
                        if eliminar_ativo(ticker_eliminar):
                            st.rerun()
            
            with col2:
                st.markdown("**⏸️ Desactivar Activo**")
                ativos_activos = [a for a in ativos if a.ativo]
                if ativos_activos:
                    with st.form("form_desactivar_ativo"):
                        ticker_desactivar = st.selectbox(
                            "Seleccionar activo para desactivar:",
                            options=[ativo.ticker for ativo in ativos_activos],
                            help="💡 Oculta el activo pero conserva los datos"
                        )
                        submitted_desactivar = st.form_submit_button("⏸️ Desactivar", type="secondary")
                        
                        if submitted_desactivar and ticker_desactivar:
                            if desactivar_ativo(ticker_desactivar):
                                st.rerun()
                else:
                    st.info("No hay activos activos para desactivar")
            
            with col3:
                st.markdown("**▶️ Reactivar Activo**")
                ativos_inativos = [a for a in listar_ativos(apenas_ativos=False) if not a.ativo]
                if ativos_inativos:
                    with st.form("form_reactivar_ativo"):
                        ticker_reactivar = st.selectbox(
                            "Seleccionar activo para reactivar:",
                            options=[ativo.ticker for ativo in ativos_inativos],
                            help="▶️ Volver a mostrar activo desactivado"
                        )
                        submitted_reactivar = st.form_submit_button("▶️ Reactivar", type="primary")
                        
                        if submitted_reactivar and ticker_reactivar:
                            if reactivar_ativo(ticker_reactivar):
                                st.rerun()
                else:
                    st.info("No hay activos desactivados")
                    
            # Información de ayuda
            st.markdown("---")
            st.info("""
            💡 **Opciones de gestión:**
            - **🗑️ Eliminar**: Borra completamente el activo y TODOS sus datos (irreversible)
            - **⏸️ Desactivar**: Oculta el activo pero conserva todos los datos históricos
            - **▶️ Reactivar**: Vuelve a mostrar un activo desactivado
            
            ⚠️ **Importante**: No se pueden eliminar/desactivar activos con posiciones activas.
            """)
            
        else:
            st.info("No hay valores registrados. Añade algunos usando el formulario arriba.")
    
    # ========================================================================
    # PANTALLA: COTIZACIONES
    # ========================================================================
    elif menu == "Cotizaciones":
        st.header("💹 Cotizaciones en Tiempo Real")
        
        ativos = listar_ativos()
        if not ativos:
            st.warning("No hay valores registrados. Ve a la sección 'Valores' para añadir algunos.")
            return
        
        if st.button("🔄 Actualizar Cotizaciones", type="primary"):
            st.rerun()
        
        st.markdown("---")
        
        data_cotacoes = []
        for ativo in ativos:
            with st.spinner(f"Obteniendo {ativo.ticker}..."):
                cotacao = obter_cotacao_atual(ativo.ticker)
                if cotacao:
                    data_cotacoes.append({
                        'Ticker': cotacao['ticker'],
                        'Precio Actual': f"${cotacao['preco_atual']:.2f}",
                        'Apertura': f"${cotacao['abertura']:.2f}",
                        'Cierre Anterior': f"${cotacao['fechamento_anterior']:.2f}",
                        'Variación': f"${cotacao['variacao_dia']:.2f}",
                        'Variación %': f"{cotacao['variacao_pct']:.2f}%",
                        'Volumen': f"{cotacao['volume']:,}"
                    })
                    
                    # Guardar precio diario
                    salvar_preco_diario(ativo.id, ativo.ticker)
        
        if data_cotacoes:
            df_cotacoes = pd.DataFrame(data_cotacoes)
            st.dataframe(df_cotacoes, use_container_width=True)
    
    # ========================================================================
    # PANTALLA: OPERACIONES
    # ========================================================================
    elif menu == "Operaciones":
        st.header("💼 Registro de Operaciones")
        
        ativos = listar_ativos()
        if not ativos:
            st.warning("No hay valores registrados. Ve a la sección 'Valores' para añadir algunos.")
            return
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("➕ Nueva Operación")
            with st.form("form_operacao"):
                ativo_selecionado = st.selectbox(
                    "Valor",
                    options=[(a.id, f"{a.ticker} - {a.nome}") for a in ativos],
                    format_func=lambda x: x[1]
                )
                
                data_operacao = st.date_input("Fecha", value=datetime.now())
                tipo_operacao = st.radio("Tipo", ["compra", "venda"], horizontal=True)
                quantidade = st.number_input("Cantidad", min_value=1, value=1, step=1)
                preco = st.number_input("Precio Unitario", min_value=0.01, value=100.00, step=0.01)
                
                submitted = st.form_submit_button("Registrar Operación")
                
                if submitted:
                    total = quantidade * preco
                    st.info(f"Total: ${total:.2f}")
                    registrar_operacao(
                        ativo_id=ativo_selecionado[0],
                        data=datetime.combine(data_operacao, datetime.min.time()),
                        tipo=tipo_operacao,
                        quantidade=quantidade,
                        preco=preco
                    )
        
        with col2:
            st.subheader("📊 Resumen")
            st.metric("Total de Operaciones", len(listar_operacoes()))
        
        st.markdown("---")
        st.subheader("📜 Histórico de Operaciones")
        
        operacoes = listar_operacoes()
        if operacoes:
            data_ops = []
            for op in operacoes[:50]:  # Últimas 50
                ativo = next((a for a in ativos if a.id == op.ativo_id), None)
                data_ops.append({
                    'Fecha': op.data,
                    'Ticker': ativo.ticker if ativo else 'N/A',
                    'Tipo': op.tipo.upper(),
                    'Cantidad': op.quantidade,
                    'Precio': f"${float(op.preco):.2f}",
                    'Total': f"${op.quantidade * float(op.preco):.2f}"
                })
            
            df_ops = pd.DataFrame(data_ops)
            st.dataframe(df_ops, use_container_width=True)
        else:
            st.info("No hay operaciones registradas.")
    
    # ========================================================================
    # PANTALLA: POSICIONES
    # ========================================================================
    elif menu == "Posiciones":
        st.header("📊 Posiciones Consolidadas")
        
        if st.button("🔄 Actualizar Posiciones", type="primary"):
            ativos = listar_ativos()
            for ativo in ativos:
                atualizar_posicao(ativo.id)
            st.success("Posiciones actualizadas")
            st.rerun()
        
        st.markdown("---")
        
        posicoes = listar_posicoes()
        
        if posicoes:
            # Resumen general
            total_investido = sum(float(p.quantidade_total) * float(p.preco_medio) for p in posicoes)
            total_atual = sum(float(p.quantidade_total) * float(p.preco_atual) for p in posicoes)
            resultado_total = total_atual - total_investido
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Invertido", f"${total_investido:,.2f}")
            col2.metric("Valor Actual", f"${total_atual:,.2f}")
            col3.metric("Resultado", f"${resultado_total:,.2f}", 
                       delta=f"{(resultado_total/total_investido*100):.2f}%" if total_investido > 0 else "0%")
            col4.metric("Número de Posiciones", len(posicoes))
            
            st.markdown("---")
            
            # Tabla de posiciones
            data_pos = []
            session = SessionLocal()
            try:
                for pos in posicoes:
                    ativo = session.query(Ativo).filter(Ativo.id == pos.ativo_id).first()
                    financeiro_compra = float(pos.quantidade_total) * float(pos.preco_medio)
                    financeiro_atual = float(pos.quantidade_total) * float(pos.preco_atual)
                    
                    data_pos.append({
                        'Ticker': ativo.ticker,
                        'Cantidad': pos.quantidade_total,
                        'Precio Medio': f"${float(pos.preco_medio):.2f}",
                        'Precio Actual': f"${float(pos.preco_atual):.2f}",
                        'Invertido': f"${financeiro_compra:,.2f}",
                        'Valor Actual': f"${financeiro_atual:,.2f}",
                        'Resultado Día': f"${float(pos.resultado_dia):,.2f}",
                        'Resultado Total': f"${float(pos.resultado_acumulado):,.2f}",
                        'Rentabilidad': f"{(float(pos.resultado_acumulado)/financeiro_compra*100):.2f}%" if financeiro_compra > 0 else "0%"
                    })
            finally:
                session.close()
            
            df_pos = pd.DataFrame(data_pos)
            st.dataframe(df_pos, use_container_width=True)
        else:
            st.info("No hay posiciones abiertas. Registra operaciones de compra para crear posiciones.")
    
    # ========================================================================
    # PANTALLA: HISTÓRICO
    # ========================================================================
    elif menu == "Histórico":
        st.header("📈 Histórico de Precios")
        
        ativos = listar_ativos()
        if not ativos:
            st.warning("No hay valores registrados.")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            ticker_selecionado = st.selectbox(
                "Selecciona un Valor",
                options=[f"{a.ticker} - {a.nome}" for a in ativos]
            )
        
        with col2:
            dias = st.selectbox("Período", [7, 30, 90, 180, 365], index=2)
        
        if ticker_selecionado:
            ticker = ticker_selecionado.split(" - ")[0]
            
            with st.spinner(f"Cargando histórico de {ticker}..."):
                hist = obter_historico(ticker, dias)
                
                if not hist.empty:
                    # Gráfico
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close'],
                        name=ticker
                    ))
                    
                    fig.update_layout(
                        title=f"Histórico de {ticker} - Últimos {dias} días",
                        yaxis_title="Precio (USD)",
                        xaxis_title="Fecha",
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Estadísticas
                    st.subheader("📊 Estadísticas del Período")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    col1.metric("Precio Mínimo", f"${hist['Low'].min():.2f}")
                    col2.metric("Precio Máximo", f"${hist['High'].max():.2f}")
                    col3.metric("Precio Promedio", f"${hist['Close'].mean():.2f}")
                    col4.metric("Volumen Promedio", f"{int(hist['Volume'].mean()):,}")
                    
                    # Tabla de datos
                    st.subheader("📋 Datos Detallados")
                    hist_display = hist[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                    hist_display.columns = ['Apertura', 'Máximo', 'Mínimo', 'Cierre', 'Volumen']
                    st.dataframe(hist_display.sort_index(ascending=False).head(30), use_container_width=True)
                else:
                    st.error("No se pudo obtener el histórico")


if __name__ == "__main__":
    main()