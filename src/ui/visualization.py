
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

    # Ensure we have data
    if not bore_x:
        st.warning("No bore geometry defined.")
        return

    for bx, br in zip(bore_x, bore_r):
        x.append(bx)
        y_top.append(br)
        y_bot.append(-br)

    fig = go.Figure()

    # Bore
    fig.add_trace(go.Scatter(
        x=x, y=y_top,
        mode='lines',
        name='Bore Profile',
        line=dict(color='#1E3A8A', width=2),
        fill=None
    ))
    fig.add_trace(go.Scatter(
        x=x, y=y_bot,
        mode='lines',
        name='Bore Bottom',
        line=dict(color='#1E3A8A', width=2),
        fill='tonexty', # Fill between top and bottom
        fillcolor='rgba(30, 58, 138, 0.1)',
        showlegend=False
    ))

    # Holes
    for h in clarinet.holes:
        # Draw holes as vertical lines/markers
        # Chimney visualization: line from radius to radius + chimney
        fig.add_trace(go.Scatter(
            x=[h.position, h.position],
            y=[h.radius, h.radius + h.chimney],
            mode='lines+markers',
            name=f"{h.label}",
            text=f"Pos: {h.position:.3f}m<br>Rad: {h.radius*1000:.1f}mm<br>Chim: {h.chimney*1000:.1f}mm",
            hoverinfo="text",
            marker=dict(symbol='circle-open', size=8, color='#EF4444'),
            line=dict(color='#EF4444', width=3)
        ))

        # Mirror hole on bottom for visual completeness?
        # Usually tone holes are on one side, but let's keep it simple.

    fig.update_layout(
        title="Instrument Geometry Visualization",
        xaxis_title="Position along Axis (m)",
        yaxis_title="Bore Radius (m)",
        yaxis=dict(scaleanchor="x", scaleratio=0.2), # Exaggerate Y slightly for visibility
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="closest"
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_impedance_interactive(frequencies, impedance, title="Input Impedance", show_phase=False, ref_freqs=None, ref_imp=None, ref_label="Reference"):
    """
    Interactive impedance plot using Plotly.
    Supports overlaying a reference trace.
    """
    mag_db = 20 * np.log10(np.abs(impedance))

    fig = go.Figure()

    # Main Trace
    fig.add_trace(go.Scatter(
        x=frequencies, y=mag_db,
        mode='lines',
        name='Current Design',
        line=dict(color='#2563EB', width=2)
    ))

    # Reference Trace
    if ref_freqs is not None and ref_imp is not None:
        ref_mag_db = 20 * np.log10(np.abs(ref_imp))
        fig.add_trace(go.Scatter(
            x=ref_freqs, y=ref_mag_db,
            mode='lines',
            name=ref_label,
            line=dict(color='#9CA3AF', width=2, dash='dash')
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Frequency (Hz)",
        yaxis_title="Magnitude (dB)",
        hovermode="x unified",
        template="plotly_white",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_phase_interactive(frequencies, impedance):
    """
    Interactive Phase plot.
    """
    phase_rad = np.angle(impedance)
    phase_deg = np.rad2deg(phase_rad)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=frequencies, y=phase_deg,
        mode='lines',
        name='Phase',
        line=dict(color='#10B981', width=1.5)
    ))

    fig.update_layout(
        title="Input Impedance Phase",
        xaxis_title="Frequency (Hz)",
        yaxis_title="Phase (Degrees)",
        hovermode="x unified",
        template="plotly_white",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)
