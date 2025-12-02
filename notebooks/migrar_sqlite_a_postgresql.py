#!/usr/bin/env python3
"""
Script de migración de SQLite a PostgreSQL
Migra la base de datos de criminalidad con esquema optimizado
Usa variables de entorno desde archivo .env
"""

import sqlite3
import psycopg2
from psycopg2 import sql
import pandas as pd
from datetime import datetime
import sys
import os
from pathlib import Path

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Variables de entorno cargadas desde .env")
except ImportError:
    print("⚠️  python-dotenv no instalado. Usando variables de entorno del sistema.")
    print("   Instala con: pip install python-dotenv")

# ============================================================================
# CONFIGURACIÓN DESDE VARIABLES DE ENTORNO
# ============================================================================

SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', '../data/delitos_raw.db')

# Configuración PostgreSQL desde variables de entorno
PG_CONFIG = {
    'host': os.getenv('PG_HOST', 'localhost'),
    'port': int(os.getenv('PG_PORT', 5432)),
    'database': os.getenv('PG_DATABASE'),
    'user': os.getenv('PG_USER'),
    'password': os.getenv('PG_PASSWORD')
}

# Validar que las credenciales estén configuradas
if not PG_CONFIG['user'] or not PG_CONFIG['password']:
    print("\n" + "="*80)
    print("❌ ERROR: Credenciales de PostgreSQL no configuradas")
    print("="*80)
    print("\nPor favor, configura las variables de entorno:")
    print("  1. Copia el archivo .env.example a .env")
    print("  2. Edita .env y configura PG_USER y PG_PASSWORD")
    print("\nO ejecuta:")
    print("  export PG_USER='tu_usuario'")
    print("  export PG_PASSWORD='tu_password'")
    print("\n" + "="*80 + "\n")
    sys.exit(1)

# ============================================================================
# ESQUEMA POSTGRESQL OPTIMIZADO
# ============================================================================

SCHEMA_SQL = """
-- ============================================================================
-- TABLA: delitos_aux (tabla principal)
-- ============================================================================
CREATE TABLE IF NOT EXISTS delitos_aux (
    id SERIAL PRIMARY KEY,
    periodo DATE NOT NULL,
    geo VARCHAR(255) NOT NULL,
    tipo VARCHAR(255) NOT NULL,
    valor_acumulado INTEGER,
    valor NUMERIC(12,2),
    pob INTEGER,
    tasa NUMERIC(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_delitos_periodo ON delitos_aux(periodo);
CREATE INDEX IF NOT EXISTS idx_delitos_geo ON delitos_aux(geo);
CREATE INDEX IF NOT EXISTS idx_delitos_tipo ON delitos_aux(tipo);
CREATE INDEX IF NOT EXISTS idx_delitos_periodo_geo ON delitos_aux(periodo, geo);
CREATE INDEX IF NOT EXISTS idx_delitos_periodo_tipo ON delitos_aux(periodo, tipo);
CREATE INDEX IF NOT EXISTS idx_delitos_composite ON delitos_aux(periodo, geo, tipo);

-- ============================================================================
-- TABLA: delitos (tabla raw original)
-- ============================================================================
CREATE TABLE IF NOT EXISTS delitos (
    id SERIAL PRIMARY KEY,
    geografia TEXT,
    tipologia_penal TEXT,
    periodo TEXT,
    total TEXT,
    fichero INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_delitos_raw_fichero ON delitos(fichero);
CREATE INDEX IF NOT EXISTS idx_delitos_raw_periodo ON delitos(periodo);

-- ============================================================================
-- TABLA: pob_municipios
-- ============================================================================
CREATE TABLE IF NOT EXISTS pob_municipios (
    id SERIAL PRIMARY KEY,
    provincia VARCHAR(100),
    nombre VARCHAR(255),
    pob INTEGER,
    anio INTEGER,
    cod_mun VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pob_mun_codigo ON pob_municipios(cod_mun);
CREATE INDEX IF NOT EXISTS idx_pob_mun_anio ON pob_municipios(anio);
CREATE INDEX IF NOT EXISTS idx_pob_mun_codigo_anio ON pob_municipios(cod_mun, anio);

-- ============================================================================
-- TABLA: diccionario_municipios
-- ============================================================================
CREATE TABLE IF NOT EXISTS diccionario_municipios (
    id SERIAL PRIMARY KEY,
    geo_mun_unique VARCHAR(100) UNIQUE,
    cp_pk_tab_pob VARCHAR(10)
);

CREATE INDEX IF NOT EXISTS idx_dict_mun_geo ON diccionario_municipios(geo_mun_unique);
CREATE INDEX IF NOT EXISTS idx_dict_mun_cp ON diccionario_municipios(cp_pk_tab_pob);

-- ============================================================================
-- TABLA: pob_ccaa
-- ============================================================================
CREATE TABLE IF NOT EXISTS pob_ccaa (
    id SERIAL PRIMARY KEY,
    codccaa VARCHAR(5),
    ccaa VARCHAR(100),
    anio INTEGER,
    pob INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pob_ccaa_codigo ON pob_ccaa(codccaa);
CREATE INDEX IF NOT EXISTS idx_pob_ccaa_anio ON pob_ccaa(anio);
CREATE UNIQUE INDEX IF NOT EXISTS idx_pob_ccaa_unique ON pob_ccaa(codccaa, anio);

-- ============================================================================
-- TABLA: pob_provincias
-- ============================================================================
CREATE TABLE IF NOT EXISTS pob_provincias (
    id SERIAL PRIMARY KEY,
    cpro VARCHAR(5),
    provincia VARCHAR(100),
    anio INTEGER,
    pob INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pob_prov_codigo ON pob_provincias(cpro);
CREATE INDEX IF NOT EXISTS idx_pob_prov_anio ON pob_provincias(anio);
CREATE UNIQUE INDEX IF NOT EXISTS idx_pob_prov_unique ON pob_provincias(cpro, anio);

-- ============================================================================
-- VISTAS ÚTILES
-- ============================================================================

-- Vista con datos listos para la app (similar al procesamiento de Streamlit)
CREATE OR REPLACE VIEW v_delitos_app AS
SELECT 
    id,
    periodo,
    geo,
    tipo,
    valor,
    tasa,
    CASE 
        WHEN geo ~ '^[0-9]{5}' THEN 'municipio'
        WHEN geo LIKE 'Provincia%' THEN 'provincia'
        WHEN geo LIKE 'CCAA%' THEN 'ccaa'
        ELSE 'otros'
    END as tipo_geo,
    CASE 
        WHEN geo ~ '^[0-9]{5}' THEN SUBSTRING(geo, 1, 5)
        WHEN geo LIKE 'Provincia%' THEN SPLIT_PART(geo, ' ', 2)
        WHEN geo LIKE 'CCAA%' THEN SPLIT_PART(geo, ' ', 2)
        ELSE NULL
    END as codigo_geo,
    CASE 
        WHEN geo ~ '^[0-9]{5}' THEN SUBSTRING(geo, 7)
        WHEN geo LIKE 'Provincia%' THEN SUBSTRING(geo, POSITION(' ' IN geo) + 3)
        WHEN geo LIKE 'CCAA%' THEN SUBSTRING(geo, POSITION(' ' IN geo) + 3)
        ELSE geo
    END as nombre_geo,
    TO_CHAR(periodo, 'TQ YYYY') as periodo_display,
    EXTRACT(YEAR FROM periodo) as year,
    EXTRACT(QUARTER FROM periodo) as quarter
FROM delitos_aux;

-- Vista de estadísticas por periodo y tipo
CREATE OR REPLACE VIEW v_estadisticas_delitos AS
SELECT 
    periodo,
    tipo,
    COUNT(*) as total_registros,
    SUM(valor) as suma_valor,
    AVG(valor) as promedio_valor,
    AVG(tasa) as promedio_tasa,
    MIN(valor) as min_valor,
    MAX(valor) as max_valor
FROM delitos_aux
WHERE valor IS NOT NULL
GROUP BY periodo, tipo
ORDER BY periodo DESC, tipo;

-- Comentarios en las tablas
COMMENT ON TABLE delitos_aux IS 'Tabla principal con datos de criminalidad procesados';
COMMENT ON TABLE delitos IS 'Tabla raw original de delitos sin procesar';
COMMENT ON TABLE pob_municipios IS 'Población de municipios por año';
COMMENT ON TABLE pob_ccaa IS 'Población de comunidades autónomas por año';
COMMENT ON TABLE pob_provincias IS 'Población de provincias por año';
COMMENT ON TABLE diccionario_municipios IS 'Mapeo de códigos de municipios';
"""

# ============================================================================
# FUNCIONES DE MIGRACIÓN
# ============================================================================

def log(msg, tipo="INFO"):
    """Imprime mensajes con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    simbolo = {
        "INFO": "ℹ️",
        "OK": "✅",
        "ERROR": "❌",
        "WARN": "⚠️",
        "PROGRESS": "🔄"
    }.get(tipo, "•")
    print(f"[{timestamp}] {simbolo} {msg}")

def mostrar_configuracion():
    """Muestra la configuración actual (sin mostrar password)"""
    print("\n" + "="*80)
    print("  CONFIGURACIÓN")
    print("="*80)
    print(f"\nSQLite:")
    print(f"  Ruta: {SQLITE_DB_PATH}")
    print(f"\nPostgreSQL:")
    print(f"  Host: {PG_CONFIG['host']}")
    print(f"  Port: {PG_CONFIG['port']}")
    print(f"  Database: {PG_CONFIG['database']}")
    print(f"  User: {PG_CONFIG['user']}")
    print(f"  Password: {'*' * len(PG_CONFIG['password']) if PG_CONFIG['password'] else 'NO CONFIGURADO'}")
    print("="*80 + "\n")

def conectar_postgresql():
    """Conecta a PostgreSQL"""
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        log(f"Conectado a PostgreSQL: {PG_CONFIG['database']}", "OK")
        return conn
    except Exception as e:
        log(f"Error conectando a PostgreSQL: {e}", "ERROR")
        sys.exit(1)

def crear_base_datos():
    """Crea la base de datos si no existe"""
    try:
        # Conectar a postgres (base de datos por defecto)
        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database='postgres',
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Verificar si existe
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (PG_CONFIG['database'],)
        )
        existe = cursor.fetchone()
        
        if not existe:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(PG_CONFIG['database'])
                )
            )
            log(f"Base de datos '{PG_CONFIG['database']}' creada", "OK")
        else:
            log(f"Base de datos '{PG_CONFIG['database']}' ya existe", "INFO")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        log(f"Error creando base de datos: {e}", "ERROR")
        sys.exit(1)

def crear_esquema(pg_conn):
    """Crea el esquema de tablas en PostgreSQL"""
    try:
        cursor = pg_conn.cursor()
        log("Creando esquema de tablas...", "PROGRESS")
        cursor.execute(SCHEMA_SQL)
        pg_conn.commit()
        log("Esquema creado exitosamente", "OK")
        cursor.close()
    except Exception as e:
        log(f"Error creando esquema: {e}", "ERROR")
        pg_conn.rollback()
        sys.exit(1)

def migrar_tabla(sqlite_conn, pg_conn, tabla_sqlite, tabla_pg, mapeo_columnas=None):
    """
    Migra una tabla de SQLite a PostgreSQL
    
    Args:
        mapeo_columnas: dict con mapeo de nombres de columnas si son diferentes
                       ejemplo: {'Geografía': 'geografia', 'Periodos:': 'periodo'}
    """
    try:
        log(f"Migrando tabla '{tabla_sqlite}' → '{tabla_pg}'...", "PROGRESS")
        
        # Leer desde SQLite
        df = pd.read_sql_query(f"SELECT * FROM {tabla_sqlite}", sqlite_conn)
        log(f"  Leídos {len(df):,} registros de SQLite", "INFO")
        
        # Aplicar mapeo de columnas si existe
        if mapeo_columnas:
            df.rename(columns=mapeo_columnas, inplace=True)
        
        # Escribir a PostgreSQL
        if len(df) > 0:
            # Limpiar tabla si existe
            cursor = pg_conn.cursor()
            cursor.execute(f"TRUNCATE TABLE {tabla_pg} RESTART IDENTITY CASCADE")
            pg_conn.commit()
            
            # Insertar datos usando COPY (mucho más rápido que INSERT)
            from io import StringIO
            
            buffer = StringIO()
            df.to_csv(buffer, index=False, header=False, sep='\t', na_rep='\\N')
            buffer.seek(0)
            
            columnas = ', '.join([f'"{col}"' if col != col.lower() else col for col in df.columns])
            cursor.copy_from(buffer, tabla_pg, sep='\t', null='\\N', columns=df.columns.tolist())
            pg_conn.commit()
            
            log(f"  ✓ Migrados {len(df):,} registros a PostgreSQL", "OK")
            cursor.close()
        else:
            log(f"  ⚠️ Tabla vacía, no se migró nada", "WARN")
            
    except Exception as e:
        log(f"Error migrando tabla '{tabla_sqlite}': {e}", "ERROR")
        pg_conn.rollback()
        raise

def validar_migracion(sqlite_conn, pg_conn):
    """Valida que la migración fue correcta comparando conteos"""
    log("\n" + "="*80, "INFO")
    log("VALIDACIÓN DE MIGRACIÓN", "INFO")
    log("="*80, "INFO")
    
    tablas = [
        'delitos',
        'delitos_aux',
        'pob_municipios',
        'diccionario_municipios',
        'pob_ccaa',
        'pob_provincias'
    ]
    
    todo_ok = True
    
    for tabla in tablas:
        # Contar en SQLite
        cursor_sqlite = sqlite_conn.cursor()
        cursor_sqlite.execute(f"SELECT COUNT(*) FROM {tabla}")
        count_sqlite = cursor_sqlite.fetchone()[0]
        
        # Contar en PostgreSQL
        cursor_pg = pg_conn.cursor()
        cursor_pg.execute(f"SELECT COUNT(*) FROM {tabla}")
        count_pg = cursor_pg.fetchone()[0]
        
        if count_sqlite == count_pg:
            log(f"✓ {tabla:25} SQLite: {count_sqlite:>8,} | PostgreSQL: {count_pg:>8,}", "OK")
        else:
            log(f"✗ {tabla:25} SQLite: {count_sqlite:>8,} | PostgreSQL: {count_pg:>8,}", "ERROR")
            todo_ok = False
    
    log("="*80, "INFO")
    
    if todo_ok:
        log("¡Migración validada exitosamente!", "OK")
    else:
        log("Hay diferencias en los conteos. Revisa la migración.", "ERROR")
    
    return todo_ok

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    print("\n" + "="*80)
    print("  MIGRACIÓN SQLite → PostgreSQL")
    print("  Base de datos: Criminalidad España")
    print("="*80 + "\n")
    
    # Mostrar configuración
    mostrar_configuracion()
    
    # 1. Conectar a SQLite
    log("Conectando a SQLite...", "PROGRESS")
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        log(f"Conectado a SQLite: {SQLITE_DB_PATH}", "OK")
    except Exception as e:
        log(f"Error conectando a SQLite: {e}", "ERROR")
        sys.exit(1)
    
    # 2. Crear base de datos PostgreSQL
    crear_base_datos()
    
    # 3. Conectar a PostgreSQL
    pg_conn = conectar_postgresql()
    
    # 4. Crear esquema
    crear_esquema(pg_conn)
    
    # 5. Migrar tablas
    log("\n" + "="*80, "INFO")
    log("INICIANDO MIGRACIÓN DE DATOS", "INFO")
    log("="*80 + "\n", "INFO")
    
    try:
        # Tabla delitos (raw)
        migrar_tabla(
            sqlite_conn, pg_conn, 
            'delitos', 'delitos',
            mapeo_columnas={
                'Geografía': 'geografia',
                'Tipología penal': 'tipologia_penal',
                'Periodos:': 'periodo',
                'Total': 'total'
            }
        )
        
        # Tabla delitos_aux (principal)
        migrar_tabla(sqlite_conn, pg_conn, 'delitos_aux', 'delitos_aux')
        
        # Tabla pob_municipios
        migrar_tabla(
            sqlite_conn, pg_conn,
            'pob_municipios', 'pob_municipios',
            mapeo_columnas={
                'PROVINCIA': 'provincia',
                'NOMBRE': 'nombre',
                'POB': 'pob',
                'AÑO': 'anio',
                'cod_mun': 'cod_mun'
            }
        )
        
        # Tabla diccionario_municipios
        migrar_tabla(sqlite_conn, pg_conn, 'diccionario_municipios', 'diccionario_municipios')
        
        # Tabla pob_ccaa
        migrar_tabla(
            sqlite_conn, pg_conn,
            'pob_ccaa', 'pob_ccaa',
            mapeo_columnas={
                'CODCCAA': 'codccaa',
                'CCAA': 'ccaa',
                'AÑO': 'anio',
                'POB': 'pob'
            }
        )
        
        # Tabla pob_provincias
        migrar_tabla(
            sqlite_conn, pg_conn,
            'pob_provincias', 'pob_provincias',
            mapeo_columnas={
                'CPRO': 'cpro',
                'PROVINCIA': 'provincia',
                'AÑO': 'anio',
                'POB': 'pob'
            }
        )
        
        # 6. Validar migración
        validar_migracion(sqlite_conn, pg_conn)
        
        # 7. Mostrar información de las vistas
        log("\n" + "="*80, "INFO")
        log("VISTAS CREADAS", "INFO")
        log("="*80, "INFO")
        log("• v_delitos_app - Datos procesados listos para la aplicación", "INFO")
        log("• v_estadisticas_delitos - Estadísticas agregadas por periodo y tipo", "INFO")
        
        log("\n" + "="*80, "OK")
        log("¡MIGRACIÓN COMPLETADA EXITOSAMENTE!", "OK")
        log("="*80, "OK")
        
    except Exception as e:
        log(f"\n¡Error durante la migración!: {e}", "ERROR")
        sys.exit(1)
    finally:
        sqlite_conn.close()
        pg_conn.close()
        log("\nConexiones cerradas", "INFO")

if __name__ == "__main__":
    main()