import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from wheel_data import CATEGORIES, export_assessments, import_assessments

# Define life categories
categories = list(CATEGORIES)

# Initialize session state
if "saved_wheels" not in st.session_state:
    st.session_state.saved_wheels = {}

# --- Main Title ---
st.title("Life Wheel Web App")

# --- Input Sliders ---
st.header("1. Current Life Wheel")
with st.sidebar:
    st.header("Life Wheel Inputs")
    wheel_name = st.text_input("Wheel Name", value="My Life Wheel")
    scores = [st.slider(cat, 0, 10, 5) for cat in categories]
    if st.button("Save This Wheel"):
        if not wheel_name.strip():
            st.error("Enter a non-empty wheel name.")
        elif wheel_name in st.session_state.saved_wheels:
            st.error("That name already exists. Choose another name to preserve the saved wheel.")
        else:
            st.session_state.saved_wheels[wheel_name] = scores.copy()
            st.success(f"Wheel '{wheel_name}' saved.")

# --- Export & Import ---
st.subheader("Export / Import")
st.download_button(
    "Download All Wheels as JSON",
    export_assessments(st.session_state.saved_wheels),
    file_name="life_wheels.json",
    mime="application/json",
)
uploaded_file = st.file_uploader("Upload a Life Wheel JSON export", type=["json"])
if st.button("Import Wheels", disabled=uploaded_file is None):
    try:
        before_count = len(st.session_state.saved_wheels)
        merged = import_assessments(uploaded_file.getvalue(), st.session_state.saved_wheels)
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.session_state.saved_wheels = merged
        st.success(f"Imported {len(merged) - before_count} assessment(s). Existing assessments were preserved.")

# --- Comparison Chart ---
st.header("2. Compare Saved Wheels")
if len(st.session_state.saved_wheels) >= 2:
    selected_wheels = st.multiselect(
        "Choose up to 3 wheels to compare",
        options=list(st.session_state.saved_wheels.keys()),
        default=list(st.session_state.saved_wheels.keys())[:2],
        max_selections=3
    )

    if selected_wheels:
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

        for name in selected_wheels:
            values = st.session_state.saved_wheels[name] + [st.session_state.saved_wheels[name][0]]
            ax.plot(angles, values, label=name)
            ax.fill(angles, values, alpha=0.1)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=9)
        ax.set_ylim(0, 10)
        ax.set_yticklabels([])
        ax.set_title("Life Wheel Comparison", fontsize=14)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

        st.pyplot(fig)
        plt.close(fig)
else:
    st.info("You need at least two saved wheels to compare.")

# --- Show All Saved Wheels in Table ---
st.header("3. View All Saved Wheels")
if st.session_state.saved_wheels:
    st.dataframe(
        {name: vals for name, vals in st.session_state.saved_wheels.items()},
        use_container_width=True
    )
else:
    st.write("No wheels saved yet. Use the sliders above to create one.")
