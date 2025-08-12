import pandas as pd
from datetime import datetime
import numpy as np

def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)

    # Convertir fecha_publicacion a datetime y manejar posibles errores
    df["fecha_publicacion"] = pd.to_datetime(df["fecha_publicacion"], errors=\'coerce\')
    df.dropna(subset=["fecha_publicacion"], inplace=True)

    # Calcular \'horas_desde_pub\' si no está presente o si se necesita recalcular
    # Asumiendo que la fecha actual es la de la ejecución del script
    if \'horas_desde_pub\' not in df.columns:
        df["horas_desde_pub"] = (datetime.now() - df["fecha_publicacion"]).dt.total_seconds() / 3600

    # Asegurar que las columnas numéricas sean de tipo numérico
    numeric_cols = [\'vistas\', \'likes\', \'comentarios\', \'duracion_segundos\', \'horas_desde_pub\']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors=\'coerce\').fillna(0)

    # Calcular VPH si no está presente o si se necesita recalcular
    if \'vph\' not in df.columns:
        df["vph"] = df["vistas"] / (df["horas_desde_pub"] + 0.001) # Evitar división por cero

    # Clasificar Formato (Shorts vs. Largos) - CORREGIDO A 180 SEGUNDOS
    df["formato"] = df["duracion_segundos"].apply(lambda x: \'Short\' if x < 180 else \'Largo\')

    # Calcular Índice de Conexión
    df["indice_conexion"] = ((df["likes"] + df["comentarios"] * 2) / (df["vistas"] + 0.001)) * 100

    # Calcular Índice CLARA™ (ejemplo de fórmula ponderada)
    # Necesitamos \'vistas_normalizadas\' para CLARA, que no está en el CSV de ejemplo.
    # Por ahora, usaremos una simplificación o asumiremos que se calculará más adelante.
    # Para este ejemplo, vamos a normalizar las vistas de forma simple para la demostración.
    min_vistas = df[\'vistas\'].min()
    max_vistas = df[\'vistas\'].max()
    df["vistas_normalizadas"] = (df["vistas"] - min_vistas) / (max_vistas - min_vistas + 0.001)
    df["clara_index"] = (df["vph"] * 0.5) + (df["indice_conexion"] * 0.3) + (df["vistas_normalizadas"] * 0.2)

    # Identificar Buckets Temáticos (Esto requeriría un modelo de NLP o reglas, por ahora es un placeholder)
    # Para la demostración, asignaremos un bucket genérico o basado en palabras clave simples
    def assign_bucket(title):
        title_lower = str(title).lower()
        if \'productividad\' in title_lower: return \'Productividad\'
        if \'finanzas\' in title_lower: return \'Finanzas\'
        if \'negocios\' in title_lower: return \'Negocios\'
        if \'tutorial\' in title_lower: return \'Tutorial\'
        return \'General\'

    df["bucket_tematico"] = df["titulo"].apply(assign_bucket)

    return df

def get_top_videos(df, num_videos=20, sort_by=\'vph\', ascending=False):
    return df.sort_values(by=sort_by, ascending=ascending).head(num_videos)

def filter_by_channel(df, channel_name):
    return df[df["nombre_canal"] == channel_name]

def get_channel_metrics(df_channel):
    # Aquí se calcularían métricas agregadas para un canal específico
    total_videos = len(df_channel)
    total_vistas = df_channel[\'vistas\'].sum()
    avg_vph = df_channel[\'vph\'].mean()
    avg_duration = df_channel[\'duracion_segundos\'].mean()
    return {
        \'total_videos\': total_videos,
        \'total_vistas\': total_vistas,
        \'avg_vph\': avg_vph,
        \'avg_duration\': avg_duration
    }
