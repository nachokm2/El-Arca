import streamlit as st
import json
import pandas as pd
from dashboard.components.agent_card import render_agent_card, render_mini_card, ESTADO_EMOJIS
from dashboard.components.network_graph import render_network_agraph, render_network_plotly, render_leyenda_estados
from ai.agent_factory import AgentFactory, SAVED_DIR


def render_society_view():
    st.title("🌐 Sociedad de Agentes")

    tab_sim, tab_banco = st.tabs(["🔬 Simulación activa", "🗄️ Banco de agentes"])

    with tab_banco:
        _render_banco_agentes()

    with tab_sim:
        _render_simulacion_activa()


def _render_simulacion_activa():
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


# ── banco de agentes guardados ───────────────────────────────────────────────

def _render_banco_agentes():
    guardados = AgentFactory.listar_guardados()

    if not guardados:
        st.info("No hay agentes guardados aún. Genera una simulación con IA y activa **Guardar agentes** para que aparezcan aquí.")
        return

    st.caption(f"{len(guardados)} set(s) guardado(s) en `data/agent_profiles/saved/`")

    nombres = [f"{g['nombre']}  ({g['n_agentes']} agentes · {g['fecha']})" for g in guardados]
    sel = st.selectbox("Seleccionar set", nombres, key="banco_sel")
    idx = nombres.index(sel)
    set_nombre = guardados[idx]["nombre"]

    # Cargar perfiles del set seleccionado
    path = SAVED_DIR / f"{set_nombre}.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    perfiles = data.get("perfiles", [])

    st.subheader(f"{set_nombre} — {len(perfiles)} agentes")

    # Normalizar perfiles (los dataclasses están serializados como dicts anidados)
    def _flat(p: dict) -> dict:
        eco = p.get("perfil_economico", {})
        psi = p.get("perfil_psicologico", {})
        return {
            "nombre":           p.get("nombre", "?"),
            "edad":             p.get("edad", 0),
            "genero":           p.get("genero", "?"),
            "ciudad":           p.get("ciudad", "?"),
            "nivel_educativo":  p.get("nivel_educativo", "?"),
            "situacion_laboral":p.get("situacion_laboral", "?"),
            "ocupacion":        p.get("ocupacion", ""),
            "area_profesional": p.get("area_profesional", ""),
            "activo_en_redes":  p.get("activo_en_redes", True),
            "ingreso_mensual":  eco.get("ingreso_mensual", 0),
            "disposicion_pago": eco.get("disposicion_pago", 0),
            "sensibilidad_precio": eco.get("sensibilidad_precio", 0),
            "apertura_cambio":  psi.get("apertura_cambio", 0),
            "aversion_riesgo":  psi.get("aversion_riesgo", 0),
            "influenciabilidad":psi.get("influenciabilidad", 0),
            "orientacion_logro":psi.get("orientacion_logro", 0),
            "pragmatismo":      psi.get("pragmatismo", 0),
        }

    flat = [_flat(p) for p in perfiles]
    df = pd.DataFrame(flat)

    # Filtros
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        ciudades = sorted(df["ciudad"].unique())
        sel_ciudad = st.multiselect("Ciudad", ciudades, default=ciudades, key="banco_ciudad")
    with fc2:
        edus = sorted(df["nivel_educativo"].unique())
        sel_edu = st.multiselect("Educación", edus, default=edus, key="banco_edu")
    with fc3:
        labs = sorted(df["situacion_laboral"].unique())
        sel_lab = st.multiselect("Situación laboral", labs, default=labs, key="banco_lab")

    mask = (
        df["ciudad"].isin(sel_ciudad) &
        df["nivel_educativo"].isin(sel_edu) &
        df["situacion_laboral"].isin(sel_lab)
    )
    df_fil = df[mask]
    st.caption(f"Mostrando {len(df_fil)} de {len(df)} agentes")

    # Tabla resumen con columnas relevantes
    cols_tabla = ["nombre", "edad", "genero", "ciudad", "nivel_educativo",
                  "situacion_laboral", "ocupacion", "ingreso_mensual",
                  "apertura_cambio", "aversion_riesgo", "orientacion_logro"]
    st.dataframe(
        df_fil[cols_tabla].rename(columns={
            "nombre": "Nombre", "edad": "Edad", "genero": "Género",
            "ciudad": "Ciudad", "nivel_educativo": "Educación",
            "situacion_laboral": "Situación", "ocupacion": "Ocupación",
            "ingreso_mensual": "Ingreso CLP",
            "apertura_cambio": "Apertura", "aversion_riesgo": "Av. Riesgo",
            "orientacion_logro": "Logro",
        }),
        use_container_width=True,
        column_config={
            "Ingreso CLP": st.column_config.NumberColumn(format="$%d"),
            "Apertura":    st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1),
            "Av. Riesgo":  st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1),
            "Logro":       st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1),
        },
    )

    # Detalle individual
    with st.expander("Ver perfil completo de un agente"):
        nombres_lista = df_fil["nombre"].tolist()
        if nombres_lista:
            sel_ag = st.selectbox("Agente", nombres_lista, key="banco_ag_det")
            row = df_fil[df_fil["nombre"] == sel_ag].iloc[0].to_dict()
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f"**{row['nombre']}**")
                st.markdown(f"Edad: {row['edad']} · {row['genero'].capitalize()}")
                st.markdown(f"Ciudad: {row['ciudad']}")
                st.markdown(f"Educación: {row['nivel_educativo']}")
                st.markdown(f"Situación: {row['situacion_laboral']}")
                st.markdown(f"Ocupación: {row['ocupacion']}")
                st.markdown(f"Área: {row['area_profesional']}")
                st.markdown(f"Activo en redes: {'Sí' if row['activo_en_redes'] else 'No'}")
            with col_b:
                st.markdown("**Perfil económico:**")
                st.markdown(f"Ingreso: ${row['ingreso_mensual']:,} CLP")
                st.progress(row['disposicion_pago'], text=f"Disposición de pago: {row['disposicion_pago']:.2f}")
                st.progress(row['sensibilidad_precio'], text=f"Sensibilidad al precio: {row['sensibilidad_precio']:.2f}")
            with col_c:
                st.markdown("**Perfil psicológico:**")
                st.progress(row['apertura_cambio'],  text=f"Apertura al cambio: {row['apertura_cambio']:.2f}")
                st.progress(row['aversion_riesgo'],  text=f"Aversión al riesgo: {row['aversion_riesgo']:.2f}")
                st.progress(row['influenciabilidad'],text=f"Influenciabilidad: {row['influenciabilidad']:.2f}")
                st.progress(row['orientacion_logro'],text=f"Orientación al logro: {row['orientacion_logro']:.2f}")
                st.progress(row['pragmatismo'],      text=f"Pragmatismo: {row['pragmatismo']:.2f}")

    # Descarga
    csv = df_fil.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar set filtrado (CSV)", data=csv,
                       file_name=f"{set_nombre}.csv", mime="text/csv")
