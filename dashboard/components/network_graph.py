import streamlit as st
try:
    from streamlit_agraph import agraph, Node, Edge, Config
    AGRAPH_AVAILABLE = True
except ImportError:
    AGRAPH_AVAILABLE = False

import plotly.graph_objects as go
import networkx as nx

ESTADO_COLORES = {
    "neutral": "#94a3b8",
    "interesado": "#3b82f6",
    "esceptico": "#f97316",
    "adoptado": "#22c55e",
    "rechazado": "#ef4444",
}


def render_network_agraph(nodes_data: list[dict], edges_data: list[dict]):
    if not AGRAPH_AVAILABLE:
        st.warning("streamlit-agraph no está instalado. Usa `pip install streamlit-agraph`.")
        return

    nodes = [
        Node(
            id=n["id"],
            label=n.get("label", n["id"])[:12],
            color=n.get("color", "#94a3b8"),
            size=n.get("size", 15),
            title=n.get("title", ""),
        )
        for n in nodes_data
    ]
    edges = [
        Edge(source=e["from"], target=e["to"])
        for e in edges_data
    ]

    config = Config(
        width=750,
        height=500,
        directed=False,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#f0a500",
        collapsible=False,
        node={"labelProperty": "label"},
        link={"labelProperty": "label", "renderLabel": False},
    )
    agraph(nodes=nodes, edges=edges, config=config)


def render_network_plotly(grafo: nx.Graph, agentes_dict: dict):
    """Alternativa con Plotly cuando agraph no está disponible."""
    if grafo.number_of_nodes() == 0:
        st.info("La red está vacía.")
        return

    pos = nx.spring_layout(grafo, seed=42)

    edge_x, edge_y = [], []
    for u, v in grafo.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=0.5, color="#d1d5db"),
        hoverinfo="none",
    )

    node_x, node_y, node_colors, node_text = [], [], [], []
    for node_id in grafo.nodes():
        x, y = pos[node_id]
        node_x.append(x)
        node_y.append(y)
        estado = grafo.nodes[node_id].get("estado", "neutral")
        nombre = grafo.nodes[node_id].get("nombre", str(node_id))
        node_colors.append(ESTADO_COLORES.get(estado, "#94a3b8"))
        node_text.append(f"{nombre}<br>{estado}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers",
        hoverinfo="text",
        text=node_text,
        marker=dict(
            showscale=False,
            color=node_colors,
            size=8,
            line=dict(width=1, color="#fff"),
        ),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Red social de agentes",
            showlegend=False,
            hovermode="closest",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=500,
            margin=dict(t=40, b=10, l=10, r=10),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_leyenda_estados():
    st.markdown("**Leyenda:**")
    cols = st.columns(5)
    estados = [
        ("neutral", "Neutral"),
        ("interesado", "Interesado"),
        ("esceptico", "Escéptico"),
        ("adoptado", "Adoptado"),
        ("rechazado", "Rechazado"),
    ]
    emojis = ["⚪", "🔵", "🟠", "🟢", "🔴"]
    for col, (estado, label), emoji in zip(cols, estados, emojis):
        with col:
            st.markdown(f"{emoji} {label}")
