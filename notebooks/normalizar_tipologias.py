import pandas as pd
import matplotlib.pyplot as plt
pd.set_option("display.max_columns", None)

csv_file = r"./data/esp_desagg_ytd.csv"

df = pd.read_csv(csv_file)


TIPOLOGIA_NORMALIZAR = {
    # Criminalidad convencional
    "1.-Homicidios dolosos y asesinatos consumados": "1. Homicidios dolosos y asesinatos consumados",
    "2.-HOMICIDIOS DOLOSOS Y ASESINATOS CONSUMADOS (EU)": "1. Homicidios dolosos y asesinatos consumados",

    "2.-Homicidios dolosos y asesinatos en grado tentativa": "2. Homicidios dolosos y asesinatos en grado tentativa",

    "3.-Delitos graves y menos graves de lesiones y riña tumultuaria": "3. Delitos graves y menos graves de lesiones y riña tumultuaria",

    "4.-Secuestro": "4. Secuestro",

    # Libertad sexual
    "5.-Delitos contra la libertad e indemnidad sexual": "5. Delitos contra la libertad sexual",
    "5.-Delitos contra la libertad sexual": "5. Delitos contra la libertad sexual",

    "5.1.-Agresión sexual con penetración": "5.1.-Agresión sexual con penetración",
    "5.2.-Resto de delitos contra la libertad e indemnidad sexual": "5.2.-Resto de delitos contra la libertad sexual",
    "5.2.-Resto de delitos contra la libertad sexual": "5.2.-Resto de delitos contra la libertad sexual",

    # Robos con violencia
    "6.-Robos con violencia e intimidación": "6. Robos con violencia e intimidación",
    "3.-ROBO CON VIOLENCIA E INTIMIDACIÓN (EU)": "6. Robos con violencia e intimidación",

    # Robos con fuerza
    "7.- Robos con fuerza en domicilios, establecimientos y otras instalaciones": "7. Robos con fuerza en domicilios, establecimientos y otras instalaciones",
    "4.-ROBOS CON FUERZA EN DOMICILIOS (EU)": "7.1.-Robos con fuerza en domicilios",

    "7.1.-Robos con fuerza en domicilios": "7.1.-Robos con fuerza en domicilios",

    # Hurtos
    "8.-Hurtos": "8. Hurtos",
    "8.-HURTOS": "8. Hurtos",

    # Sustracciones
    "9.-Sustracciones de vehículos": "9. Sustracciones de vehículos",
    "5.-SUSTRACCIÓN VEHÍCULOS A MOTOR (EU)": "9. Sustracciones de vehículos",

    # Tráfico de drogas
    "10.-Tráfico de drogas": "10. Tráfico de drogas",
    "6.-TRÁFICO DE DROGAS (EU)": "10. Tráfico de drogas",

    # Daños
    "7.-DAÑOS;": "11. Resto de criminalidad convencional",

    # Resto / totales
    "Resto de infracciones penales": "11. Resto de criminalidad convencional",
    "TOTAL INFRACCIONES PENALES": "III. TOTAL INFRACCIONES PENALES",
    "1.-DELITOS Y FALTAS (EU)": "I. CRIMINALIDAD CONVENCIONAL",
}

def normalizar_tipologia(valor: str) -> str:
    """
    Normaliza una tipología antigua al estándar actual.
    Si no hay correspondencia, devuelve el valor original.
    """
    if pd.isna(valor):
        return valor
    valor = valor.strip()
    return TIPOLOGIA_NORMALIZAR.get(valor, valor)


df["tipo_normalizado"] = df["tipo"].apply(normalizar_tipologia)

# drop columna tipo original
df = df.drop(columns=["tipo"])

# df.to_csv("./data/esp_desagg_ytd_normalizado.csv", index=False, encoding="utf-8")

