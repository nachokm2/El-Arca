import streamlit as st
from programs.templates import list_templates
from programs.evaluator import ProgramEvaluator, ProgramaAcademico


def render_home():
    st.title("🏛️ EL ARCA")
    st.subheader("Simulador de Sociedades Artificiales")
    st.markdown(
        """
        **EL ARCA** permite testear cómo distintos perfiles de personas perciben y adoptan
        programas académicos, campañas y productos, usando agentes autónomos con IA.

        ---
        ### ¿Cómo funciona?
        1. **Define un programa** → precio, modalidad, propuesta de valor
        2. **Configura la sociedad** → número y tipo de agentes
        3. **Corre la simulación** → los agentes interactúan, se influyen y deciden
        4. **Analiza resultados** → tasas de adopción, segmentos, factores clave
        """
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 🤖 Agentes\nPersonas virtuales con perfil socioeconómico y psicológico chileno realista")
    with col2:
        st.info("### 🌐 Red Social\nConectados en topología small-world que difunde información y opiniones")
    with col3:
        st.info("### 📊 Análisis\nKPIs en tiempo real: tasas de adopción, segmentos, factores críticos")

    st.divider()
    st.subheader("Programas disponibles")

    templates = list_templates()
    evaluator = ProgramEvaluator()
    from programs.templates import get_template

    cols = st.columns(2)
    for i, tmpl in enumerate(templates):
        with cols[i % 2]:
            prog = get_template(tmpl["id"])
            ev = evaluator.evaluar(prog)
            score_pct = int(ev.score_global * 100)
            score_color = "🟢" if score_pct >= 65 else "🟡" if score_pct >= 45 else "🔴"
            with st.container(border=True):
                st.markdown(f"**{tmpl['nombre']}**")
                st.markdown(f"💰 ${tmpl['precio_clp']:,} CLP · ⏱ {tmpl['duracion_meses']} meses · 📡 {tmpl['modalidad']}")
                st.markdown(f"Score competitivo: {score_color} **{score_pct}/100**")
                if st.button("Simular este programa", key=f"sim_{tmpl['id']}"):
                    st.session_state["programa_seleccionado"] = prog
                    st.session_state["vista"] = "experimento"
                    st.rerun()

    st.divider()
    st.subheader("Configuración del sistema")
    import config
    api_ok = bool(config.ANTHROPIC_API_KEY)
    if api_ok:
        st.success("✅ API de Anthropic configurada. Agentes con IA disponibles.")
    else:
        st.warning("⚠️ ANTHROPIC_API_KEY no configurada. Los agentes funcionarán sin IA (modo determinístico).")
        st.code("Crea un archivo .env con: ANTHROPIC_API_KEY=tu_clave_aqui")
