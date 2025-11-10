# FASE 3 - Sistema de Autenticación y Multi-usuario

## 🎯 Objetivo
Implementar sistema completo de autenticación, autorización y aislamiento multi-tenant en BolsaV1, permitiendo múltiples usuarios con carteras independientes.

## 🏗️ Diseño del Sistema

### Arquitectura de Seguridad

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CAPA DE AUTENTICACIÓN                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐│
│  │   Streamlit      │    │   Session        │    │   JWT Tokens    ││
│  │   Authentication │────│   Management     │────│   + Cookies     ││
│  │                  │    │                  │    │                 ││
│  └──────────────────┘    └──────────────────┘    └─────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   CAPA DE AUTORIZACIÓN                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐│
│  │   Role-Based     │    │   Permission     │    │   User Context  ││
│  │   Access Control │────│   Checking       │────│   Injection     ││
│  │   (RBAC)         │    │                  │    │                 ││
│  └──────────────────┘    └──────────────────┘    └─────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  CAPA DE DATOS AISLADOS                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐│
│  │   Data Filtering │    │   User Scoped    │    │   Multi-tenant  ││
│  │   por User ID    │────│   Queries        │────│   Isolation     ││
│  │                  │    │                  │    │                 ││
│  └──────────────────┘    └──────────────────┘    └─────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Modelo de Datos Expandido

```sql
-- Nuevas tablas para autenticación
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Modificar tablas existentes para aislamiento multi-tenant
ALTER TABLE ativos ADD COLUMN user_id INTEGER REFERENCES users(id);
ALTER TABLE operacoes ADD COLUMN user_id INTEGER REFERENCES users(id);
ALTER TABLE posicoes ADD COLUMN user_id INTEGER REFERENCES users(id);
ALTER TABLE precos_diarios ADD COLUMN user_id INTEGER REFERENCES users(id);

-- Índices para performance con multi-tenancy
CREATE INDEX idx_ativos_user_id ON ativos(user_id);
CREATE INDEX idx_operacoes_user_id ON operacoes(user_id);
CREATE INDEX idx_posicoes_user_id ON posicoes(user_id);
CREATE INDEX idx_precos_diarios_user_id ON precos_diarios(user_id);
```

## 🔧 Componentes a Implementar

### 1. Modelos de Autenticação (app/models/)
- [x] user.py - Modelo de usuário
- [x] user_session.py - Sesiones de usuario

### 2. Servicios de Autenticação (app/services/)
- [x] auth_service.py - Lógica de autenticación
- [x] user_service.py - CRUD de usuarios
- [x] session_service.py - Gestión de sesiones

### 3. Middleware de Seguridad (app/utils/)
- [x] auth_utils.py - Utilidades de autenticación
- [x] decorators.py - Decoradores de protección
- [x] security.py - Funciones de seguridad

### 4. UI de Autenticación (app/pages/)
- [x] login.py - Página de login
- [x] register.py - Registro de usuarios
- [x] profile.py - Perfil de usuario
- [x] admin.py - Panel administrativo

### 5. Integración con Sistema Existente
- [x] Modificar main.py para manejo de autenticación
- [x] Actualizar servicios existentes para multi-tenancy
- [x] Migrar datos existentes para primer usuario admin

## 🛡️ Características de Seguridad

### Autenticación
- **Hashing de passwords**: bcrypt con salt
- **Session management**: Tokens seguros con expiración
- **Cookie security**: HttpOnly, Secure, SameSite
- **Logout seguro**: Invalidación de sesiones

### Autorización
- **Role-based access**: Admin, User
- **Permission checking**: Decoradores de verificación
- **Resource ownership**: Usuarios solo ven sus datos
- **Admin privileges**: Gestión completa del sistema

### Protección contra Ataques
- **SQL Injection**: SQLAlchemy ORM + parámetros
- **XSS**: Streamlit sanitization + validation
- **CSRF**: SameSite cookies + token validation
- **Session Hijacking**: Secure cookies + IP tracking
- **Brute Force**: Rate limiting + account lockout

## 📊 Flujo de Usuario

### 1. Login Flow
```
Usuario accede → Página Login → Credenciales → Validación → 
Cookie Seguro → Redirección a Dashboard → Session Activa
```

### 2. Multi-tenant Data Access
```
Usuario logueado → Request a Service → User ID injection → 
Query filtrada por User → Datos aislados → Response
```

### 3. Logout Flow
```
Usuario logout → Invalidar session → Limpiar cookies → 
Redireccionar a Login → Session terminada
```

## 🔄 Migración de Datos

### Plan de Migración
1. **Crear usuario admin por defecto** con datos existentes
2. **Migrar datos actuales** al usuario admin (user_id = 1)
3. **Actualizar servicios** para requerir user_id
4. **Mantener compatibilidad** con datos existentes

### Script de Migración
```sql
-- Crear usuario admin por defecto
INSERT INTO users (username, email, hashed_password, full_name, is_admin) 
VALUES ('admin', 'admin@bolsav1.com', '$2b$12$...', 'Administrator', TRUE);

-- Migrar datos existentes al admin
UPDATE ativos SET user_id = 1 WHERE user_id IS NULL;
UPDATE operacoes SET user_id = 1 WHERE user_id IS NULL;
UPDATE posicoes SET user_id = 1 WHERE user_id IS NULL;
UPDATE precos_diarios SET user_id = 1 WHERE user_id IS NULL;
```

## 📱 Experiencia de Usuario

### Para Usuarios Nuevos
1. **Registro simple** con email y password
2. **Dashboard vacío** listo para configurar
3. **Onboarding opcional** con datos demo

### Para Usuario Admin
1. **Panel administrativo** con gestión de usuarios
2. **Métricas del sistema** y monitoreo
3. **Backup y restauración** de datos

### Para Usuarios Existentes
1. **Transición transparente** con auto-login
2. **Datos preservados** sin pérdida
3. **Funcionalidades nuevas** disponibles inmediatamente

## 🧪 Testing Strategy

### Tests de Autenticación
- Login exitoso y fallido
- Registro de usuarios
- Gestión de sesiones
- Logout y cleanup

### Tests de Autorización
- Acceso a recursos propios
- Bloqueo de recursos ajenos
- Verificación de roles
- Permisos de admin

### Tests de Integración
- Flujo completo de usuario
- Multi-tenancy isolation
- Performance con múltiples usuarios
- Security penetration testing

## 📈 Beneficios Esperados

### Para Usuarios
- **Carteras privadas** e independientes
- **Múltiples cuentas** en el mismo sistema
- **Seguridad robusta** de datos personales
- **Experiencia personalizada**

### Para el Sistema
- **Escalabilidad** a múltiples usuarios
- **Monetización** potencial con planes
- **Analytics** de uso por usuario
- **Compliance** con regulaciones de privacidad

### Para Desarrolladores
- **Arquitectura moderna** y escalable
- **Security by design** implementado
- **Testing framework** robusto
- **Documentación completa** de seguridad

## 🎯 Cronograma de Implementación

### Fase 3.1: Fundación (Días 1-2)
- [x] Modelos de autenticación
- [x] Servicios base
- [x] Middleware de seguridad

### Fase 3.2: UI y UX (Días 3-4)
- [x] Páginas de auth
- [x] Integración con main.py
- [x] Flow de usuario

### Fase 3.3: Integración (Días 5-6)
- [x] Multi-tenancy en servicios
- [x] Migración de datos
- [x] Testing exhaustivo

### Fase 3.4: Documentación (Día 7)
- [x] Actualizar documentación
- [x] Guías de seguridad
- [x] Deployment notes

---

**🚀 Ready para implementar FASE 3!**

*Sistema de autenticación enterprise-grade para BolsaV1, manteniendo la simplicidad de uso pero agregando seguridad y escalabilidad profesional.*