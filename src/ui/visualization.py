
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import streamlit as st

def plot_geometry(clarinet):
    """
    Visualizes the clarinet geometry.
    """
    # Bore
    bore_x = [b.position for b in clarinet.bore]
    bore_r = [b.radius for b in clarinet.bore]

    # Create symmetrical profile for plotting
    x = []
    y_top = []
    y_bot = []

    for bx, br in zip(bore_x, bore_r):
        x.append(bx)
        y_top.append(br)
        y_bot.append(-br)

    fig = go.Figure()

    # Bore
    fig.add_trace(go.Scatter(x=x, y=y_top, mode='lines', name='Bore Top', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=x, y=y_bot, mode='lines', name='Bore Bottom', line=dict(color='blue'), fill='tonexty'))

    # Holes
    for h in clarinet.holes:
        # Draw a marker or a small rectangle for holes
        fig.add_trace(go.Scatter(
            x=[h.position, h.position],
            y=[h.radius, h.radius + h.chimney],
            mode='lines+markers',
            name=f"Hole {h.label}",
            line=dict(color='red', width=4)
        ))

    fig.update_layout(
        title="Clarinet Geometry",
        xaxis_title="Position (m)",
        yaxis_title="Radius (m)",
        yaxis=dict(scaleanchor="x", scaleratio=1),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_impedance_interactive(frequencies, impedance):
    """
    Interactive impedance plot using Plotly.
    """
    mag_db = 20 * np.log10(impedance)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=frequencies, y=mag_db, mode='lines', name='Impedance'))

    fig.update_layout(
        title="Input Impedance",
        xaxis_title="Frequency (Hz)",
        yaxis_title="Magnitude (dB)",
        hovermode="x"
    )

    st.plotly_chart(fig, use_container_width=True)
