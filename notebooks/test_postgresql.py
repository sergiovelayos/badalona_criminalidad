#!/usr/bin/env python3
"""
Script de prueba de conexión a PostgreSQL
Ejecuta este script ANTES de la migración para verificar que todo está configurado
Usa variables de entorno desde archivo .env
"""

import psycopg2
import sys
import os

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Variables de entorno cargadas desde .env\n")
except ImportError:
    print("⚠️  python-dotenv no instalado. Usando variables de entorno del sistema.")
    print("   Instala con: pip install python-dotenv\n")

# ============================================================================
# CONFIGURACIÓN DESDE VARIABLES DE ENTORNO
# ============================================================================
PG_CONFIG = {
    'host': os.getenv('PG_HOST', 'localhost'),
    'port': int(os.getenv('PG_PORT', 5432)),
    'database': 'postgres',  # Conectamos a postgres por defecto para probar
    'user': os.getenv('PG_USER'),
    'password': os.getenv('PG_PASSWORD')
}

# Validar que las credenciales estén configuradas
if not PG_CONFIG['user'] or not PG_CONFIG['password']:
    print("="*80)
    print("❌ ERROR: Credenciales de PostgreSQL no configuradas")
    print("="*80)
    print("\nPor favor, configura las variables de entorno:")
    print("  1. Copia el archivo .env.example a .env")
    print("  2. Edita .env y configura PG_USER y PG_PASSWORD")
    print("\nO ejecuta:")
    print("  export PG_USER='tu_usuario'")
    print("  export PG_PASSWORD='tu_password'")
    print("="*80 + "\n")
    sys.exit(1)

def test_connection():
    """Prueba la conexión a PostgreSQL"""
    print("\n" + "="*80)
    print("  TEST DE CONEXIÓN A POSTGRESQL")
    print("="*80 + "\n")
    
    print("Intentando conectar con los siguientes parámetros:")
    print(f"  Host: {PG_CONFIG['host']}")
    print(f"  Port: {PG_CONFIG['port']}")
    print(f"  Database: {PG_CONFIG['database']}")
    print(f"  User: {PG_CONFIG['user']}")
    print(f"  Password: {'*' * len(PG_CONFIG['password'])}")
    print()
    
    try:
        # Intentar conexión
        print("🔄 Conectando...")
        conn = psycopg2.connect(**PG_CONFIG)
        print("✅ ¡Conexión exitosa!\n")
        
        # Obtener información del servidor
        cursor = conn.cursor()
        
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📊 Versión de PostgreSQL:")
        print(f"   {version}\n")
        
        # Verificar permisos
        cursor.execute("""
            SELECT has_database_privilege(current_user, 'postgres', 'CREATE');
        """)
        puede_crear_db = cursor.fetchone()[0]
        
        if puede_crear_db:
            print("✅ El usuario tiene permisos para crear bases de datos")
        else:
            print("⚠️  El usuario NO tiene permisos para crear bases de datos")
            print("   Ejecuta: ALTER USER {} CREATEDB;".format(PG_CONFIG['user']))
        
        # Listar bases de datos existentes
        cursor.execute("""
            SELECT datname FROM pg_database 
            WHERE datistemplate = false 
            ORDER BY datname;
        """)
        databases = cursor.fetchall()
        
        print(f"\n📋 Bases de datos existentes ({len(databases)}):")
        for db in databases:
            print(f"   • {db[0]}")
        
        # Verificar si ya existe la base de datos objetivo
        cursor.execute("""
            SELECT 1 FROM pg_database WHERE datname = 'criminalidad_espana';
        """)
        existe_target_db = cursor.fetchone()
        
        if existe_target_db:
            print("\n⚠️  La base de datos 'criminalidad_espana' YA EXISTE")
            print("   El script de migración la recreará (se borrarán datos existentes)")
        else:
            print("\n✅ La base de datos 'criminalidad_espana' NO existe (se creará durante migración)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80)
        print("✅ TODO CORRECTO - LISTO PARA MIGRAR")
        print("="*80 + "\n")
        
        print("Siguiente paso:")
        print("  python migrar_sqlite_a_postgresql.py")
        print()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión: {e}\n")
        print("Posibles soluciones:")
        print("  1. Verificar que PostgreSQL está corriendo:")
        print("     sudo systemctl status postgresql")
        print()
        print("  2. Verificar usuario y contraseña:")
        print("     sudo -u postgres psql")
        print("     CREATE USER tu_usuario WITH PASSWORD 'tu_password';")
        print("     ALTER USER tu_usuario CREATEDB;")
        print()
        print("  3. Verificar que el puerto 5432 está abierto:")
        print("     netstat -tuln | grep 5432")
        print()
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}\n")
        return False

if __name__ == "__main__":
    exito = test_connection()
    sys.exit(0 if exito else 1)