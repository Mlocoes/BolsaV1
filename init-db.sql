-- ============================================================================
-- SCRIPT DE INICIALIZACIÓN DOCKER - BolsaV1
-- Sistema de Gestión de Valores Cotizados  
-- ============================================================================

-- Configurar codificación y locale
SET client_encoding = 'UTF8';
SET timezone = 'America/Sao_Paulo';

-- Mensaje de bienvenida
\echo '🚀 Iniciando configuración de base de datos BolsaV1...'

-- ============================================================================
-- TABLA: ativos
-- Almacena los valores/acciones que se están siguiendo
-- ============================================================================
CREATE TABLE IF NOT EXISTS ativos (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL UNIQUE,
    nome VARCHAR(100),
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ativos_ticker ON ativos(ticker);
CREATE INDEX IF NOT EXISTS idx_ativos_ativo ON ativos(ativo);

\echo '✅ Tabla ativos creada/verificada'

-- ============================================================================
-- TABLA: precos_diarios
-- Almacena los precios de cierre diarios de cada activo
-- ============================================================================
CREATE TABLE IF NOT EXISTS precos_diarios (
    id SERIAL PRIMARY KEY,
    ativo_id INTEGER NOT NULL REFERENCES ativos(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    preco_fechamento NUMERIC(12, 4) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ativo_id, data)
);

CREATE INDEX IF NOT EXISTS idx_precos_ativo_id ON precos_diarios(ativo_id);
CREATE INDEX IF NOT EXISTS idx_precos_data ON precos_diarios(data);
CREATE INDEX IF NOT EXISTS idx_precos_ativo_data ON precos_diarios(ativo_id, data);

\echo '✅ Tabla precos_diarios creada/verificada'

-- ============================================================================
-- TABLA: operacoes
-- Registra todas las operaciones de compra y venta
-- ============================================================================
CREATE TABLE IF NOT EXISTS operacoes (
    id SERIAL PRIMARY KEY,
    ativo_id INTEGER NOT NULL REFERENCES ativos(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('compra', 'venda')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco NUMERIC(12, 4) NOT NULL CHECK (preco > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_operacoes_ativo_id ON operacoes(ativo_id);
CREATE INDEX IF NOT EXISTS idx_operacoes_data ON operacoes(data);
CREATE INDEX IF NOT EXISTS idx_operacoes_tipo ON operacoes(tipo);

\echo '✅ Tabla operacoes creada/verificada'

-- ============================================================================
-- TABLA: posicoes
-- Almacena las posiciones consolidadas calculadas
-- ============================================================================
CREATE TABLE IF NOT EXISTS posicoes (
    id SERIAL PRIMARY KEY,
    ativo_id INTEGER NOT NULL UNIQUE REFERENCES ativos(id) ON DELETE CASCADE,
    quantidade_total INTEGER DEFAULT 0,
    preco_medio NUMERIC(12, 4) DEFAULT 0,
    preco_atual NUMERIC(12, 4) DEFAULT 0,
    resultado_dia NUMERIC(15, 2) DEFAULT 0,
    resultado_acumulado NUMERIC(15, 2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_posicoes_ativo_id ON posicoes(ativo_id);

\echo '✅ Tabla posicoes creada/verificada'

-- ============================================================================
-- FUNCIÓN: Actualizar timestamp
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================================================
-- TRIGGERS: Para actualizar updated_at automáticamente
-- ============================================================================
DROP TRIGGER IF EXISTS update_ativos_updated_at ON ativos;
CREATE TRIGGER update_ativos_updated_at
    BEFORE UPDATE ON ativos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_posicoes_updated_at ON posicoes;
CREATE TRIGGER update_posicoes_updated_at
    BEFORE UPDATE ON posicoes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

\echo '✅ Triggers de updated_at configurados'

-- ============================================================================
-- DATOS DE EJEMPLO (OPCIONAL)
-- ============================================================================
INSERT INTO ativos (ticker, nome, ativo) VALUES 
    ('AAPL', 'Apple Inc.', true),
    ('MSFT', 'Microsoft Corporation', true),
    ('GOOGL', 'Alphabet Inc.', true),
    ('AMZN', 'Amazon.com Inc.', true),
    ('TSLA', 'Tesla Inc.', true)
ON CONFLICT (ticker) DO NOTHING;

\echo '✅ Dados de exemplo inseridos'

-- ============================================================================
-- VERIFICACIÓN FINAL
-- ============================================================================
\echo ''
\echo '📊 RESUMEN DE TABLAS CREADAS:'
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

\echo ''
\echo '🎉 Base de datos BolsaV1 configurada correctamente!'
\echo '📝 Tablas: ativos, precos_diarios, operacoes, posicoes'
\echo '🔗 Indices y triggers configurados'
\echo '📈 Datos de ejemplo incluidos'
\echo ''