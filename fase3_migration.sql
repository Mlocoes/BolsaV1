-- ============================================================================
-- MIGRACIÓN FASE 3: Sistema de Autenticación y Multi-tenant
-- BolsaV1 v3.0.0
-- ============================================================================

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    avatar_url VARCHAR(255),
    bio TEXT
);

-- Crear tabla de sesiones de usuario
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    device_info VARCHAR(200),
    is_revoked BOOLEAN DEFAULT FALSE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_reason VARCHAR(100)
);

-- Crear índices para performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Agregar columna user_id a tablas existentes (si no existe)
ALTER TABLE ativos ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE operacoes ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE posicoes ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE precos_diarios ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;

-- Crear índices para multi-tenancy
CREATE INDEX IF NOT EXISTS idx_ativos_user_id ON ativos(user_id);
CREATE INDEX IF NOT EXISTS idx_operacoes_user_id ON operacoes(user_id);
CREATE INDEX IF NOT EXISTS idx_posicoes_user_id ON posicoes(user_id);
CREATE INDEX IF NOT EXISTS idx_precos_diarios_user_id ON precos_diarios(user_id);

-- Eliminar constraint único anterior de ticker (ahora único por usuario)
ALTER TABLE ativos DROP CONSTRAINT IF EXISTS ativos_ticker_key;

-- Eliminar constraint único anterior de ativo_id en posicoes
ALTER TABLE posicoes DROP CONSTRAINT IF EXISTS posicoes_ativo_id_key;

-- Crear constraints únicos por usuario
ALTER TABLE ativos ADD CONSTRAINT IF NOT EXISTS unique_ticker_per_user 
    UNIQUE (ticker, user_id);
    
ALTER TABLE posicoes ADD CONSTRAINT IF NOT EXISTS unique_position_per_user 
    UNIQUE (ativo_id, user_id);
    
ALTER TABLE precos_diarios ADD CONSTRAINT IF NOT EXISTS unique_price_per_asset_date_user 
    UNIQUE (ativo_id, data, user_id);

-- Crear usuario administrador por defecto (solo si no existe ningún usuario)
DO $$
BEGIN
    -- Solo crear admin si no hay usuarios existentes
    IF NOT EXISTS (SELECT 1 FROM users LIMIT 1) THEN
        INSERT INTO users (
            username, 
            email, 
            hashed_password, 
            full_name, 
            is_active, 
            is_admin
        ) VALUES (
            'admin',
            'admin@bolsav1.com',
            '$2b$12$LQv3c1yqBwlVHpfXiRfuauN6wdQFYFi8.gPQkf8V4j5v4i1J8J8Qq', -- 'admin123'
            'Administrador',
            TRUE,
            TRUE
        );
        
        -- Migrar datos existentes al usuario admin (user_id = 1)
        UPDATE ativos SET user_id = 1 WHERE user_id IS NULL;
        UPDATE operacoes SET user_id = 1 WHERE user_id IS NULL;
        UPDATE posicoes SET user_id = 1 WHERE user_id IS NULL;
        UPDATE precos_diarios SET user_id = 1 WHERE user_id IS NULL;
        
        RAISE NOTICE 'Usuario admin creado y datos migrados';
    ELSE
        RAISE NOTICE 'Ya existen usuarios, migración omitida';
    END IF;
END
$$;

-- Hacer user_id NOT NULL después de la migración
ALTER TABLE ativos ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE operacoes ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE posicoes ALTER COLUMN user_id SET NOT NULL;
-- precos_diarios puede tener user_id NULL para precios globales

-- Crear función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Crear trigger para actualizar updated_at en users
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Crear función para limpiar sesiones expiradas
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions 
    WHERE expires_at < CURRENT_TIMESTAMP 
    OR is_revoked = TRUE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Comentarios en las tablas
COMMENT ON TABLE users IS 'Tabla de usuarios del sistema con autenticación';
COMMENT ON TABLE user_sessions IS 'Sesiones activas de usuarios para control de acceso';
COMMENT ON COLUMN users.hashed_password IS 'Contraseña hasheada con bcrypt';
COMMENT ON COLUMN user_sessions.session_id IS 'ID único de sesión para autenticación';
COMMENT ON COLUMN ativos.user_id IS 'ID del usuario propietario del activo';
COMMENT ON COLUMN operacoes.user_id IS 'ID del usuario que realizó la operación';
COMMENT ON COLUMN posicoes.user_id IS 'ID del usuario propietario de la posición';

-- Crear vista para estadísticas de usuarios (solo admin)
CREATE OR REPLACE VIEW user_statistics AS
SELECT 
    COUNT(*) as total_users,
    COUNT(*) FILTER (WHERE is_active = TRUE) as active_users,
    COUNT(*) FILTER (WHERE is_admin = TRUE) as admin_users,
    COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '30 days') as recent_registrations,
    COUNT(*) FILTER (WHERE last_login >= CURRENT_DATE - INTERVAL '7 days') as recent_logins
FROM users;

-- Mensaje final
DO $$
BEGIN
    RAISE NOTICE '✅ Migración FASE 3 completada exitosamente';
    RAISE NOTICE '🔐 Sistema de autenticación y multi-tenant activado';
    RAISE NOTICE '👤 Usuario admin creado con credenciales: admin / admin123';
    RAISE NOTICE '🔧 Recuerde cambiar la contraseña del admin en producción';
END
$$;