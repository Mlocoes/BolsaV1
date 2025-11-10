-- ============================================================================
-- SCRIPT DE INICIALIZACIÓN DE BASE DE DATOS
-- Sistema de Gestión de Valores Cotizados
-- ============================================================================

-- Crear base de datos (ejecutar como superusuario)
CREATE DATABASE stock_management;

-- Conectar a la base de datos
\c stock_management;

-- ============================================================================
-- TABLA: ativos
-- Almacena los valores/acciones que se están siguiendo
-- ============================================================================
CREATE TABLE ativos (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL UNIQUE,
    nome VARCHAR(100),
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ativos_ticker ON ativos(ticker);
CREATE INDEX idx_ativos_ativo ON ativos(ativo);

-- ============================================================================
-- TABLA: precos_diarios
-- Almacena los precios de cierre diarios de cada activo
-- ============================================================================
CREATE TABLE precos_diarios (
    id SERIAL PRIMARY KEY,
    ativo_id INTEGER NOT NULL REFERENCES ativos(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    preco_fechamento NUMERIC(12, 4) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ativo_id, data)
);

CREATE INDEX idx_precos_ativo_id ON precos_diarios(ativo_id);
CREATE INDEX idx_precos_data ON precos_diarios(data);
CREATE INDEX idx_precos_ativo_data ON precos_diarios(ativo_id, data);

-- ============================================================================
-- TABLA: operacoes
-- Registra todas las operaciones de compra y venta
-- ============================================================================
CREATE TABLE operacoes (
    id SERIAL PRIMARY KEY,
    ativo_id INTEGER NOT NULL REFERENCES ativos(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('compra', 'venda')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco NUMERIC(12, 4) NOT NULL CHECK (preco > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_operacoes_ativo_id ON operacoes(ativo_id);
CREATE INDEX idx_operacoes_data ON operacoes(data);
CREATE INDEX idx_operacoes_tipo ON operacoes(tipo);

-- ============================================================================
-- TABLA: posicoes
-- Almacena la posición consolidada de cada activo
-- ============================================================================
CREATE TABLE posicoes (
    id SERIAL PRIMARY KEY,
    ativo_id INTEGER NOT NULL UNIQUE REFERENCES ativos(id) ON DELETE CASCADE,
    quantidade_total INTEGER DEFAULT 0,
    preco_medio NUMERIC(12, 4) DEFAULT 0,
    preco_atual NUMERIC(12, 4) DEFAULT 0,
    resultado_dia NUMERIC(12, 4) DEFAULT 0,
    resultado_acumulado NUMERIC(12, 4) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posicoes_ativo_id ON posicoes(ativo_id);

-- ============================================================================
-- FUNCIONES Y TRIGGERS
-- ============================================================================

-- Función para actualizar el timestamp de updated_at
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para actualizar automáticamente updated_at
CREATE TRIGGER update_ativos_timestamp
    BEFORE UPDATE ON ativos
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_posicoes_timestamp
    BEFORE UPDATE ON posicoes
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- ============================================================================
-- VISTAS ÚTILES
-- ============================================================================

-- Vista con información completa de posiciones
CREATE OR REPLACE VIEW v_posicoes_completas AS
SELECT 
    p.id,
    a.ticker,
    a.nome,
    p.quantidade_total,
    p.preco_medio,
    p.preco_atual,
    (p.quantidade_total * p.preco_medio) AS financeiro_compra,
    (p.quantidade_total * p.preco_atual) AS financeiro_atual,
    p.resultado_dia,
    p.resultado_acumulado,
    CASE 
        WHEN p.quantidade_total * p.preco_medio > 0 
        THEN ((p.resultado_acumulado / (p.quantidade_total * p.preco_medio)) * 100)
        ELSE 0 
    END AS rentabilidade_pct,
    p.updated_at
FROM posicoes p
JOIN ativos a ON p.ativo_id = a.id
WHERE p.quantidade_total > 0
ORDER BY p.resultado_acumulado DESC;

-- Vista con resumen de operaciones por activo
CREATE OR REPLACE VIEW v_resumo_operacoes AS
SELECT 
    a.ticker,
    a.nome,
    COUNT(o.id) AS total_operacoes,
    SUM(CASE WHEN o.tipo = 'compra' THEN o.quantidade ELSE 0 END) AS total_comprado,
    SUM(CASE WHEN o.tipo = 'venda' THEN o.quantidade ELSE 0 END) AS total_vendido,
    SUM(CASE WHEN o.tipo = 'compra' THEN o.quantidade * o.preco ELSE 0 END) AS valor_compras,
    SUM(CASE WHEN o.tipo = 'venda' THEN o.quantidade * o.preco ELSE 0 END) AS valor_vendas,
    MIN(o.data) AS primeira_operacao,
    MAX(o.data) AS ultima_operacao
FROM ativos a
LEFT JOIN operacoes o ON a.id = o.ativo_id
GROUP BY a.ticker, a.nome;

-- ============================================================================
-- DATOS DE EJEMPLO (OPCIONAL)
-- ============================================================================

-- Descomentar para insertar datos de prueba
/*
INSERT INTO ativos (ticker, nome, ativo) VALUES
('AAPL', 'Apple Inc.', TRUE),
('MSFT', 'Microsoft Corporation', TRUE),
('GOOGL', 'Alphabet Inc.', TRUE),
('TSLA', 'Tesla Inc.', TRUE),
('AMZN', 'Amazon.com Inc.', TRUE);

INSERT INTO operacoes (ativo_id, data, tipo, quantidade, preco) VALUES
(1, '2024-01-15', 'compra', 10, 185.50),
(1, '2024-02-20', 'compra', 5, 190.25),
(2, '2024-01-20', 'compra', 8, 380.00),
(3, '2024-01-25', 'compra', 15, 140.75),
(4, '2024-02-01', 'compra', 20, 195.30);
*/

-- ============================================================================
-- CONSULTAS ÚTILES PARA VERIFICACIÓN
-- ============================================================================

-- Verificar todas las tablas creadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Verificar todas las vistas creadas
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'public';

-- Contar registros en cada tabla
SELECT 
    'ativos' AS tabla, COUNT(*) AS registros FROM ativos
UNION ALL
SELECT 'precos_diarios', COUNT(*) FROM precos_diarios
UNION ALL
SELECT 'operacoes', COUNT(*) FROM operacoes
UNION ALL
SELECT 'posicoes', COUNT(*) FROM posicoes;

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================