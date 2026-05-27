import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def render_kpi_row(resumen: dict):
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            "Tasa de Adopción",
            f"{resumen.get('tasa_adopcion_final', 0):.1%}",
            help="Fracción de agentes que adoptaron el programa",
        )
    with col2:
        st.metric(
            "Interés Medio",
            f"{resumen.get('interes_medio_final', 0):+.3f}",
            help="Promedio del nivel de interés [-1, 1]",
        )
    with col3:
        st.metric(
            "Adoptados",
            resumen.get("conteos_finales", {}).get("adoptado", 0),
        )
    with col4:
        st.metric(
            "Rechazados",
            resumen.get("conteos_finales", {}).get("rechazado", 0),
        )
    with col5:
        paso = resumen.get("paso_adopcion_masiva")
        st.metric(
            "Paso Adopción 50%",
            paso if paso is not None else "No alcanzado",
            help="Primer paso en que más del 50% adoptó",
        )


def render_estado_pie(conteos: dict):
    COLORES = {
        "neutral": "#94a3b8",
        "interesado": "#3b82f6",
        "esceptico": "#f97316",
        "adoptado": "#22c55e",
        "rechazado": "#ef4444",
    }
    labels = list(conteos.keys())
    values = list(conteos.values())
    colors = [COLORES.get(l, "#999") for l in labels]

    fig = go.Figure(data=[
        go.Pie(
            labels=[l.capitalize() for l in labels],
            values=values,
            marker=dict(colors=colors),
            hole=0.4,
        )
    ])
    fig.update_layout(
        title="Distribución final de estados",
        height=300,
        margin=dict(t=40, b=10, l=10, r=10),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_curva_difusion(curva: dict):
    if not curva or not curva.get("pasos"):
        st.info("Sin datos de difusión disponibles.")
        return

    df = pd.DataFrame({
        "Paso": curva["pasos"],
        "Adoptados": curva["adoptados"],
        "Interesados": curva["interesados"],
        "Escépticos": curva["escepticos"],
        "Rechazados": curva["rechazados"],
        "Neutrales": curva["neutros"],
    })

    fig = px.area(
        df.melt(id_vars="Paso", var_name="Estado", value_name="Agentes"),
        x="Paso",
        y="Agentes",
        color="Estado",
        color_discrete_map={
            "Adoptados": "#22c55e",
            "Interesados": "#3b82f6",
            "Escépticos": "#f97316",
            "Rechazados": "#ef4444",
            "Neutrales": "#94a3b8",
        },
        title="Curva de difusión del programa",
    )
    fig.update_layout(height=350, margin=dict(t=40, b=30, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)


def render_interes_linea(curva: dict):
    if not curva or not curva.get("pasos"):
        return
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=curva["pasos"],
        y=curva["interes_medio"],
        mode="lines+markers",
        name="Interés medio",
        line=dict(color="#6366f1", width=2),
        marker=dict(size=4),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8", opacity=0.5)
    fig.update_layout(
        title="Evolución del interés medio",
        yaxis_title="Interés [-1, 1]",
        xaxis_title="Paso de simulación",
        height=280,
        margin=dict(t=40, b=30, l=40, r=10),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_factores_bar(factores: list[dict]):
    if not factores:
        st.info("Sin datos de factores disponibles.")
        return

    df = pd.DataFrame(factores[:8])
    fig = px.bar(
        df,
        x="factor",
        y="diferencia",
        color="diferencia",
        color_continuous_scale="RdYlGn",
        title="Factores que diferencian adoptantes vs no-adoptantes",
        labels={"factor": "Factor", "diferencia": "Diferencia media"},
    )
    fig.update_layout(height=320, margin=dict(t=40, b=60, l=10, r=10))
    fig.update_xaxes(tickangle=30)
    st.plotly_chart(fig, use_container_width=True)
