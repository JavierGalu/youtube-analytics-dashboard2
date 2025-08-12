import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_processing import load_and_preprocess_data, get_top_videos, filter_by_channel
from analytics_functions import (
    analyze_channel_performance,
    create_performance_comparison_chart,
    analyze_content_strategy,
    create_format_distribution_chart,
    analyze_temporal_trends,
    create_temporal_trends_chart,
    analyze_bucket_performance,
    create_bucket_performance_chart,
    get_top_performing_videos,
    calculate_optimal_duration
)
from title_analysis import (
    analyze_title_patterns,
    create_wordcloud_from_titles,
    analyze_publishing_schedule,
    create_publishing_heatmap,
    generate_seo_recommendations
)

# --- Configuración de la página --- #
st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Estilos CSS personalizados --- #
st.markdown("""
<style>
    .main-header {
        font-size: 3.5em !important;
        color: #FF0000;
        text-align: center;
        margin-bottom: 0.5em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .section-header {
        font-size: 2.5em !important;
        color: #FF4B4B;
        margin-top: 1.5em;
        margin-bottom: 0.8em;
        border-bottom: 2px solid #FF4B4B;
        padding-bottom: 0.3em;
    }
    .stMetric {
        background-color: #26282F;
        padding: 20px;
        border-radius: 10px;
        color: #FF4B4B;
        border: 1px solid #FF0000;
    }
    .stMetric > div > div:first-child {
        color: #FFFFFF;
    }
    .stMetric > div > div:nth-child(2) > div {
        font-size: 2.5em;
        color: #FF0000;
    }
    .stMetric > div > div:nth-child(3) > div {
        color: #FFFFFF;
    }
    .explanation-box {
        background-color: #333333;
        border-left: 5px solid #FF0000;
        padding: 15px;
        margin-top: 20px;
        border-radius: 5px;
    }
    .explanation-box h4 {
        color: #FF0000;
        font-size: 1.3em;
    }
    .explanation-box p {
        color: #FFFFFF;
        font-size: 1em;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size:1.5rem;
    }
    .stDataFrame {
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# --- Título Principal --- #
st.markdown("<h1 class=\"main-header\">📊 YouTube Analytics Dashboard</h1>", unsafe_allow_html=True)

# --- Sidebar para carga de datos y selección de canal --- #
st.sidebar.header("🧭 Navegación")

uploaded_file = st.sidebar.file_uploader("📁 Sube tu archivo CSV de YouTube", type=["csv"])

df = None
if uploaded_file is not None:
    df = load_and_preprocess_data(uploaded_file)
    st.sidebar.success(f"✅ Datos cargados: {len(df)} videos analizados.")

    all_channels = ["Todos los Canales"] + sorted(df["nombre_canal"].unique().tolist())
    selected_channel = st.sidebar.selectbox(
        "👤 Selecciona el canal del cliente",
        all_channels
    )

    if selected_channel != "Todos los Canales":
        df_cliente = filter_by_channel(df, selected_channel)
        df_competencia = df[df["nombre_canal"] != selected_channel]
        canal_cliente = selected_channel
    else:
        df_cliente = df
        df_competencia = df # En este caso, la competencia es el mismo dataset
        canal_cliente = "Todos los Canales"

    # Calcular métricas promedio de la competencia (si aplica)
    if not df_competencia.empty:
        avg_vph_competencia = df_competencia["vph"].mean()
        avg_connection_index_competencia = df_competencia["indice_conexion"].mean()
        avg_duration_competencia = df_competencia["duracion_segundos"].mean()
    else:
        avg_vph_competencia = 0
        avg_connection_index_competencia = 0
        avg_duration_competencia = 0

    # Crear un diccionario de métricas de competencia para pasar a las funciones
    metricas_competencia_dict = {
        "avg_vph": avg_vph_competencia,
        "avg_connection_index": avg_connection_index_competencia,
        "avg_duration": avg_duration_competencia
    }

else:
    st.info("Sube un archivo CSV para comenzar el análisis.")
    st.markdown("""
    ## 👋 ¡Bienvenido al Dashboard de Análisis de YouTube!

    Esta aplicación te ayudará a analizar el rendimiento de tu canal de YouTube comparándolo con la competencia.

    ### 🚀 ¿Cómo empezar?

    1.  **Sube tu archivo CSV** usando el botón en la barra lateral
    2.  **Selecciona tu canal** de la lista de canales disponibles
    3.  **Explora las diferentes secciones** del análisis

    ### 📊 ¿Qué obtendrás?

    *   **Análisis completo** de tu posicionamiento en el mercado
    *   **Comparativa detallada** con canales de referencia
    *   **Recomendaciones estratégicas** para mejorar tu contenido
    *   **Insights visuales** fáciles de entender

    ### 🎯 Diseñado para todos

    Este dashboard está diseñado para ser **fácil de entender**, incluso para un niño de 12 años, con explicaciones claras y visualizaciones intuitivas.
    """)

# --- Funciones para mostrar cada sección --- #

def mostrar_resumen_ejecutivo(df_cliente, metricas_competencia_dict, canal_cliente):
    st.markdown("<h2 class=\"section-header\">🏠 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    if len(df_cliente) == 0:
        st.warning("No hay datos disponibles para este canal.")
        return

    metricas_cliente, _ = analyze_channel_performance(df_cliente, df_competencia)

    st.markdown(f"### 📈 Rendimiento General de {canal_cliente}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="VPH Promedio",
            value=f"{metricas_cliente[\"avg_vph\"]:.1f}",
            delta=f"{(metricas_cliente[\"avg_vph\"] - metricas_competencia_dict[\"avg_vph\"]):.1f} vs Competencia",
            delta_color="inverse"
        )
    with col2:
        st.metric(
            label="Índice de Conexión Promedio",
            value=f"{metricas_cliente[\"avg_connection_index\"]:.1f}%",
            delta=f"{(metricas_cliente[\"avg_connection_index\"] - metricas_competencia_dict[\"avg_connection_index\"]):.1f}% vs Competencia",
            delta_color="inverse"
        )
    with col3:
        st.metric(
            label="Duración Promedio",
            value=f"{metricas_cliente[\"avg_duration\"] / 60:.1f} min",
            delta=f"{(metricas_cliente[\"avg_duration\"] / 60 - metricas_competencia_dict[\"avg_duration\"] / 60):.1f} min vs Competencia",
            delta_color="inverse"
        )

    st.markdown("""
    <div class="explanation-box">
    <h4>🤔 ¿Qué significan estos números?</h4>
    <p><strong>VPH (Vistas Por Hora):</strong> Mide qué tan rápido tus videos consiguen vistas. Un número más alto es mejor.</p>
    <p><strong>Índice de Conexión:</strong> Mide cuánto le gusta tu contenido a la gente (likes y comentarios). Un porcentaje más alto es mejor.</p>
    <p><strong>Duración Promedio:</strong> Es el tiempo promedio de tus videos. Compara si tus videos son más largos o cortos que los de la competencia.</p>
    <p><strong>Delta vs Competencia:</strong> Te dice si estás por encima (verde) o por debajo (rojo) del promedio de los otros canales.</p>
    </div>
    """, unsafe_allow_html=True)

    fig_comparison = create_performance_comparison_chart(metricas_cliente, metricas_competencia_dict)
    st.plotly_chart(fig_comparison, use_container_width=True)

def mostrar_posicionamiento_general(df_cliente, df_competencia, canal_cliente):
    st.markdown("<h2 class=\"section-header\">📊 Posicionamiento General</h2>", unsafe_allow_html=True)

    if len(df_cliente) == 0:
        st.warning("No hay datos disponibles para este canal.")
        return

    st.markdown("""
    ### 🌍 Tu Lugar en el Mapa de YouTube

    Aquí puedes ver cómo se compara tu canal con los demás en tu nicho. 
    Cada punto es un video. Los tuyos son rojos, los de la competencia son grises.
    """)

    # Gráfico de dispersión VPH vs Vistas
    fig_vph_views = px.scatter(
        df,
        x="vistas",
        y="vph",
        color="nombre_canal",
        hover_name="titulo",
        log_x=True,
        size="duracion_segundos",
        color_discrete_map={canal_cliente: "#FF0000"},
        title="📈 VPH vs Vistas: ¿Quién crece más rápido y llega más lejos?"
    )
    fig_vph_views.update_layout(height=600)
    st.plotly_chart(fig_vph_views, use_container_width=True)

    st.markdown("""
    <div class="explanation-box">
    <h4>🤔 ¿Qué buscar en este gráfico?</h4>
    <p><strong>Tus videos (rojos):</strong> ¿Están en la parte superior (alto VPH) o a la derecha (muchas vistas)?</p>
    <p><strong>Videos de la competencia (grises):</strong> ¿Hay videos de la competencia que tienen mucho VPH y vistas? ¡Aprende de ellos!</p>
    <p><strong>Tamaño del círculo:</strong> Indica la duración del video. Los círculos grandes son videos largos, los pequeños son cortos.</p>
    </div>
    """, unsafe_allow_html=True)

    # Gráfico de dispersión Índice de Conexión vs Vistas
    fig_connection_views = px.scatter(
        df,
        x="vistas",
        y="indice_conexion",
        color="nombre_canal",
        hover_name="titulo",
        log_x=True,
        size="duracion_segundos",
        color_discrete_map={canal_cliente: "#FF0000"},
        title="❤️ Índice de Conexión vs Vistas: ¿Quién conecta más con su audiencia?"
    )
    fig_connection_views.update_layout(height=600)
    st.plotly_chart(fig_connection_views, use_container_width=True)

    st.markdown("""
    <div class="explanation-box">
    <h4>🤔 ¿Qué buscar en este gráfico?</h4>
    <p><strong>Tus videos (rojos):</strong> ¿Están arriba (alto Índice de Conexión)? Significa que a tu audiencia le encanta lo que haces.</p>
    <p><strong>Videos de la competencia (grises):</strong> ¿Hay videos de la competencia que tienen un Índice de Conexión muy alto? Mira qué hacen para conectar tanto.</p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_estrategia_contenido(df_cliente, canal_cliente):
    st.markdown("<h2 class=\"section-header\">🚀 Estrategia de Contenido</h2>", unsafe_allow_html=True)

    if len(df_cliente) == 0:
        st.warning("No hay datos disponibles para este canal.")
        return

    st.markdown("""
    ### 🎬 ¿Qué Tipo de Videos Funcionan Mejor para Ti?

    Aquí analizamos si tus videos cortos (Shorts) o largos tienen mejor rendimiento, 
    y qué temas son los más populares en tu canal.
    """)

    strategy_analysis = analyze_content_strategy(df_cliente)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Shorts", strategy_analysis["shorts"]["count"])
        st.metric("VPH Promedio Shorts", f"{strategy_analysis[\"shorts\"][\"avg_vph\"]:.1f}")
        st.metric("Vistas Promedio Shorts", f"{strategy_analysis[\"shorts\"][\"avg_views\"]:.0f}")
    with col2:
        st.metric("Total Videos Largos", strategy_analysis["largos"]["count"])
        st.metric("VPH Promedio Largos", f"{strategy_analysis[\"largos\"][\"avg_vph\"]:.1f}")
        st.metric("Vistas Promedio Largos", f"{strategy_analysis[\"largos\"][\"avg_views\"]:.0f}")

    fig_format_dist = create_format_distribution_chart(strategy_analysis)
    st.plotly_chart(fig_format_dist, use_container_width=True)

    st.markdown("""
    <div class="explanation-box">
    <h4>🤔 ¿Shorts o Videos Largos?</h4>
    <p>Mira qué formato tiene un VPH más alto. Ese es el que más rápido consigue vistas para ti.</p>
    <p>Si tienes muchos videos de un tipo pero el VPH es bajo, ¡quizás debas probar otra cosa!</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 Temas que Conectan con Tu Audiencia")
    bucket_stats = analyze_bucket_performance(df_cliente)
    if not bucket_stats.empty:
        fig_bucket_perf = create_bucket_performance_chart(bucket_stats)
        st.plotly_chart(fig_bucket_perf, use_container_width=True)

        st.markdown("""
        <div class="explanation-box">
        <h4>🤔 ¿Qué temas funcionan mejor?</h4>
        <p>Los temas con un VPH más alto son los que más le gustan a tu audiencia. ¡Haz más videos sobre eso!</p>
        <p>Si un tema tiene muchas vistas pero poco VPH, significa que es popular pero tarda en arrancar.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No hay suficientes datos para analizar los buckets temáticos. Asegúrate de que los títulos de tus videos contengan palabras clave relevantes.")

    st.markdown("### ⏱️ Duración Óptima de Tus Videos")
    duration_stats, optimal_range = calculate_optimal_duration(df_cliente)
    if not duration_stats.empty:
        st.dataframe(duration_stats.sort_values("vph", ascending=False), use_container_width=True)
        st.markdown(f"""
        <div class="explanation-box">
        <h4>💡 Tu duración ideal: **{optimal_range}**</h4>
        <p>Tus videos que duran **{optimal_range}** son los que mejor VPH tienen. ¡Intenta hacer más videos con esa duración!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No hay suficientes datos para calcular la duración óptima.")

def mostrar_videos_estrella(df_cliente, canal_cliente):
    st.markdown("<h2 class=\"section-header\">🏆 Videos Estrella</h2>", unsafe_allow_html=True)

    if len(df_cliente) == 0:
        st.warning("No hay datos disponibles para este canal.")
        return

    st.markdown("""
    ### ✨ Tus Videos Más Brillantes

    Estos son los videos de tu canal que han tenido el mejor rendimiento (VPH más alto).
    ¡Aprende de ellos para crear tu próximo éxito!
    """)

    top_videos = get_top_performing_videos(df_cliente, n=20)

    if not top_videos.empty:
        # Mostrar videos en una grilla
        cols_per_row = 4
        videos_list = list(top_videos.iterrows())

        for i in range(0, len(videos_list), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(videos_list):
                    idx, video = videos_list[i + j]
                    with cols[j]:
                        try:
                            st.image(
                                video["url_miniatura"],
                                width=150,
                                caption=f"VPH: {video[\"vph\"]:.1f}"
                            )
                            st.markdown(f"""
                            **{video[\"titulo\"]}**
                              
👀 {video[\"vistas\"]:,} vistas
                              
⏱️ {video[\"duracion_formateada\"]}
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error cargando miniatura para {video[\"titulo\"]}")
                            st.markdown(f"**{video[\"titulo\"]}**  
VPH: {video[\"vph\"]:.1f}")
    else:
        st.info("No hay videos para mostrar en esta sección.")

    st.markdown("""
    <div class="explanation-box">
    <h4>🤔 ¿Cómo usar esta información?</h4>
    <p><strong>Analiza los títulos:</strong> ¿Qué palabras usaste? ¿Hay preguntas o números?</p>
    <p><strong>Observa las miniaturas:</strong> ¿Qué las hace atractivas? ¿Qué colores o elementos usaste?</p>
    <p><strong>Revisa la duración:</strong> ¿Son cortos o largos? ¿Coincide con tu duración óptima?</p>
    <p><strong>Replica el éxito:</strong> Usa estos videos como inspiración para tu próximo contenido.</p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_optimizacion_titulos(df_cliente, df_competencia, canal_cliente):
    st.markdown("<h2 class=\"section-header\">✍️ Optimización de Títulos</h2>", unsafe_allow_html=True)
    
    if len(df_cliente) == 0:
        st.warning("No hay datos disponibles para este canal.")
        return
    
    # Análisis de patrones de títulos
    patterns, top_videos = analyze_title_patterns(df_cliente)
    
    # Mostrar estadísticas de patrones
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("❓ Títulos con Preguntas", f"{patterns[\"preguntas\"]}/20")
    
    with col2:
        st.metric("🔢 Títulos con Números", f"{patterns[\"numeros\"]}/20")
    
    with col3:
        st.metric("💪 Palabras de Poder", patterns[\"palabras_poder\"])
    
    with col4:
        st.metric("📏 Longitud Promedio", f"{patterns[\"longitud_promedio\"]:.0f} chars")
    
    # Nube de palabras
    st.markdown("### ☁️ Palabras Clave Más Exitosas")
    
    try:
        wordcloud_img = create_wordcloud_from_titles(df_cliente)
        if wordcloud_img:
            st.image(wordcloud_img, caption="Nube de palabras de tus videos más exitosos")
        else:
            st.info("No hay suficientes datos para generar la nube de palabras.")
    except Exception as e:
        st.error(f"Error generando nube de palabras: {str(e)}")
        st.info("Mostrando análisis alternativo...")
    
    # Recomendaciones SEO
    st.markdown("### 🎯 Recomendaciones SEO")
    seo_recs = generate_seo_recommendations(df_cliente)
    
    # Mostrar top keywords
    if seo_recs[\"top_keywords\"]:
        st.markdown("#### 🔑 Palabras Clave Más Exitosas:")
        keywords_df = pd.DataFrame(list(seo_recs[\"top_keywords\"].items()), 
                                 columns=[\"Palabra Clave\", \"Frecuencia\"])
        st.dataframe(keywords_df, use_container_width=True)
    
    # Plantillas de títulos
    if seo_recs[\"title_template\"]:
        st.markdown("#### 📝 Fábrica de Títulos Virales:")
        st.markdown("**Plantillas basadas en tus videos más exitosos:**")
        for i, template in enumerate(seo_recs[\"title_template\"], 1):
            st.markdown(f"{i}. `{template}`")
    
    # Longitud óptima
    st.markdown(f"#### 📏 Longitud Óptima de Título: **{seo_recs[\"optimal_title_length\"]:.0f} caracteres**")
    
    # Explicación para niños
    st.markdown("""
    <div class="explanation-box">
    <h4>🤔 ¿Cómo usar estas recomendaciones?</h4>
    <p><strong>Palabras Clave:</strong> Usa las palabras que más aparecen en tus videos exitosos.</p>
    <p><strong>Plantillas:</strong> Reemplaza las partes entre [CORCHETES] con tu contenido específico.</p>
    <p><strong>Longitud:</strong> Mantén tus títulos cerca de la longitud óptima para mejor rendimiento.</p>
    <p><strong>Preguntas y Números:</strong> Si funcionan en tu nicho, úsalos más seguido.</p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_calendario_seo(df_cliente, canal_cliente):
    st.markdown("<h2 class=\"section-header\">🗓️ Calendario y SEO</h2>", unsafe_allow_html=True)
    
    if len(df_cliente) == 0:
        st.warning("No hay datos disponibles para este canal.")
        return
    
    # Análisis de horarios de publicación
    day_performance, hour_performance = analyze_publishing_schedule(df_cliente)
    
    if len(day_performance) > 0 and len(hour_performance) > 0:
        # Crear gráficos de horarios
        fig_days, fig_hours = create_publishing_heatmap(day_performance, hour_performance)
        
        # Mostrar gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(fig_days, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig_hours, use_container_width=True)
        
        # Recomendaciones de horarios
        best_day = day_performance[\"vph\"].idxmax()
        best_hour = hour_performance[\"vph\"].idxmax()
        
        st.markdown(f"""
        ### 🎯 Recomendaciones de Publicación
        
        **📅 Mejor día:** {best_day} (VPH promedio: {day_performance.loc[best_day, \"vph\"]:.1f})
        
        **🕐 Mejor hora:** {best_hour}:00 (VPH promedio: {hour_performance.loc[best_hour, \"vph\"]:.1f})
        """)
    
    # Kit de posicionamiento SEO
    st.markdown("### 🔧 Kit de Posicionamiento SEO")
    
    # Checklist SEO
    st.markdown("""
    #### ✅ Checklist SEO para YouTube
    
    **Antes de publicar, verifica:**
    
    - [ ] **Título optimizado** (usa palabras clave principales)
    - [ ] **Descripción completa** (mínimo 125 palabras)
    - [ ] **Tags relevantes** (5-10 tags específicos)
    - [ ] **Miniatura atractiva** (alta resolución, contraste)
    - [ ] **Subtítulos/CC** (mejora accesibilidad y SEO)
    - [ ] **Cards y pantallas finales** (aumenta retención)
    - [ ] **Hora de publicación óptima** (según tu análisis)
    """)
    
    # Plantilla de descripción
    st.markdown("""
    #### 📝 Plantilla de Descripción SEO
    
    ```
    🎯 En este video aprenderás [TEMA PRINCIPAL]
    
    ⏰ Timestamps:
    00:00 - Introducción
    [XX:XX] - [SECCIÓN 1]
    [XX:XX] - [SECCIÓN 2]
    [XX:XX] - Conclusión
    
    📚 Recursos mencionados:
    • [RECURSO 1]
    • [RECURSO 2]
    
    🔗 Mis redes sociales:
    • Instagram: [TU_INSTAGRAM]
    • Twitter: [TU_TWITTER]
    
    #[TAG1] #[TAG2] #[TAG3]
    
    [DESCRIPCIÓN DETALLADA DEL CONTENIDO - Mínimo 125 palabras]
    ```
    """)
    
    # Análisis de tags (si están disponibles)
    if \"tags\" in df_cliente.columns:
        st.markdown("#### 🏷️ Análisis de Tags")
        # Aquí iría el análisis de tags si estuvieran disponibles
        st.info("Los tags no están disponibles en este dataset, pero son importantes para SEO.")
    
    # Explicación para niños
    st.markdown("""
    <div class="explanation-box">
    <h4>🤔 ¿Por qué importa el SEO?</h4>
    <p><strong>SEO = Search Engine Optimization:</strong> Ayuda a que YouTube entienda de qué trata tu video.</p>
    <p><strong>Mejor horario:</strong> Publica cuando tu audiencia está más activa para conseguir más vistas iniciales.</p>
    <p><strong>Descripción completa:</strong> YouTube lee tu descripción para recomendar tu video a las personas correctas.</p>
    <p><strong>Tags relevantes:</strong> Son como etiquetas que ayudan a YouTube a categorizar tu contenido.</p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_top_videos_nicho(df):
    st.markdown("<h2 class=\"section-header\">🔍 Top Videos del Nicho</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    ### 📊 Los Videos Más Exitosos de Tu Nicho
    
    Estos son los videos con mejor VPH (Vistas Por Hora) en todo el dataset. 
    Analízalos para entender qué funciona en tu nicho y replica sus estrategias.
    """)
    
    # Separar por formato
    df_shorts = df[df[\"formato\"] == \"Short\"]
    df_largos = df[df[\"formato\"] == \"Largo\"]
    
    # Tabs para separar shorts y largos
    tab1, tab2 = st.tabs(["📱 Top 200 Shorts", "🎬 Top 200 Videos Largos"])
    
    with tab1:
        if len(df_shorts) > 0:
            top_shorts = get_top_videos(df_shorts, num_videos=min(200, len(df_shorts)))
            
            st.markdown(f"**📱 Top {len(top_shorts)} Shorts por VPH en el nicho:**")
            
            # Preparar datos para mostrar
            display_shorts = top_shorts.copy()
            display_shorts[\"VPH\"] = display_shorts[\"vph\"].round(1)
            display_shorts[\"Vistas\"] = display_shorts[\"vistas\"].apply(lambda x: f\"{x:,}\")
            display_shorts[\"Duración\"] = display_shorts[\"duracion_segundos\"].apply(lambda x: f\"{int(x)}s\")
            display_shorts[\"Fecha\"] = pd.to_datetime(display_shorts[\"fecha_publicacion\"]).dt.strftime(\"%d/%m/%Y\")
            display_shorts[\"Canal\"] = display_shorts[\"nombre_canal\"]
            display_shorts[\"Título\"] = display_shorts[\"titulo\"].str[:60] + \"...\"
            
            st.dataframe(
                display_shorts[[\"Título\", \"Canal\", \"VPH\", \"Vistas\", \"Duración\", \"Fecha\"]],
                use_container_width=True,
                height=600
            )
            
            # Estadísticas de shorts
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏆 VPH Máximo", f"{top_shorts[\"vph\"].max():.1f}")
            with col2:
                st.metric("📊 VPH Promedio", f"{top_shorts[\"vph\"].mean():.1f}")
            with col3:
                st.metric("⏱️ Duración Promedio", f"{top_shorts[\"duracion_segundos\"].mean():.0f}s")
        else:
            st.warning("No se encontraron videos cortos en los datos.")
    
    with tab2:
        if len(df_largos) > 0:
            top_largos = get_top_videos(df_largos, num_videos=min(200, len(df_largos)))
            
            st.markdown(f"**🎬 Top {len(top_largos)} Videos Largos por VPH en el nicho:**")
            
            # Preparar datos para mostrar
            display_largos = top_largos.copy()
            display_largos[\"VPH\"] = display_largos[\"vph\"].round(1)
            display_largos[\"Vistas\"] = display_largos[\"vistas\"].apply(lambda x: f\"{x:,}\")
            display_largos[\"Duración\"] = display_largos[\"duracion_segundos\"].apply(
                lambda x: f\"{int(x//60)}:{int(x%60):02d}\" if x >= 60 else f\"{int(x)}s\"
            )
            display_largos[\"Fecha\"] = pd.to_datetime(display_largos[\"fecha_publicacion\"]).dt.strftime(\"%d/%m/%Y\")
            display_largos[\"Canal\"] = display_largos[\"nombre_canal\"]
            display_largos[\"Título\"] = display_largos[\"titulo\"].str[:60] + \"...\"
            
            st.dataframe(
                display_largos[[\"Título\", \"Canal\", \"VPH\", \"Vistas\", \"Duración\", \"Fecha\"]],
                use_container_width=True,
                height=600
            )
            
            # Estadísticas de videos largos
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏆 VPH Máximo", f"{top_largos[\"vph\"].max():.1f}")
            with col2:
                st.metric("📊 VPH Promedio", f"{top_largos[\"vph\"].mean():.1f}")
            with col3:
                st.metric("⏱️ Duración Promedio", f"{top_largos[\"duracion_segundos\"].mean()/60:.1f} min")
        else:
            st.warning("No se encontraron videos largos en los datos.")
    
    # Explicación para niños
    st.markdown("""
    <div class="explanation-box">
    <h4>🤔 ¿Cómo usar esta información?</h4>
    <p><strong>Analiza los títulos:</strong> ¿Qué palabras usan? ¿Qué patrones ves?</p>
    <p><strong>Observa las duraciones:</strong> ¿Hay un rango de duración que funciona mejor?</p>
    <p><strong>Estudia los canales:</strong> ¿Qué canales aparecen más seguido en el top?</p>
    <p><strong>Replica estrategias:</strong> Adapta las ideas exitosas a tu propio contenido.</p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_galeria_miniaturas(df):
    st.markdown("<h2 class=\"section-header\">🖼️ Galería de Miniaturas</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎨 Las Miniaturas Más Exitosas del Nicho
    
    Estudia estas miniaturas para entender qué elementos visuales funcionan mejor en tu nicho.
    Observa colores, composición, texto y elementos que llaman la atención.
    """)
    
    # Obtener top videos por VPH
    top_videos = get_top_videos(df, num_videos=min(200, len(df)))
    
    # Filtros para la galería
    col1, col2, col3 = st.columns(3)
    
    with col1:
        formato_filter = st.selectbox(
            "📱 Filtrar por formato:",
            ["Todos", "Short", "Largo"],
            help="Filtra las miniaturas por tipo de video"
        )
    
    with col2:
        num_miniaturas = st.slider(
            "🖼️ Número de miniaturas:",
            min_value=20,
            max_value=min(200, len(top_videos)),
            value=min(100, len(top_videos)),
            step=20
        )
    
    with col3:
        columnas = st.selectbox(
            "📐 Columnas por fila:",
            [3, 4, 5, 6],
            index=1,
            help="Número de miniaturas por fila"
        )
    
    # Aplicar filtros
    if formato_filter != "Todos":
        top_videos_filtered = top_videos[top_videos[\"formato\"] == formato_filter]
    else:
        top_videos_filtered = top_videos
    
    # Limitar número de miniaturas
    top_videos_display = top_videos_filtered.head(num_miniaturas)
    
    st.markdown(f"**🏆 Mostrando las {len(top_videos_display)} miniaturas con mejor VPH:**")
    
    # Mostrar estadísticas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 VPH Promedio", f"{top_videos_display[\"vph\"].mean():.1f}")
    with col2:
        st.metric("👀 Vistas Promedio", f"{top_videos_display[\"vistas\"].mean():,.0f}")
    with col3:
        shorts_count = len(top_videos_display[top_videos_display[\"formato\"] == \"Short\"])
        st.metric("📱 Shorts", shorts_count)
    with col4:
        largos_count = len(top_videos_display[top_videos_display[\"formato\"] == \"Largo\"])
        st.metric("🎬 Largos", largos_count)
    
    # Mostrar miniaturas en grilla
    st.markdown("\""---"\""")
    
    # Crear filas de miniaturas
    videos_list = list(top_videos_display.iterrows())
    
    for i in range(0, len(videos_list), columnas):
        cols = st.columns(columnas)
        
        for j in range(columnas):
            if i + j < len(videos_list):
                idx, video = videos_list[i + j]
                
                with cols[j]:
                    try:
                        # Mostrar miniatura
                        st.image(
                            video[\"url_miniatura\"], 
                            width=200,
                            caption=f"VPH: {video[\"vph\"]:.1f}"
                        )
                        
                        # Información del video
                        st.markdown(f"""
                        **{video[\"formato\"]}** | {video[\"nombre_canal\"][:15]}...
                        
                        {video[\"titulo\"][:40]}...
                        
                        👀 {video[\"vistas\"]:,} vistas
                        """, help=f"Título completo: {video[\"titulo\"]}")
                        
                    except Exception as e:
                        st.error(f"Error cargando miniatura")
                        st.markdown(f"""
                        **{video[\"formato\"]}** | {video[\"nombre_canal\"][:15]}...
                        
                        VPH: {video[\"vph\"]:.1f} | 👀 {video[\"vistas\"]:,}
                        
                        {video[\"titulo\"][:50]}...
                        """)
    
    # Análisis de patrones visuales
    st.markdown("\""---"\""")
    st.markdown("### 🔍 Análisis de Patrones Visuales")
    
    # Separar por formato para análisis
    shorts_miniaturas = top_videos_display[top_videos_display[\"formato\"] == \"Short\"]
    largos_miniaturas = top_videos_display[top_videos_display[\"formato\"] == \"Largo\"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(shorts_miniaturas) > 0:
            st.markdown(f"""
            **📱 Patrones en Shorts ({len(shorts_miniaturas)} miniaturas):**
            - VPH promedio: {shorts_miniaturas[\"vph\"].mean():.1f}
            - Vistas promedio: {shorts_miniaturas[\"vistas\"]}.mean():,.0f}
            - Canales más exitosos: {\", \".join(shorts_miniaturas[\"nombre_canal\"].value_counts().head(3).index)}
            """)
    
    with col2:
        if len(largos_miniaturas) > 0:
            st.markdown(f"""
            **🎬 Patrones en Videos Largos ({len(largos_miniaturas)} miniaturas):**
            - VPH promedio: {largos_miniaturas[\"vph\"].mean():.1f}
            - Vistas promedio: {largos_miniaturas[\"vistas\"]}.mean():,.0f}
            - Canales más exitosos: {\", \".join(largos_miniaturas[\"nombre_canal\"].value_counts().head(3).index)}
            """)
    
    # Explicación para niños
    st.markdown("""
    <div class="explanation-box">
    <h4>🤔 ¿Qué buscar en las miniaturas exitosas?</h4>
    <p><strong>Colores llamativos:</strong> ¿Qué colores usan más? ¿Son brillantes o contrastantes?</p>
    <p><strong>Expresiones faciales:</strong> ¿Las personas muestran emociones fuertes?</p>
    <p><strong>Texto en la miniatura:</strong> ¿Usan palabras grandes y fáciles de leer?</p>
    <p><strong>Composición:</strong> ¿Dónde colocan los elementos principales?</p>
    <p><strong>Consistencia:</strong> ¿Los canales exitosos tienen un estilo similar en todas sus miniaturas?</p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_glosario():
    st.markdown("<h2 class=\"section-header\">❓ Glosario</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="explanation-box">
    <h4>VPH (Vistas Por Hora)</h4>
    <p>El VPH mide qué tan rápido un video consigue vistas después de ser publicado. Es como la velocidad a la que se hace popular. Un VPH alto significa que el video está funcionando muy bien desde el principio.</p>
    
    <h4>Índice de Conexión</h4>
    <p>Este índice nos dice cuánto le gusta tu contenido a la gente. Se calcula viendo cuántos 'me gusta' y comentarios tiene un video en comparación con sus vistas. Un índice alto significa que tu audiencia se conecta mucho con lo que haces.</p>
    
    <h4>Índice CLARA™</h4>
    <p>CLARA es una métrica especial que combina varias cosas importantes de un video (como el VPH, el Índice de Conexión y las vistas) para darte una idea general de su éxito. Es como una puntuación total de lo bien que lo está haciendo un video.</p>
    
    <h4>Shorts vs. Videos Largos</h4>
    <p>YouTube tiene dos tipos principales de videos: los 'Shorts' que son videos muy cortitos (menos de 1 minuto) y los 'Videos Largos' que duran más. Analizamos cuál de los dos funciona mejor para tu canal y para tu nicho.</p>
    
    <h4>Buckets Temáticos</h4>
    <p>Son como 'categorías' o 'grupos' de temas. Agrupamos tus videos por el tema principal del que hablan para ver qué tipo de contenido es el más popular y exitoso en tu canal.</p>
    
    <h4>Miniatura</h4>
    <p>Es la imagen de portada de tu video. Es muy importante porque es lo primero que la gente ve y decide si hace clic o no. Analizamos las miniaturas más exitosas para que aprendas a hacer las tuyas.</p>
    
    <h4>SEO (Search Engine Optimization)</h4>
    <p>El SEO es un conjunto de trucos y estrategias para que tus videos aparezcan más arriba cuando alguien busca algo en YouTube. Incluye usar buenas palabras en el título, la descripción y las etiquetas.</p>
    
    <h4>Vistas Normalizadas</h4>
    <p>Es una forma de comparar las vistas de tus videos de manera justa, sin importar si un video tiene muchas más vistas que otro solo porque lleva mucho tiempo publicado. Ayuda a ver el rendimiento real.</p>
    </div>
    """, unsafe_allow_html=True)

# --- Lógica principal de la aplicación --- #
if df is not None:
    # Pestañas de navegación
    tab_names = [
        "🏠 Resumen Ejecutivo",
        "📊 Posicionamiento General",
        "🚀 Estrategia de Contenido",
        "🏆 Videos Estrella",
        "✍️ Optimización de Títulos",
        "🗓️ Calendario y SEO",
        "🔍 Top Videos del Nicho",
        "🖼️ Galería de Miniaturas",
        "❓ Glosario"
    ]
    
    tabs = st.tabs(tab_names)

    with tabs[0]:
        mostrar_resumen_ejecutivo(df_cliente, metricas_competencia_dict, canal_cliente)
    with tabs[1]:
        mostrar_posicionamiento_general(df_cliente, df_competencia, canal_cliente)
    with tabs[2]:
        mostrar_estrategia_contenido(df_cliente, canal_cliente)
    with tabs[3]:
        mostrar_videos_estrella(df_cliente, canal_cliente)
    with tabs[4]:
        mostrar_optimizacion_titulos(df_cliente, df_competencia, canal_cliente)
    with tabs[5]:
        mostrar_calendario_seo(df_cliente, canal_cliente)
    with tabs[6]:
        mostrar_top_videos_nicho(df)
    with tabs[7]:
        mostrar_galeria_miniaturas(df)
    with tabs[8]:
        mostrar_glosario()
