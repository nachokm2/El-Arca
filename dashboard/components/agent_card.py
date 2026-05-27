import streamlit as st

ESTADO_COLORES = {
    "neutral": "#94a3b8",
    "interesado": "#3b82f6",
    "esceptico": "#f97316",
    "adoptado": "#22c55e",
    "rechazado": "#ef4444",
}

ESTADO_EMOJIS = {
    "neutral": "⚪",
    "interesado": "🔵",
    "esceptico": "🟠",
    "adoptado": "🟢",
    "rechazado": "🔴",
}


def render_agent_card(agente: dict, expandir: bool = False):
    estado = agente.get("estado", "neutral")
    color = ESTADO_COLORES.get(estado, "#94a3b8")
    emoji = ESTADO_EMOJIS.get(estado, "⚪")
    interes = agente.get("nivel_interes", 0.0)
    nombre = agente.get("nombre", "Agente")
    id_agente = agente.get("id", "?")

    with st.expander(f"{emoji} **{nombre}** — {estado.capitalize()}", expanded=expandir):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**ID:** {id_agente}")
            st.markdown(f"**Edad:** {agente.get('edad', '?')} años")
            st.markdown(f"**Ciudad:** {agente.get('ciudad', '?')}")
            st.markdown(f"**Género:** {agente.get('genero', '?')}")
        with col2:
            st.markdown(f"**Educación:** {agente.get('nivel_educativo', '?')}")
            st.markdown(f"**Situación:** {agente.get('situacion_laboral', '?')}")
            st.markdown(f"**Ocupación:** {agente.get('ocupacion', '?')}")
            ingreso = agente.get("ingreso_mensual", 0)
            st.markdown(f"**Ingreso:** ${ingreso:,} CLP")
        with col3:
            st.markdown(f"**Estado:** {emoji} {estado}")
            barra_interes = "█" * int(abs(interes) * 10) + "░" * (10 - int(abs(interes) * 10))
            signo = "+" if interes >= 0 else "-"
            st.markdown(f"**Interés:** {signo}{abs(interes):.2f}")
            st.code(barra_interes, language=None)

        with st.container():
            st.markdown("**Perfil psicológico:**")
            pc1, pc2 = st.columns(2)
            with pc1:
                st.progress(agente.get("apertura_cambio", 0.5), text=f"Apertura al cambio: {agente.get('apertura_cambio', 0.5):.2f}")
                st.progress(agente.get("orientacion_logro", 0.5), text=f"Orientación al logro: {agente.get('orientacion_logro', 0.5):.2f}")
            with pc2:
                st.progress(agente.get("aversion_riesgo", 0.5), text=f"Aversión al riesgo: {agente.get('aversion_riesgo', 0.5):.2f}")
                st.progress(agente.get("influenciabilidad", 0.5), text=f"Influenciabilidad: {agente.get('influenciabilidad', 0.5):.2f}")


def render_mini_card(agente: dict):
    """Tarjeta compacta para listados."""
    estado = agente.get("estado", "neutral")
    emoji = ESTADO_EMOJIS.get(estado, "⚪")
    nombre = agente.get("nombre", "?")
    ciudad = agente.get("ciudad", "?")
    interes = agente.get("nivel_interes", 0.0)
    ingreso = agente.get("ingreso_mensual", 0)

    st.markdown(
        f"{emoji} **{nombre}** | {ciudad} | ${ingreso:,} | Interés: {interes:+.2f}"
    )
