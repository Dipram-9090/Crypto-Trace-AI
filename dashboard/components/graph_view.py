"""
Network graph visualization component.
"""
import networkx as nx
import plotly.graph_objects as go


def plot_forensic_subgraph(G_sub: nx.DiGraph, center_node: str = "") -> go.Figure:
    """Render interactive Plotly 2D Network graph for forensic exploration."""
    if len(G_sub.nodes) == 0:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_dark",
            annotations=[dict(text="No Graph Data Available", showarrow=False, font=dict(size=16))]
        )
        return fig

    pos = nx.spring_layout(G_sub, seed=42, k=0.45, iterations=50)

    edge_x, edge_y = [], []
    for edge in G_sub.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.2, color='rgba(148, 163, 184, 0.4)'),
        hoverinfo='none',
        mode='lines'
    )

    node_x, node_y, node_text, node_color, node_size, node_symbols = [], [], [], [], [], []
    color_map = {
        "Transaction": "#3b82f6",
        "Wallet": "#10b981",
        "IP": "#f59e0b",
        "ASN": "#8b5cf6",
        "Country": "#ec4899"
    }

    for node in G_sub.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        attrs = G_sub.nodes[node]
        ntype = attrs.get("node_type", "Unknown")
        label = attrs.get("label", 2)
        entity_type = attrs.get("entity_type", "")
        is_center = (node == center_node)

        if is_center:
            color = "#ef4444"
            size = 24
        elif label == 1:
            color = "#dc2626"
            size = 18
        else:
            color = color_map.get(ntype, "#94a3b8")
            size = 14 if ntype == "Wallet" else (16 if ntype == "Transaction" else 12)

        node_color.append(color)
        node_size.append(size)
        node_symbols.append("star" if is_center else "circle")

        hover_info = f"<b>{ntype}</b>: {node}<br>"
        if entity_type: hover_info += f"Archetype: {entity_type}<br>"
        if "country" in attrs: hover_info += f"Country: {attrs['country']}<br>"
        if "asn" in attrs: hover_info += f"ASN: {attrs['asn']}<br>"
        if label in [0, 1]: hover_info += f"Class: {'Suspicious' if label == 1 else 'Licit'}"

        node_text.append(hover_info)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[n if len(n) <= 12 else n[:8] + ".." for n in G_sub.nodes()],
        textposition="bottom center",
        textfont=dict(size=9, color="#94a3b8"),
        hovertext=node_text,
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            symbol=node_symbols,
            line=dict(width=1.5, color='rgba(255,255,255,0.6)')
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=10, l=10, r=10, t=25),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor='rgba(15, 23, 42, 0.6)',
        plot_bgcolor='rgba(15, 23, 42, 0.6)',
        height=520
    )
    return fig
