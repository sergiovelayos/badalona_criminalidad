#!/usr/bin/env python3
"""
Script para analizar completamente una base de datos SQLite
Extrae: esquema, tablas, tipos de datos, índices, y muestra de datos
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path

def analizar_sqlite(db_path):
    """Analiza completamente una base de datos SQLite"""
    
    print(f"\n{'='*80}")
    print(f"ANÁLISIS DE BASE DE DATOS: {db_path}")
    print(f"{'='*80}\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Obtener lista de tablas
        print("📋 TABLAS EN LA BASE DE DATOS:")
        print("-" * 80)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        
        if not tablas:
            print("❌ No se encontraron tablas en la base de datos")
            return
        
        for tabla in tablas:
            print(f"  • {tabla[0]}")
        
        print(f"\n{'='*80}\n")
        
        # 2. Para cada tabla, obtener información detallada
        for tabla in tablas:
            nombre_tabla = tabla[0]
            print(f"\n📊 TABLA: {nombre_tabla}")
            print("=" * 80)
            
            # 2.1 Schema de la tabla
            print("\n🔧 ESQUEMA:")
            cursor.execute(f"PRAGMA table_info({nombre_tabla});")
            columnas = cursor.fetchall()
            
            print(f"\n{'ID':<5} {'Nombre':<25} {'Tipo':<15} {'Not Null':<10} {'Default':<15} {'PK':<5}")
            print("-" * 80)
            for col in columnas:
                cid, nombre, tipo, notnull, default, pk = col
                notnull_str = "Sí" if notnull else "No"
                pk_str = "Sí" if pk else "No"
                default_str = str(default) if default is not None else "NULL"
                print(f"{cid:<5} {nombre:<25} {tipo:<15} {notnull_str:<10} {default_str:<15} {pk_str:<5}")
            
            # 2.2 Conteo de registros
            cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla};")
            total_registros = cursor.fetchone()[0]
            print(f"\n📈 Total de registros: {total_registros:,}")
            
            # 2.3 Índices
            print("\n🔑 ÍNDICES:")
            cursor.execute(f"PRAGMA index_list({nombre_tabla});")
            indices = cursor.fetchall()
            if indices:
                for idx in indices:
                    print(f"  • {idx[1]} (Único: {'Sí' if idx[2] else 'No'})")
            else:
                print("  Sin índices")
            
            # 2.4 Muestra de datos (primeras 5 filas)
            print("\n📄 MUESTRA DE DATOS (primeras 5 filas):")
            df = pd.read_sql_query(f"SELECT * FROM {nombre_tabla} LIMIT 5", conn)
            print("\n" + df.to_string(index=False))
            
            # 2.5 Estadísticas de columnas numéricas
            print("\n📊 ESTADÍSTICAS (columnas numéricas):")
            df_full = pd.read_sql_query(f"SELECT * FROM {nombre_tabla}", conn)
            numeric_cols = df_full.select_dtypes(include=['number']).columns.tolist()
            
            if numeric_cols:
                stats = df_full[numeric_cols].describe()
                print("\n" + stats.to_string())
            else:
                print("  No hay columnas numéricas")
            
            # 2.6 Valores únicos en columnas categóricas (si hay pocas categorías)
            print("\n🏷️  VALORES ÚNICOS EN COLUMNAS CATEGÓRICAS:")
            categorical_cols = df_full.select_dtypes(include=['object']).columns.tolist()
            
            for col in categorical_cols:
                unique_values = df_full[col].nunique()
                if unique_values < 50:  # Solo mostrar si hay menos de 50 valores únicos
                    print(f"\n  Columna '{col}' ({unique_values} valores únicos):")
                    value_counts = df_full[col].value_counts().head(10)
                    for val, count in value_counts.items():
                        print(f"    • {val}: {count:,} registros")
                else:
                    print(f"\n  Columna '{col}': {unique_values:,} valores únicos (demasiados para mostrar)")
            
            print("\n" + "=" * 80 + "\n")
        
        # 3. SQL de creación de tablas
        print("\n💾 SQL DE CREACIÓN DE TABLAS:")
        print("=" * 80)
        for tabla in tablas:
            nombre_tabla = tabla[0]
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{nombre_tabla}';")
            sql = cursor.fetchone()
            if sql:
                print(f"\n-- Tabla: {nombre_tabla}")
                print(sql[0] + ";")
        
        conn.close()
        
        print(f"\n{'='*80}")
        print("✅ Análisis completado exitosamente")
        print(f"{'='*80}\n")
        
    except sqlite3.Error as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Ruta por defecto
        db_path = "../data/delitos_raw.db"
    
    if not Path(db_path).exists():
        print(f"❌ Error: No se encuentra el archivo '{db_path}'")
        print(f"\nUso: python {sys.argv[0]} <ruta_a_base_de_datos.db>")
        sys.exit(1)
    
    analizar_sqlite(db_path)