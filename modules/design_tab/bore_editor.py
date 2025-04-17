# clarinet_simulator/modules/design_tab/bore_editor.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Import the VTK rendering function ---
from ui_components.bore_viewer_3d import render_bore_vtk, display_vtk_in_streamlit
from config import get_current_bore_data
# -----------------------------------------

def create_bore_editor_section():
    """Creates the UI section for bore geometry editing."""
    st.subheader("1. Bore Geometry Editor")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("**Controls & Data**")

        templates = ["Custom", "Buffet R13 (Example)", "Selmer Focus (Example)", "Cylindrical", "Conical"]
        st.session_state.selected_template = st.selectbox("Load Template:", templates, key="sb_template_select")
        if st.button("Load Selected Template"):
            # Example: Add your real template logic here!
            if st.session_state.selected_template == "Buffet R13 (Example)":
                st.session_state.bore_nodes = pd.DataFrame({
                    'position_mm': [0, 5, 15, 30, 50, 65],
                    'diameter_mm': [14.8, 14.85, 14.95, 15.0, 15.1, 15.05]
                })
                st.success(f"Loaded {st.session_state.selected_template}")
            else:
                st.info(f"Template '{st.session_state.selected_template}' loading not implemented yet.")
            st.rerun()

        st.markdown("**Edit Bore Nodes (mm):**")
        st.caption("Drag rows to reorder, double-click cells to edit.")
        edited_df = st.data_editor(
            st.session_state.bore_nodes,
            num_rows="dynamic",
            key="data_editor_bore_nodes",
            column_config={
                "position_mm": st.column_config.NumberColumn("Position (mm)", min_value=0, format="%.2f", required=True),
                "diameter_mm": st.column_config.NumberColumn("Diameter (mm)", min_value=1, max_value=25, format="%.2f", required=True),
            }
        )
        if not edited_df.equals(st.session_state.bore_nodes):
            st.session_state.bore_nodes = edited_df.sort_values(by='position_mm').reset_index(drop=True)
            st.rerun()

        st.session_state.snap_to_wavelength = st.checkbox(
            "Snap nodes to acoustic wavelengths/harmonics",
            value=st.session_state.snap_to_wavelength,
            help="Aligns node positions to calculated acoustic points (Feature 1.1 - Not Implemented)"
        )

        if st.button("Add Node Manually"):
            last_pos = st.session_state.bore_nodes['position_mm'].max() if not st.session_state.bore_nodes.empty else 0
            last_diam = st.session_state.bore_nodes['diameter_mm'].iloc[-1] if not st.session_state.bore_nodes.empty else 15.0
            new_node = pd.DataFrame({'position_mm': [last_pos + 5.0], 'diameter_mm': [last_diam]})
            st.session_state.bore_nodes = pd.concat([st.session_state.bore_nodes, new_node], ignore_index=True).sort_values(by='position_mm').reset_index(drop=True)
            st.rerun()

    with col2:
        st.markdown("**Visualizations**")
        st.markdown("**Bore Profile Preview**")
        fig_profile = go.Figure()
        if not st.session_state.bore_nodes.empty:
            fig_profile.add_trace(go.Scatter(
                x=st.session_state.bore_nodes['position_mm'],
                y=st.session_state.bore_nodes['diameter_mm'],
                mode='lines+markers', name='Bore Diameter'
            ))
            fig_profile.add_trace(go.Scatter(
                x=st.session_state.bore_nodes['position_mm'],
                y=-st.session_state.bore_nodes['diameter_mm']/2,
                mode='lines', name='Bottom Radius', line=dict(color='lightblue', dash='dot')
            ))
            fig_profile.add_trace(go.Scatter(
                x=st.session_state.bore_nodes['position_mm'],
                y=st.session_state.bore_nodes['diameter_mm']/2,
                mode='lines', name='Top Radius', line=dict(color='lightblue', dash='dot')
            ))

        fig_profile.update_layout(
            xaxis_title="Position along bore (mm)",
            yaxis_title="Diameter / Radius (mm)",
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig_profile, use_container_width=True)

        st.markdown("**3D Model Preview**")
        st.session_state.show_cross_section = st.toggle(
            "Show Cross-Section View",
            value=st.session_state.show_cross_section,
            key="toggle_cross_section"
        )

        # --- VTK Rendering Integration ---
        bore_data_for_3d = get_current_bore_data()
        if not bore_data_for_3d.empty and bore_data_for_3d['position_mm'].nunique() >= 2:
            try:
                render_window = render_bore_vtk(
                    bore_nodes_df=bore_data_for_3d,
                    cross_section=st.session_state.show_cross_section,
                    loss_overlay_data=None,
                    key_suffix="design"
                )
                if render_window:
                    display_vtk_in_streamlit(render_window, key="vtk_design_viewer")
                else:
                    st.warning("Failed to generate VTK render window.")
            except ImportError:
                st.error("VTK library not found. Please install `vtk`.")
                st.image(f"https://via.placeholder.com/400x300.png?text=VTK+Error", caption="VTK library missing.")
            except Exception as e:
                st.error(f"An error occurred during VTK rendering: {e}")
                st.image(f"https://via.placeholder.com/400x300.png?text=VTK+Render+Error", caption=f"Error: {e}")
        else:
            st.info("Add at least two distinct bore nodes to generate 3D preview.")
        # ----------------------------------------
