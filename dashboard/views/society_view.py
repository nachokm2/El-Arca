import streamlit as st
import json
import pandas as pd
from dashboard.components.agent_card import render_agent_card, render_mini_card, ESTADO_EMOJIS
from dashboard.components.network_graph import render_network_agraph, render_network_plotly, render_leyenda_estados


def render_society_view():
    st.title("🌐 Sociedad de Agentes")

    experimento_data = st.session_state.get("experimento_activo")
    if not experimento_data:
        st.info("No hay simulación activa. Ve a **Experimento** para correr una simulación.")
        return

    resultados = experimento_data.get("resultados", {})
    agentes = resultados.get("agentes", [])
    metricas_red = resultados.get("metricas_red", {})

    if not agentes:
        st.warning("La simulación no tiene agentes guardados.")
        return

    st.subheader("Métricas de la red social")
    if metricas_red:
        cols = st.columns(len(metricas_red))
        for col, (k, v) in zip(cols, metricas_red.items()):
            with col:
                st.metric(k.replace("_", " ").capitalize(), v)

    st.divider()
    render_leyenda_estados()
    st.divider()

    st.subheader("Visualización de la red")
    st.info("La visualización de red requiere datos en vivo de la simulación. Ejecuta desde el panel de Experimento para ver la red animada.")

    st.divider()
    st.subheader(f"Agentes ({len(agentes)} total)")

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        estados_disponibles = list(set(a["estado"] for a in agentes))
        estado_filtro = st.multiselect(
            "Filtrar por estado",
            options=estados_disponibles,
            default=estados_disponibles,
        )
    with col_filter2:
        ciudades = list(set(a.get("ciudad", "?") for a in agentes))
        ciudad_filtro = st.multiselect(
            "Filtrar por ciudad",
            options=ciudades,
            default=ciudades,
        )

    agentes_filtrados = [
        a for a in agentes
        if a["estado"] in estado_filtro and a.get("ciudad") in ciudad_filtro
    ]
    st.caption(f"Mostrando {len(agentes_filtrados)} de {len(agentes)} agentes")

    vista_detalle = st.toggle("Vista detallada", value=False)
    if vista_detalle:
        for agente in agentes_filtrados[:50]:
            render_agent_card(agente)
        if len(agentes_filtrados) > 50:
            st.info(f"Mostrando primeros 50 agentes. Total: {len(agentes_filtrados)}")
    else:
        for agente in agentes_filtrados[:100]:
            render_mini_card(agente)

    st.divider()
    if st.button("⬇️ Descargar datos de agentes (JSON)"):
        json_str = json.dumps(agentes, ensure_ascii=False, indent=2)
        st.download_button(
            label="Confirmar descarga",
            data=json_str.encode("utf-8"),
            file_name="agentes_simulacion.json",
            mime="application/json",
        )
