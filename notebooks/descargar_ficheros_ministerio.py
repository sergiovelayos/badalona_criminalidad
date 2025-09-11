import os
import time
import csv
import requests
from datetime import datetime

CARPETA = "/Users/macmini/Public/badalona_criminalidad/data/descargas_portal_ministerio"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Referer": "https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/"
}

BASE = "https://estadisticasdecriminalidad.ses.mir.es/sec/jaxiPx/files/_px/es"

def codigo_ant(anio: int, trimestre: int) -> str:
    """Códigos para DatosBalanceAnt"""
    sufijo = f"{trimestre * 3:03d}"  # 003, 006, 009, 012
    if anio <= 2019:
        base = f"{anio % 10}9"       # 2017->79, 2018->89, 2019->99
    else:
        base = f"{anio - 2010}09"    # 2020->1009, 2021->1109, etc.
    return f"{base}{sufijo}"

def codigo_act(trimestre: int) -> str:
    """Códigos para DatosBalanceAct (siempre empiezan en 09...)"""
    sufijo = f"{trimestre * 3:03d}"  # 003, 006, 009, 012
    return f"09{sufijo}"

def construir_urls(anio: int, trimestre: int, anio_actual: int):
    if anio < anio_actual:
        codigo = codigo_ant(anio, trimestre)
        return [
            (f"{BASE}/csv/DatosBalanceAnt/l0/{codigo}.csv?nocab=1", ".csv"),
            (f"{BASE}/csv_bdsc/DatosBalanceAnt/l0/{codigo}.csv_bdsc?nocab=1", ".csv")
        ]
    else:  # Año en curso
        codigo = codigo_act(trimestre)
        return [
            (f"{BASE}/csv/DatosBalanceAct/l0/{codigo}.csv?nocab=1", ".csv"),
            (f"{BASE}/csv_bdsc/DatosBalanceAct/l0/{codigo}.csv_bdsc?nocab=1", ".csv")
        ]

def es_html(res: requests.Response) -> bool:
    ct = (res.headers.get("Content-Type") or "").lower()
    if "text/html" in ct:
        return True
    head = res.content[:200].lstrip().lower()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html")

def descargar_uno(anio: int, trim: int, carpeta: str, anio_actual: int):
    nombre = f"{anio}_{trim}_municipios.csv"
    destino = os.path.join(carpeta, nombre)

    for url, _ in construir_urls(anio, trim, anio_actual):
        try:
            r = requests.get(url, headers=HEADERS, timeout=40)
            if r.status_code == 200 and not es_html(r):
                with open(destino, "wb") as f:
                    f.write(r.content)
                return url, destino, len(r.content)
        except requests.RequestException:
            pass
    return None, destino, 0

def descargar_datos(inicio_anio=2017, fin_anio=2025, fin_trimestre=2, carpeta=CARPETA, pausa=0.6):
    os.makedirs(carpeta, exist_ok=True)
    indice_path = os.path.join(carpeta, "index.csv")
    nueva_tabla = not os.path.exists(indice_path)
    anio_actual = datetime.now().year

    with open(indice_path, "a", newline="", encoding="utf-8") as idx:
        w = csv.writer(idx)
        if nueva_tabla:
            w.writerow(["anio", "trimestre", "url_ok", "fichero_local", "bytes"])
        for anio in range(inicio_anio, fin_anio + 1):
            max_trim = 4 if anio < fin_anio else fin_trimestre
            for trim in range(1, max_trim + 1):
                url_ok, fichero, nbytes = descargar_uno(anio, trim, carpeta, anio_actual)
                w.writerow([anio, trim, url_ok or "", fichero, nbytes])
                if url_ok and nbytes > 0:
                    print(f"✅ {anio}_T{trim}: OK ({nbytes} bytes)")
                else:
                    print(f"⚠️  {anio}_T{trim}: NO ENCONTRADO ({fichero})")
                time.sleep(pausa)

# Ejecutar ejemplo
if __name__ == "__main__":
    descargar_datos(inicio_anio=2017, fin_anio=2025, fin_trimestre=2)
