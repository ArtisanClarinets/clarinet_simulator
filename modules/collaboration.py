# clarinet_simulator/modules/collaboration.py
import streamlit as st
from datetime import datetime

def create_collaboration_section(tab_context):
    """Creates the UI for the Collaboration section."""
    # This section could be a tab, or integrated into other tabs
    container = st if tab_context is None else tab_context # Place in main area or specific tab

    container.header("Collaboration & Versioning")
    st.markdown("*(Features 1.2, 1.5 - Placeholders)*")

    st.session_state.collaboration_enabled = st.toggle(
        "Enable Collaboration Features",
        value=st.session_state.collaboration_enabled,
        key="toggle_collaboration"
    )

    if not st.session_state.collaboration_enabled:
        container.warning("Collaboration features are disabled.")
        return

    col1, col2 = container.columns(2)

    with col1:
        container.subheader("Shared Session")
        if st.session_state.collaboration_session_id:
             container.success(f"Connected to session: {st.session_state.collaboration_session_id}")
             container.button("Disconnect") # Add disconnect logic
        else:
             session_id = container.text_input("Enter Session ID to Join:", key="txt_join_session")
             if container.button("Join Session"):
                 # Placeholder: Add logic to connect to backend service
                 st.session_state.collaboration_session_id = session_id or f"Session_{int(datetime.now().timestamp())}"
                 container.rerun()
             if container.button("Start New Session"):
                 st.session_state.collaboration_session_id = f"Session_{int(datetime.now().timestamp())}"
                 # Placeholder: Add logic to register session on backend
                 container.rerun()

        container.markdown("**Live Annotations & Chat** (Requires Backend)")
        annotation = container.text_area("Add Annotation:", key="txt_annotation")
        if container.button("Post Annotation"):
             if annotation:
                 # Placeholder: Send annotation to backend
                 st.session_state.user_annotations.append({'user': 'User1', 'text': annotation, 'time': datetime.now().strftime('%H:%M:%S')})
                 container.rerun()

        # Display annotations
        container.write("Recent Annotations:")
        for note in reversed(st.session_state.user_annotations[-5:]): # Show last 5
            container.caption(f"[{note['time']}] {note['user']}: {note['text']}")


    with col2:
        container.subheader("Version History")
        container.markdown("**(Requires Backend Integration)**")
        # Placeholder display
        versions = ["v1.0 - Initial Design", "v1.1 - Adjusted Taper", "v1.2 - Material Change (Grenadilla)", "v1.3 - Current"]
        selected_version = container.selectbox("View/Revert Version:", versions, index=len(versions)-1)
        container.button(f"Revert to {selected_version}", disabled=(selected_version == versions[-1]))
        container.button("Commit Current Changes as New Version")
