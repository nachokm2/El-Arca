import json
import streamlit as st
import pandas as pd
import plotly.express as px
from simulation.analyzer import ResultsAnalyzer
from simulation.runner import SimulationRunner
from dashboard.components.metrics_panel import (
    render_kpi_row,
    render_estado_pie,
    render_curva_difusion,
    render_interes_linea,
    render_factores_bar,
)


def render_results_view():
    st.title("📊 Resultados")

    tab_activo, tab_historico = st.tabs(["🔬 Simulación Activa", "📁 Historial"])

    with tab_activo:
        _render_resultados_activos()

    with tab_historico:
        _render_historico()


def _render_resultados_activos():
    exp_data = st.session_state.get("experimento_activo")
    if not exp_data:
        st.info("No hay simulación activa. Ve a **Experimento** y ejecuta una simulación primero.")
        return

    config_data = {
        "nombre": exp_data.get("nombre", "?"),
        "n_agentes": exp_data.get("n_agentes", 0),
        "n_pasos": exp_data.get("n_pasos", 0),
        "programa": exp_data.get("programa", {}),
    }

    st.subheader(f"Experimento: {config_data['nombre']}")
    st.caption(
        f"Agentes: {config_data['n_agentes']} · "
        f"Pasos: {config_data['n_pasos']} · "
        f"Programa: {config_data['programa'].get('nombre', '?')}"
    )

    analyzer = ResultsAnalyzer(exp_data)
    resumen = analyzer.resumen_ejecutivo()
    curva = analyzer.curva_difusion()
    factores = analyzer.factores_criticos()
    recomendaciones = analyzer.recomendaciones()
    segmentos = analyzer.segmentar_por_perfil()

    st.subheader("KPIs de adopción")
    render_kpi_row(resumen)

    col_pie, col_linea = st.columns(2)
    with col_pie:
        render_estado_pie(resumen.get("conteos_finales", {}))
    with col_linea:
        render_interes_linea(curva)

    st.subheader("Curva de difusión")
    render_curva_difusion(curva)

    st.subheader("Factores que diferencian a los adoptantes")
    render_factores_bar(factores)

    col_seg1, col_seg2 = st.columns(2)
    with col_seg1:
        st.subheader("Adopción por nivel educativo")
        _render_segmento_tabla(segmentos.get("nivel_educativo", {}))

    with col_seg2:
        st.subheader("Adopción por ciudad")
        _render_segmento_tabla(segmentos.get("ciudad", {}))

    st.subheader("Adopción por segmento de ingreso")
    _render_segmento_tabla(segmentos.get("segmento_ingreso", {}))

    st.subheader("💡 Recomendaciones")
    for rec in recomendaciones:
        st.markdown(f"- {rec}")

    st.divider()
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        if st.button("⬇️ Descargar resultados completos (JSON)"):
            json_str = json.dumps(exp_data, ensure_ascii=False, indent=2, default=str)
            st.download_button(
                "Confirmar descarga JSON",
                data=json_str.encode("utf-8"),
                file_name=f"elarca_{exp_data.get('id', 'resultado')}.json",
                mime="application/json",
            )
    with col_dl2:
        agentes = exp_data.get("resultados", {}).get("agentes", [])
        if agentes:
            df = pd.DataFrame(agentes)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Descargar agentes (CSV)",
                data=csv,
                file_name="agentes.csv",
                mime="text/csv",
            )


def _render_historico():
    runner = SimulationRunner()
    experimentos = runner.listar_experimentos()

    if not experimentos:
        st.info("No hay experimentos guardados aún.")
        return

    st.subheader(f"{len(experimentos)} experimentos guardados")

    for exp in sorted(experimentos, key=lambda x: x.get("id", ""), reverse=True):
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 2, 1])
            with c1:
                estado_emoji = "✅" if exp["estado"] == "completado" else "❌"
                st.markdown(f"{estado_emoji} **{exp['nombre']}** (ID: {exp['id']})")
                st.caption(f"Agentes: {exp['n_agentes']}")
            with c2:
                tasa = exp.get("tasa_adopcion", 0)
                st.metric("Tasa adopción", f"{tasa:.1%}")
            with c3:
                if st.button("Cargar", key=f"load_{exp['id']}"):
                    datos = runner.cargar_experimento(exp["archivo"])
                    st.session_state["experimento_activo"] = datos
                    st.success("Experimento cargado.")
                    st.rerun()


def _render_segmento_tabla(segmento_data: dict):
    if not segmento_data:
        st.caption("Sin datos de segmentación.")
        return
    df = pd.DataFrame(segmento_data).T.fillna(0)
    df = df.rename(columns=lambda c: c.capitalize())
    col_cfg = {col: st.column_config.ProgressColumn(col, format="%.0f%%", min_value=0, max_value=1)
               for col in df.columns}
    st.dataframe(df, column_config=col_cfg, use_container_width=True)
