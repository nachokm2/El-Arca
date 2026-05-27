import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

st.set_page_config(
    page_title="EL ARCA — Simulador de Sociedades",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from dashboard.views.home import render_home
from dashboard.views.live_simulation_view import render_live_simulation
from dashboard.views.society_view import render_society_view
from dashboard.views.experiment_view import render_experiment_view
from dashboard.views.results_view import render_results_view


VISTAS = {
    "inicio":     ("🏠 Inicio",              render_home),
    "live":       ("🎬 Simulación en Vivo",  render_live_simulation),
    "experimento":("🧪 Experimento",         render_experiment_view),
    "sociedad":   ("🌐 Sociedad",            render_society_view),
    "resultados": ("📊 Resultados",          render_results_view),
}


def main():
    if "vista" not in st.session_state:
        st.session_state["vista"] = "inicio"

    with st.sidebar:
        st.markdown("## 🏛️ EL ARCA")
        st.markdown("*Simulador de Sociedades Artificiales*")
        st.divider()

        for key, (label, _) in VISTAS.items():
            is_active = st.session_state["vista"] == key
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{key}", type=btn_type, use_container_width=True):
                st.session_state["vista"] = key
                st.rerun()

        st.divider()

        # estado rápido de sesión
        live_data = st.session_state.get("live_sim_data")
        exp_activo = st.session_state.get("experimento_activo")
        prog_activo = st.session_state.get("programa_activo")

        if live_data:
            n = live_data.get("n_agentes", 0)
            pasos = live_data.get("n_pasos", 0)
            snap_final = live_data["snapshots"][-1]
            tasa = snap_final.get("tasa_adopcion", 0)
            st.markdown("**Simulación en vivo:**")
            st.markdown(f"🤖 {n} agentes · {pasos} pasos · 🟢 {tasa:.1%}")
        elif exp_activo:
            resultados = exp_activo.get("resultados", {})
            tasa = resultados.get("tasa_adopcion_final", 0)
            n = exp_activo.get("n_agentes", 0)
            st.markdown("**Experimento activo:**")
            st.markdown(f"🤖 {n} agentes · 🟢 {tasa:.1%}")
        elif prog_activo:
            st.markdown("**Programa seleccionado:**")
            st.caption(prog_activo.get("nombre", "?")[:40])
        else:
            st.caption("Sin simulación activa")

        st.divider()
        st.caption("EL ARCA v1.0")
        st.caption("Universidad Autónoma de Chile")

    vista_key = st.session_state.get("vista", "inicio")
    _, render_fn = VISTAS.get(vista_key, ("Inicio", render_home))
    render_fn()


if __name__ == "__main__":
    main()
