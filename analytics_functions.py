import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def analyze_channel_performance(df_cliente, df_competencia):
    """
    Analiza el rendimiento del canal del cliente comparado con la competencia
    """
    # Métricas básicas del cliente
    metricas_cliente = {
        \"total_videos\": len(df_cliente),
        \"total_vistas\": df_cliente[\"vistas\"].sum(),
        \"avg_vph\": df_cliente[\"vph\"].mean(),
        \"avg_duration\": df_cliente[\"duracion_segundos\"].mean(),
        \"avg_likes\": df_cliente[\"likes\"].mean(),
        \"avg_comments\": df_cliente[\"comentarios\"].mean(),
        \"avg_connection_index\": df_cliente[\"indice_conexion\"].mean()
    }
    
    # Métricas de la competencia
    metricas_competencia = {
        \"total_videos\": len(df_competencia),
        \"total_vistas\": df_competencia[\"vistas\"].sum(),
        \"avg_vph\": df_competencia[\"vph\"].mean(),
        \"avg_duration\": df_competencia[\"duracion_segundos\"].mean(),
        \"avg_likes\": df_competencia[\"likes\"].mean(),
        \"avg_comments\": df_competencia[\"comentarios\"].mean(),
        \"avg_connection_index\": df_competencia[\"indice_conexion\"].mean()
    }
    
    return metricas_cliente, metricas_competencia

def create_performance_comparison_chart(metricas_cliente, metricas_competencia):
    """
    Crea un gráfico de comparación de rendimiento
    """
    metrics = [\"VPH Promedio\", \"Índice de Conexión\", \"Duración Promedio (min)\"]
    cliente_values = [
        metricas_cliente[\"avg_vph\"],
        metricas_cliente[\"avg_connection_index\"],
        metricas_cliente[\"avg_duration\"] / 60
    ]
    competencia_values = [
        metricas_competencia[\"avg_vph\"],
        metricas_competencia[\"avg_connection_index\"],
        metricas_competencia[\"avg_duration\"] / 60
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=\'Tu Canal\',
        x=metrics,
        y=cliente_values,
        marker_color=\'#FF0000\'
    ))
    
    fig.add_trace(go.Bar(
        name=\'Competencia (Promedio)\',
        x=metrics,
        y=competencia_values,
        marker_color=\'#666666\'
    ))
    
    fig.update_layout(
        title=\'📊 Comparación de Rendimiento: Tu Canal vs Competencia\',
        xaxis_title=\'Métricas\',
        yaxis_title=\'Valores\',
        barmode=\'group\',
        height=500
    )
    
    return fig

def analyze_content_strategy(df_cliente):
    """
    Analiza la estrategia de contenido del canal (Shorts vs Largos)
    """
    # Separar por formato
    shorts = df_cliente[df_cliente[\"formato\"] == \'Short\']
    largos = df_cliente[df_cliente[\"formato\"] == \'Largo\']
    
    strategy_analysis = {
        \"shorts\": {
            \"count\": len(shorts),
            \"avg_vph\": shorts[\"vph\"].mean() if len(shorts) > 0 else 0,
            \"avg_views\": shorts[\"vistas\"].mean() if len(shorts) > 0 else 0,
            \"total_views\": shorts[\"vistas\"].sum() if len(shorts) > 0 else 0
        },
        \"largos\": {
            \"count\": len(largos),
            \"avg_vph\": largos[\"vph\"].mean() if len(largos) > 0 else 0,
            \"avg_views\": largos[\"vistas\"].mean() if len(largos) > 0 else 0,
            \"total_views\": largos[\"vistas\"].sum() if len(largos) > 0 else 0
        }
    }
    
    return strategy_analysis

def create_format_distribution_chart(strategy_analysis):
    """
    Crea un gráfico de distribución de formatos
    """
    labels = [\'Shorts\', \'Videos Largos\']
    values = [strategy_analysis[\"shorts\"][\"count\"], strategy_analysis[\"largos\"][\"count\"]]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker_colors=[\'#FF6B6B\', \'#4ECDC4\']
    )])
    
    fig.update_layout(
        title=\'📱 Distribución de Formatos de Contenido\',
        height=400
    )
    
    return fig

def analyze_temporal_trends(df_cliente):
    """
    Analiza tendencias temporales del canal
    """
    # Convertir fecha a datetime si no lo está
    df_cliente[\"fecha_publicacion\"] = pd.to_datetime(df_cliente[\"fecha_publicacion\"])
    
    # Agrupar por mes
    df_cliente[\"mes\"] = df_cliente[\"fecha_publicacion\"].dt.to_period(\'M\')
    monthly_stats = df_cliente.groupby(\'mes\').agg({
        \"vistas\": \'sum\',
        \"vph\": \'mean\',
        \"video_id\": \'count\'
    }).rename(columns={\"video_id\": \"videos_publicados\"})
    
    return monthly_stats

def create_temporal_trends_chart(monthly_stats):
    """
    Crea un gráfico de tendencias temporales
    """
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(\'📈 Vistas Totales por Mes\', \'🚀 VPH Promedio por Mes\'),
        vertical_spacing=0.1
    )
    
    # Gráfico de vistas
    fig.add_trace(
        go.Scatter(
            x=monthly_stats.index.astype(str),
            y=monthly_stats[\"vistas\"],
            mode=\'lines+markers\',
            name=\'Vistas Totales\',
            line=dict(color=\'#FF0000\', width=3)
        ),
        row=1, col=1
    )
    
    # Gráfico de VPH
    fig.add_trace(
        go.Scatter(
            x=monthly_stats.index.astype(str),
            y=monthly_stats[\"vph\"],
            mode=\'lines+markers\',
            name=\'VPH Promedio\',
            line=dict(color=\'#4ECDC4\', width=3)
        ),
        row=2, col=1
    )
    
    fig.update_layout(height=600, showlegend=False)
    fig.update_xaxes(title_text=\"Mes\", row=2, col=1)
    fig.update_yaxes(title_text=\"Vistas\", row=1, col=1)
    fig.update_yaxes(title_text=\"VPH\", row=2, col=1)
    
    return fig

def analyze_bucket_performance(df_cliente):
    """
    Analiza el rendimiento por bucket temático
    """
    bucket_stats = df_cliente.groupby(\'bucket_tematico\').agg({
        \"vph\": \'mean\',
        \"vistas\": \'mean\',
        \"indice_conexion\": \'mean\',
        \"video_id\": \'count\'
    }).rename(columns={\"video_id\": \"num_videos\"})
    
    bucket_stats = bucket_stats.sort_values(\'vph\', ascending=False)
    
    return bucket_stats

def create_bucket_performance_chart(bucket_stats):
    """
    Crea un gráfico de rendimiento por bucket temático
    """
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=bucket_stats.index,
        y=bucket_stats[\"vph\"],
        marker_color=\'#FF6B6B\',
        text=bucket_stats[\"num_videos\"],
        texttemplate=\'%{text} videos\',
        textposition=\'outside\'
    ))
    
    fig.update_layout(
        title=\'🎯 Rendimiento por Tema de Contenido (VPH)\',
        xaxis_title=\'Bucket Temático\',
        yaxis_title=\'VPH Promedio\',
        height=500
    )
    
    return fig

def get_top_performing_videos(df_cliente, n=10):
    """
    Obtiene los videos con mejor rendimiento del canal
    """
    top_videos = df_cliente.nlargest(n, \'vph\')[
        [\"titulo\", \"vph\", \"vistas\", \"duracion_segundos\", \"fecha_publicacion\", \"url_miniatura\"]
    ].copy()
    
    # Formatear duración
    top_videos[\"duracion_formateada\"] = top_videos[\"duracion_segundos\"].apply(
        lambda x: f\"{int(x//60)}:{int(x%60):02d}\" if x >= 60 else f\"{int(x)}s\"
    )
    
    return top_videos

def calculate_optimal_duration(df_cliente):
    """
    Calcula la duración óptima basada en VPH
    """
    # Agrupar por rangos de duración
    df_cliente[\"duracion_rango\"] = pd.cut(
        df_cliente[\"duracion_segundos\"],
        bins=[0, 60, 180, 300, 600, 1200, float(\'inf\')],
        labels=[\'<1min\', \'1-3min\', \'3-5min\', \'5-10min\', \'10-20min\', \'>20min\']
    )
    
    duration_stats = df_cliente.groupby(\'duracion_rango\').agg({
        \"vph\": \'mean\',
        \"vistas\": \'mean\',
        \"video_id\": \'count\'
    }).rename(columns={\"video_id\": \"num_videos\"})
    
    # Encontrar la duración óptima
    optimal_range = duration_stats[\"vph\"].idxmax()
    
    return duration_stats, optimal_range
