import pandas as pd
import re
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64

def extract_keywords_from_titles(df, min_length=3):
    """
    Extrae palabras clave de los títulos de videos
    """
    all_titles = \' \'.join(df[\\'titulo\\'].astype(str))
    
    # Limpiar texto
    all_titles = re.sub(r\\'[^\\w\\s]\\', \' \', all_titles.lower())
    words = all_titles.split()
    
    # Filtrar palabras cortas y comunes
    stop_words = {\'de\', \'la\', \'el\', \'en\', \'y\', \'a\', \'que\', \'es\', \'se\', \'no\', \'te\', \'lo\', \'le\', \'da\', \'su\', \'por\', \'son\', \'con\', \'una\', \'su\', \'para\', \'es\', \'al\', \'lo\', \'como\', \'mas\', \'pero\', \'sus\', \'le\', \'ya\', \'o\', \'este\', \'si\', \'porque\', \'esta\', \'entre\', \'cuando\', \'muy\', \'sin\', \'sobre\', \'tambien\', \'me\', \'hasta\', \'hay\', \'donde\', \'quien\', \'desde\', \'todo\', \'nos\', \'durante\', \'todos\', \'uno\', \'les\', \'ni\', \'contra\', \'otros\', \'ese\', \'eso\', \'ante\', \'ellos\', \'e\', \'esto\', \'mi\', \'antes\', \'algunos\', \'que\', \'unos\', \'yo\', \'del\', \'las\', \'un\', \'por\', \'que\', \'para\', \'son\', \'se\', \'lo\', \'todo\', \'any\', \'can\', \'had\', \'her\', \'was\', \'one\', \'our\', \'out\', \'day\', \'get\', \'has\', \'him\', \'his\', \'how\', \'man\', \'new\', \'now\', \'old\', \'see\', \'two\', \'way\', \'who\', \'boy\', \'did\', \'its\', \'let\', \'put\', \'say\', \'she\', \'too\', \'use\', \'a\', \'an\', \'the\', \'and\', \'or\', \'in\', \'on\', \'at\', \'for\', \'with\', \'as\', \'by\', \'from\', \'about\', \'into\', \'through\', \'after\', \'before\', \'during\', \'over\', \'under\', \'above\', \'below\', \'to\', \'from\', \'up\', \'down\', \'out\', \'off\', \'over\', \'under\', \'again\', \'further\', \'then\', \''once\', \'here\', \'there\', \'when\', \'where\', \'why\', \'how\', \'all\', \'any\', \'both\', \'each\', \'few\', \'more\', \'most\', \'other\', \'some\', \'such\', \'no\', \'nor\', \'not\', \'only\', \'own\', \'same\', \'so\', \'than\', \'too\', \'very\', \'s\', \'t\', \'can\', \'will\', \'just\', \'don\', \'should\', \'now\']}
    
    filtered_words = [word for word in words if len(word) >= min_length and word not in stop_words]
    
    return Counter(filtered_words)

def analyze_title_patterns(df):
    """
    Analiza patrones en los títulos más exitosos
    """
    # Ordenar por VPH
    df_sorted = df.sort_values(\'vph\', ascending=False)
    top_videos = df_sorted.head(20)
    
    # Extraer patrones
    patterns = {
        \'preguntas\': len([t for t in top_videos[\\'titulo\\'] if \'?\' in str(t)]),
        \'numeros\': len([t for t in top_videos[\\'titulo\\'] if re.search(r\\'\\d+\\', str(t))]),
        \'palabras_poder\': 0,
        \'longitud_promedio\': top_videos[\\'titulo\\'].str.len().mean()
    }
    
    # Palabras de poder comunes
    power_words = [\'secreto\', \'mejor\', \'increible\', \'facil\', \'rapido\', \'gratis\', \'nuevo\', \'ultimate\', \'perfect\', \'amazing\', \'best\', \'free\', \'easy\', \'quick\', \'secret\', \'ultimate\']
    
    for titulo in top_videos[\\'titulo\\']:
        titulo_lower = str(titulo).lower()
        for word in power_words:
            if word in titulo_lower:
                patterns[\'palabras_poder\'] += 1
                break
    
    return patterns, top_videos

def create_wordcloud_from_titles(df, max_words=50):
    """
    Crea una nube de palabras de los títulos más exitosos
    """
    # Obtener top videos por VPH
    top_videos = df.nlargest(50, \'vph\')
    keywords = extract_keywords_from_titles(top_videos)
    
    if len(keywords) == 0:
        return None
    
    # Crear wordcloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color=\'white\',
        max_words=max_words,
        colormap=\'viridis\'
    ).generate_from_frequencies(keywords)
    
    # Convertir a imagen base64 para Streamlit
    img = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation=\'bilinear\')
    plt.axis(\'off\')
    plt.tight_layout(pad=0)
    plt.savefig(img, format=\'png\', bbox_inches=\'tight\', dpi=150)
    plt.close()
    
    img.seek(0)
    return img

def analyze_publishing_schedule(df):
    """
    Analiza los mejores días y horas para publicar
    """
    df[\\'fecha_publicacion\\'] = pd.to_datetime(df[\\'fecha_publicacion\\'])
    df[\\'dia_semana\\'] = df[\\'fecha_publicacion\\'].dt.day_name()
    df[\\'hora\\'] = df[\\'fecha_publicacion\\'].dt.hour
    
    # Análisis por día de la semana
    day_performance = df.groupby(\'dia_semana\').agg({
        \\'vph\\': \'mean\',
        \\'vistas\\': \'mean\',
        \\'video_id\\': \'count\'
    }).rename(columns={\'video_id\': \'num_videos\'})[['vph', 'vistas', 'num_videos']]
    
    # Reordenar días de la semana
    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_performance = day_performance.reindex(ordered_days)

    # Análisis por hora
    hour_performance = df.groupby(\'hora\').agg({
        \\'vph\\': \'mean\',
        \\'vistas\\': \'mean\',
        \\'video_id\\': \'count\'
    }).rename(columns={\'video_id\': \'num_videos\'})[['vph', 'vistas', 'num_videos']]
    
    return day_performance, hour_performance

def create_publishing_heatmap(day_performance, hour_performance):
    """
    Crea un heatmap de los mejores momentos para publicar
    """
    # Gráfico de días de la semana
    fig_days = go.Figure()
    fig_days.add_trace(go.Bar(
        x=day_performance.index,
        y=day_performance[\\'vph\\'],
        marker_color=\'#FF6B6B\',
        text=day_performance[\\'num_videos\\'],
        texttemplate=\'%{text} videos\',
        textposition=\'outside\'
    ))
    
    fig_days.update_layout(
        title=\'📅 Mejor Día de la Semana para Publicar (por VPH)\\',
        xaxis_title=\'Día de la Semana\',
        yaxis_title=\'VPH Promedio\',
        height=400
    )
    
    # Gráfico de horas
    fig_hours = go.Figure()
    fig_hours.add_trace(go.Scatter(
        x=hour_performance.index,
        y=hour_performance[\\'vph\\'],
        mode=\'lines+markers\',
        line=dict(color=\'#4ECDC4\', width=3),
        marker=dict(size=8)
    ))
    
    fig_hours.update_layout(
        title=\'🕐 Mejor Hora del Día para Publicar (por VPH)\\',
        xaxis_title=\'Hora del Día\',
        yaxis_title=\'VPH Promedio\',
        height=400
    )
    
    return fig_days, fig_hours

def generate_seo_recommendations(df):
    """
    Genera recomendaciones SEO basadas en los videos más exitosos
    """
    top_videos = df.nlargest(20, \'vph\')
    keywords = extract_keywords_from_titles(top_videos)
    
    # Top keywords
    top_keywords = dict(keywords.most_common(10))
    
    # Análisis de longitud de título
    title_lengths = top_videos[\\'titulo\\'].str.len()
    optimal_length = title_lengths.mean()
    
    # Patrones de éxito
    patterns, _ = analyze_title_patterns(top_videos)
    
    recommendations = {
        \'top_keywords\': top_keywords,
        \'optimal_title_length\': optimal_length,
        \'patterns\': patterns,
        \'title_template\': generate_title_template(top_keywords, patterns)
    }
    
    return recommendations

def generate_title_template(top_keywords, patterns):
    """
    Genera una plantilla de título basada en patrones exitosos
    """
    templates = []
    
    # Plantillas basadas en patrones
    if patterns[\'preguntas\'] > 5:
        templates.append(\"¿Cómo [ACCIÓN] [TEMA] en [TIEMPO]?\")
        templates.append(\"¿Por qué [TEMA] es [ADJETIVO]?\")
    
    if patterns[\'numeros\'] > 5:
        templates.append(\"[NÚMERO] [TEMA] que [BENEFICIO]\")
        templates.append(\"[NÚMERO] Secretos de [TEMA]\")
    
    # Plantillas con keywords populares
    top_words = list(top_keywords.keys())[:5]
    if top_words:
        templates.append(f\"Cómo {top_words[0]} [TEMA] como un Profesional\")
        templates.append(f\"La Guía Definitiva de {top_words[0]}\")
    
    return templates[:3]  # Devolver máximo 3 plantillas
