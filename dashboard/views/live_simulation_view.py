import json
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import networkx as nx

from ai.agent_factory import AgentFactory
from core.society import ArcaSociety
from core.agent import EstadoAgente
from programs.templates import list_templates, get_template
from simulation.experiment import ExperimentConfig

# ── constantes de color ─────────────────────────────────────────────────────

ESTADO_COLOR = {
    "neutral":    "#94a3b8",
    "interesado": "#3b82f6",
    "esceptico":  "#f97316",
    "adoptado":   "#22c55e",
    "rechazado":  "#ef4444",
}
ESTADO_EMOJI = {
    "neutral": "⚪", "interesado": "🔵",
    "esceptico": "🟠", "adoptado": "🟢", "rechazado": "🔴",
}
ESTADOS = [e for e in EstadoAgente]


# ── helpers de snapshot ──────────────────────────────────────────────────────

def _capturar_snapshot(sociedad: ArcaSociety) -> dict:
    conteos = {e.value: 0 for e in EstadoAgente}
    node_states = {}
    for a in sociedad.agentes:
        conteos[a.estado.value] += 1
        node_states[a.unique_id] = {
            "estado": a.estado.value,
            "nivel_interes": round(a.nivel_interes, 3),
            "nombre": a.nombre,
            "ciudad": a.ciudad,
            "ocupacion": a.ocupacion,
        }
    total = len(sociedad.agentes)
    return {
        "step": sociedad.steps,
        "node_states": node_states,
        "conteos": conteos,
        "tasa_adopcion": conteos["adoptado"] / max(total, 1),
        "interes_medio": float(np.mean([a.nivel_interes for a in sociedad.agentes])),
    }


def _run_simulation(cfg: ExperimentConfig) -> dict:
    factory = AgentFactory(use_ai=False)
    perfiles = factory.crear_sociedad(n=cfg.n_agentes, arquetipos=None)
    sociedad = ArcaSociety(
        perfiles=perfiles,
        programa=cfg.programa,
        topologia_red=cfg.topologia_red,
        seed=cfg.seed,
    )

    grafo = sociedad.network.grafo
    edges = [{"from": str(u), "to": str(v)} for u, v in grafo.edges()]
    pos = nx.spring_layout(grafo, seed=cfg.seed)
    node_positions = {str(nid): {"x": float(xy[0]), "y": float(xy[1])}
                      for nid, xy in pos.items()}

    snapshots = [_capturar_snapshot(sociedad)]
    for _ in range(cfg.n_pasos):
        sociedad.step()
        snapshots.append(_capturar_snapshot(sociedad))

    return {
        "snapshots": snapshots,
        "edges": edges,
        "node_positions": node_positions,
        "agentes_base": {
            str(a.unique_id): {
                "nombre": a.nombre,
                "ciudad": a.ciudad,
                "ocupacion": a.ocupacion,
                "nivel_educativo": a.nivel_educativo,
                "ingreso_mensual": a.economico.ingreso_mensual,
            }
            for a in sociedad.agentes
        },
        "metricas_red": sociedad.network.get_metricas(),
        "n_agentes": cfg.n_agentes,
        "n_pasos": cfg.n_pasos,
        "programa": cfg.programa,
    }


# ── figura animada (todos los frames en Plotly, sin reruns) ─────────────────

def _node_traces_for_snapshot(snapshot: dict, pos: dict, mostrar_labels: bool) -> list:
    """Devuelve una traza por estado (siempre 5, vacías si no hay nodos)."""
    node_states = snapshot["node_states"]
    traces = []
    for estado in ESTADOS:
        nids = [nid for nid, s in node_states.items() if s["estado"] == estado.value]
        xs = [pos[str(nid)]["x"] for nid in nids]
        ys = [pos[str(nid)]["y"] for nid in nids]
        hover = [
            f"<b>{node_states[nid]['nombre']}</b><br>"
            f"{node_states[nid]['ocupacion']}<br>"
            f"{node_states[nid]['ciudad']}<br>"
            f"Interés: {node_states[nid]['nivel_interes']:+.3f}"
            for nid in nids
        ]
        labels = [node_states[nid]["nombre"].split()[0] for nid in nids] if mostrar_labels else [""] * len(nids)
        traces.append(go.Scatter(
            x=xs, y=ys,
            mode="markers+text" if (mostrar_labels and nids) else "markers",
            name=f"{ESTADO_EMOJI[estado.value]} {estado.value.capitalize()}",
            marker=dict(
                color=ESTADO_COLOR[estado.value],
                size=12,
                line=dict(width=1.5, color="white"),
                opacity=0.92,
            ),
            text=labels,
            textposition="top center",
            textfont=dict(size=8),
            hovertemplate="%{customdata}<extra></extra>" if nids else "%{x}<extra></extra>",
            customdata=hover,
            showlegend=True,
        ))
    return traces


def _build_animated_figure(sim_data: dict, mostrar_labels: bool = False, frame_ms: int = 400) -> go.Figure:
    snapshots = sim_data["snapshots"]
    edges = sim_data["edges"]
    pos = sim_data["node_positions"]
    n_pasos = sim_data["n_pasos"]

    # Aristas (estáticas)
    edge_x, edge_y = [], []
    for e in edges:
        x0, y0 = pos[e["from"]]["x"], pos[e["from"]]["y"]
        x1, y1 = pos[e["to"]]["x"], pos[e["to"]]["y"]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=0.6, color="#cbd5e1"),
        hoverinfo="none",
        showlegend=False,
    )

    # Frame inicial
    initial_data = [edge_trace] + _node_traces_for_snapshot(snapshots[0], pos, mostrar_labels)

    # Todos los frames
    frames = []
    for i, snap in enumerate(snapshots):
        tasa = snap["tasa_adopcion"]
        interes = snap["interes_medio"]
        frames.append(go.Frame(
            data=[edge_trace] + _node_traces_for_snapshot(snap, pos, mostrar_labels),
            name=str(i),
            layout=go.Layout(title=dict(
                text=f"<b>Paso {i} / {n_pasos}</b>"
                     f"   |   Adopción: {tasa:.1%}"
                     f"   |   Interés medio: {interes:+.3f}",
            )),
        ))

    slider_steps = [
        {
            "args": [[str(i)], {
                "frame": {"duration": 0, "redraw": True},
                "mode": "immediate",
                "transition": {"duration": 0},
            }],
            "label": str(i),
            "method": "animate",
        }
        for i in range(len(snapshots))
    ]

    snap0 = snapshots[0]
    fig = go.Figure(
        data=initial_data,
        frames=frames,
        layout=go.Layout(
            title=dict(
                text=f"<b>Paso 0 / {n_pasos}</b>"
                     f"   |   Adopción: {snap0['tasa_adopcion']:.1%}"
                     f"   |   Interés medio: {snap0['interes_medio']:+.3f}",
                font=dict(size=14),
                x=0.02,
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="right", x=1,
                font=dict(size=11),
            ),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="#f8fafc",
            paper_bgcolor="#f8fafc",
            height=540,
            margin=dict(t=70, b=100, l=10, r=10),
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                y=-0.10,
                x=0.0,
                xanchor="left",
                yanchor="top",
                pad=dict(r=8, t=4),
                buttons=[
                    dict(
                        label="▶ Play",
                        method="animate",
                        args=[None, dict(
                            frame=dict(duration=frame_ms, redraw=True),
                            fromcurrent=True,
                            transition=dict(duration=frame_ms // 4, easing="linear"),
                        )],
                    ),
                    dict(
                        label="⏸ Pausa",
                        method="animate",
                        args=[[None], dict(
                            frame=dict(duration=0, redraw=False),
                            mode="immediate",
                            transition=dict(duration=0),
                        )],
                    ),
                ],
            )],
            sliders=[dict(
                active=0,
                steps=slider_steps,
                x=0.09,
                y=0,
                xanchor="left",
                yanchor="top",
                len=0.91,
                currentvalue=dict(
                    prefix="Paso: ",
                    visible=True,
                    xanchor="right",
                    font=dict(size=12),
                ),
                transition=dict(duration=0),
                pad=dict(b=8),
            )],
        ),
    )
    return fig


# ── componentes auxiliares ───────────────────────────────────────────────────

def _render_barra_estados(conteos: dict, total: int):
    cols = st.columns(5)
    estados = ["neutral", "interesado", "esceptico", "adoptado", "rechazado"]
    for col, estado in zip(cols, estados):
        n = conteos.get(estado, 0)
        pct = n / max(total, 1)
        with col:
            st.metric(
                label=f"{ESTADO_EMOJI[estado]} {estado.capitalize()}",
                value=n,
                delta=f"{pct:.0%}",
                delta_color="off",
            )


def _render_mini_curva(snapshots: list):
    pasos = [s["step"] for s in snapshots]
    adoptados  = [s["conteos"].get("adoptado", 0)   for s in snapshots]
    interesados= [s["conteos"].get("interesado", 0) for s in snapshots]
    rechazados = [s["conteos"].get("rechazado", 0)  for s in snapshots]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pasos, y=adoptados, name="Adoptados",
                             fill="tozeroy", line=dict(color="#22c55e", width=2)))
    fig.add_trace(go.Scatter(x=pasos, y=interesados, name="Interesados",
                             line=dict(color="#3b82f6", width=1.5, dash="dot")))
    fig.add_trace(go.Scatter(x=pasos, y=rechazados, name="Rechazados",
                             line=dict(color="#ef4444", width=1.5, dash="dot")))
    fig.update_layout(
        height=180,
        margin=dict(t=10, b=30, l=30, r=10),
        showlegend=True,
        legend=dict(orientation="h", y=-0.4, font=dict(size=10)),
        xaxis=dict(title="Paso", tickfont=dict(size=9)),
        yaxis=dict(title="Agentes", tickfont=dict(size=9)),
        plot_bgcolor="#f8fafc",
        paper_bgcolor="#f8fafc",
    )
    st.plotly_chart(fig, use_container_width=True, key="minicurva")


# ── vista principal ──────────────────────────────────────────────────────────

def render_live_simulation():
    st.title("🎬 Simulación en Vivo")
    st.caption("Animación fluida — los frames corren en el browser sin recargar la página")

    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⚙️ Configurar simulación")

        templates = list_templates()
        nombres = [t["nombre"] for t in templates]
        idx_template = st.selectbox("Programa", range(len(nombres)),
                                    format_func=lambda i: nombres[i], key="live_template")
        programa = get_template(templates[idx_template]["id"])

        n_agentes = st.slider("Agentes", 15, 120, 40, 5, key="live_n")
        n_pasos   = st.slider("Pasos",    5,  40, 15, 1, key="live_pasos")
        topologia = st.selectbox("Topología de red",
                                  ["small_world", "scale_free", "comunidades", "random"],
                                  key="live_topo")
        seed = st.number_input("Semilla", 1, 9999, 42, key="live_seed")

        if st.button("▶ Ejecutar nueva simulación", type="primary", use_container_width=True):
            cfg = ExperimentConfig(
                nombre="Live Sim",
                descripcion="Simulación en vivo",
                n_agentes=n_agentes,
                n_pasos=n_pasos,
                topologia_red=topologia,
                programa=programa,
                seed=int(seed),
                usar_ia=False,
            )
            with st.spinner(f"Corriendo {n_pasos} pasos con {n_agentes} agentes…"):
                sim_data = _run_simulation(cfg)
            st.session_state["live_sim_data"] = sim_data
            st.rerun()

    # ── contenido principal ──────────────────────────────────────────────────
    sim_data = st.session_state.get("live_sim_data")

    if sim_data is None:
        st.info("Configura los parámetros en el panel izquierdo y pulsa **▶ Ejecutar nueva simulación**.")
        _render_ejemplo_vacio()
        return

    snapshots = sim_data["snapshots"]
    n_total   = sim_data["n_agentes"]

    # Opciones + velocidad en una fila
    opt1, opt2, opt3 = st.columns([2, 2, 3])
    with opt1:
        mostrar_labels = st.toggle("Mostrar nombres", value=False, key="live_labels")
    with opt2:
        mostrar_curva = st.toggle("Mostrar curva", value=True, key="live_curva")
    with opt3:
        velocidad = st.select_slider(
            "Velocidad de animación",
            options=["0.25×", "0.5×", "1×", "2×", "4×"],
            value="1×",
            key="live_vel",
        )

    dur_map = {"0.25×": 1200, "0.5×": 700, "1×": 400, "2×": 200, "4×": 100}
    frame_ms = dur_map[velocidad]

    # Figura animada completa (play/pause/slider nativos de Plotly)
    fig = _build_animated_figure(sim_data, mostrar_labels=mostrar_labels, frame_ms=frame_ms)
    st.plotly_chart(fig, use_container_width=True, key="live_graph")

    # Curva de difusión completa
    if mostrar_curva:
        _render_mini_curva(snapshots)

    # Métricas del estado final
    st.markdown("**Estado final de la sociedad:**")
    _render_barra_estados(snapshots[-1]["conteos"], n_total)

    # Resumen / descarga
    with st.expander("📊 Resumen y descarga", expanded=False):
        snap_final = snapshots[-1]
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Tasa de adopción final", f"{snap_final['tasa_adopcion']:.1%}")
            st.metric("Interés medio final",    f"{snap_final['interes_medio']:+.3f}")
        with col_b:
            st.metric("Total pasos", sim_data["n_pasos"])
            red = sim_data.get("metricas_red", {})
            if red:
                st.metric("Densidad de red",  red.get("densidad", "—"))
                st.metric("Grado promedio",   red.get("grado_promedio", "—"))

        payload = json.dumps(snap_final, ensure_ascii=False, indent=2)
        st.download_button(
            "⬇️ Descargar estado final (JSON)",
            data=payload.encode("utf-8"),
            file_name="paso_final.json",
            mime="application/json",
        )


def _render_ejemplo_vacio():
    st.markdown("---")
    st.caption("Vista previa de la interfaz (datos de ejemplo):")

    G = nx.watts_strogatz_graph(30, 4, 0.15, seed=7)
    pos = nx.spring_layout(G, seed=7)
    import random
    rng = random.Random(7)
    estados_demo = ["neutral", "interesado", "esceptico", "adoptado", "rechazado"]
    pesos = [0.3, 0.25, 0.15, 0.2, 0.1]
    colores = [ESTADO_COLOR[rng.choices(estados_demo, pesos)[0]] for _ in G.nodes()]

    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines",
                              line=dict(width=0.6, color="#e2e8f0"), hoverinfo="none",
                              showlegend=False))
    fig.add_trace(go.Scatter(
        x=[pos[n][0] for n in G.nodes()],
        y=[pos[n][1] for n in G.nodes()],
        mode="markers",
        marker=dict(color=colores, size=12, line=dict(width=1.5, color="white")),
        hoverinfo="none",
        showlegend=False,
    ))
    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="#f8fafc", paper_bgcolor="#f8fafc",
        height=350, margin=dict(t=30, b=10, l=10, r=10),
        title="Ejemplo: red social de 30 agentes (datos sintéticos)",
    )
    st.plotly_chart(fig, use_container_width=True)
