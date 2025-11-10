#!/usr/bin/env python3
"""
Script de Prueba de Conexión y Funcionalidades
Sistema de Gestión de Valores Cotizados

Este script verifica que todos los componentes del sistema funcionen correctamente:
- Conexión a PostgreSQL
- Creación de tablas
- APIs externas (Yahoo Finance)
- Operaciones CRUD básicas
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import yfinance as yf


def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"✅ {message}")


def print_error(message):
    """Imprime mensaje de error"""
    print(f"❌ {message}")


def print_info(message):
    """Imprime mensaje informativo"""
    print(f"ℹ️  {message}")


def test_environment_variables():
    """Prueba 1: Verificar variables de entorno"""
    print_header("TEST 1: Variables de Entorno")
    
    required_vars = ['DATABASE_URL']
    optional_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
    
    all_ok = True
    
    # Verificar variables requeridas
    for var in required_vars:
        if os.getenv(var):
            print_success(f"{var} encontrada")
        else:
            print_error(f"{var} no encontrada")
            all_ok = False
    
    # Mostrar variables opcionales
    print("\nVariables opcionales:")
    for var in optional_vars:
        value = os.getenv(var, 'No configurada')
        if value != 'No configurada':
            # Ocultar contraseñas
            if 'PASSWORD' in var:
                value = '*' * len(value)
        print(f"   {var}: {value}")
    
    return all_ok


def test_database_connection():
    """Prueba 2: Verificar conexión a PostgreSQL"""
    print_header("TEST 2: Conexión a PostgreSQL")
    
    database_url = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/stock_management'
    )
    
    try:
        print_info(f"Intentando conectar a: {database_url.split('@')[1]}")
        engine = create_engine(database_url)
        
        # Intentar conectar
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print_success("Conexión exitosa a PostgreSQL")
            print(f"   Versión: {version.split(',')[0]}")
            
            # Verificar base de datos actual
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"   Base de datos: {db_name}")
            
        return True, engine
        
    except Exception as e:
        print_error(f"Error de conexión: {e}")
        return False, None


def test_database_tables(engine):
    """Prueba 3: Verificar existencia de tablas"""
    print_header("TEST 3: Estructura de Base de Datos")
    
    required_tables = ['ativos', 'precos_diarios', 'operacoes', 'posicoes']
    
    try:
        with engine.connect() as conn:
            # Obtener lista de tablas
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            existing_tables = [row[0] for row in result]
            
            all_ok = True
            for table in required_tables:
                if table in existing_tables:
                    print_success(f"Tabla '{table}' existe")
                    
                    # Contar registros
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table};"))
                    count = count_result.fetchone()[0]
                    print(f"   Registros: {count}")
                else:
                    print_error(f"Tabla '{table}' no existe")
                    all_ok = False
            
            # Verificar vistas
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.views 
                WHERE table_schema = 'public';
            """))
            
            views = [row[0] for row in result]
            if views:
                print("\nVistas creadas:")
                for view in views:
                    print(f"   ✓ {view}")
            
        return all_ok
        
    except Exception as e:
        print_error(f"Error al verificar tablas: {e}")
        return False


def test_yahoo_finance_api():
    """Prueba 4: Verificar API de Yahoo Finance"""
    print_header("TEST 4: API de Yahoo Finance")
    
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'INVALID_TICKER_XYZ']
    
    all_ok = True
    
    for ticker in test_tickers:
        try:
            print_info(f"Probando ticker: {ticker}")
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period='1d')
            
            if hist.empty or 'regularMarketPrice' not in info:
                print_error(f"  '{ticker}' no es válido o no tiene datos")
                if ticker != 'INVALID_TICKER_XYZ':
                    all_ok = False
            else:
                print_success(f"  '{ticker}' - {info.get('longName', 'N/A')}")
                print(f"     Precio actual: ${info['regularMarketPrice']:.2f}")
                
        except Exception as e:
            if ticker == 'INVALID_TICKER_XYZ':
                print_success(f"  Validación correcta: ticker inválido rechazado")
            else:
                print_error(f"  Error con '{ticker}': {e}")
                all_ok = False
    
    return all_ok


def test_basic_operations(engine):
    """Prueba 5: Operaciones CRUD básicas"""
    print_header("TEST 5: Operaciones CRUD")
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Test: Insertar activo de prueba
        print_info("Insertando activo de prueba...")
        test_ticker = f"TEST{datetime.now().strftime('%H%M%S')}"
        
        session.execute(text("""
            INSERT INTO ativos (ticker, nome, ativo)
            VALUES (:ticker, :nome, :ativo)
        """), {
            'ticker': test_ticker,
            'nome': 'Test Asset',
            'ativo': True
        })
        session.commit()
        print_success(f"Activo '{test_ticker}' insertado")
        
        # Test: Leer activo
        print_info("Leyendo activo...")
        result = session.execute(text("""
            SELECT id, ticker, nome FROM ativos 
            WHERE ticker = :ticker
        """), {'ticker': test_ticker})
        
        row = result.fetchone()
        if row:
            print_success(f"Activo encontrado: ID={row[0]}, Ticker={row[1]}")
            ativo_id = row[0]
        else:
            print_error("No se pudo leer el activo")
            return False
        
        # Test: Actualizar activo
        print_info("Actualizando activo...")
        session.execute(text("""
            UPDATE ativos 
            SET nome = :nome 
            WHERE id = :id
        """), {
            'nome': 'Test Asset Updated',
            'id': ativo_id
        })
        session.commit()
        print_success("Activo actualizado")
        
        # Test: Insertar operación
        print_info("Insertando operación de prueba...")
        session.execute(text("""
            INSERT INTO operacoes (ativo_id, data, tipo, quantidade, preco)
            VALUES (:ativo_id, :data, :tipo, :quantidade, :preco)
        """), {
            'ativo_id': ativo_id,
            'data': datetime.now().date(),
            'tipo': 'compra',
            'quantidade': 10,
            'preco': 100.50
        })
        session.commit()
        print_success("Operación registrada")
        
        # Test: Eliminar datos de prueba
        print_info("Limpiando datos de prueba...")
        session.execute(text("DELETE FROM operacoes WHERE ativo_id = :id"), {'id': ativo_id})
        session.execute(text("DELETE FROM ativos WHERE id = :id"), {'id': ativo_id})
        session.commit()
        print_success("Datos de prueba eliminados")
        
        return True
        
    except Exception as e:
        session.rollback()
        print_error(f"Error en operaciones CRUD: {e}")
        return False
    finally:
        session.close()


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "█" * 70)
    print("  SISTEMA DE GESTIÓN DE VALORES - PRUEBAS DE INTEGRACIÓN")
    print("█" * 70)
    
    results = {}
    
    # Cargar variables de entorno
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print_info("Variables de entorno cargadas desde .env")
    except ImportError:
        print_info("python-dotenv no instalado, usando variables de sistema")
    
    # Test 1: Variables de entorno
    results['environment'] = test_environment_variables()
    
    # Test 2: Conexión a base de datos
    db_ok, engine = test_database_connection()
    results['connection'] = db_ok
    
    if not db_ok:
        print("\n" + "!" * 70)
        print_error("No se puede continuar sin conexión a la base de datos")
        print("!" * 70)
        return False
    
    # Test 3: Estructura de base de datos
    results['tables'] = test_database_tables(engine)
    
    # Test 4: API de Yahoo Finance
    results['yahoo_api'] = test_yahoo_finance_api()
    
    # Test 5: Operaciones CRUD
    results['crud'] = test_basic_operations(engine)
    
    # Resumen final
    print_header("RESUMEN DE PRUEBAS")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.upper():<20} {status}")
    
    print("\n" + "=" * 70)
    print(f"  RESULTADO FINAL: {passed_tests}/{total_tests} pruebas exitosas")
    print("=" * 70)
    
    if passed_tests == total_tests:
        print("\n🎉 ¡Todos los tests pasaron! El sistema está listo para usar.")
        return True
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa los mensajes de error arriba.")
        return False


def main():
    """Función principal"""
    success = run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()