import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from wheel_data import CATEGORIES, export_assessments, import_assessments

categories = list(CATEGORIES)

if "saved_wheels" not in st.session_state:
    st.session_state.saved_wheels = {}


def render_radar_chart(wheels, title):
    """Render one or more named score arrays on a fixed 0–10 radar chart."""
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    for name, scores in wheels.items():
        values = scores + [scores[0]]
        ax.plot(angles, values, label=name)
        ax.fill(angles, values, alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylim(0, 10)
    ax.set_yticklabels([])
    ax.set_title(title, fontsize=14)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    st.pyplot(fig)
    plt.close(fig)


st.title("Life Wheel Web App")

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

st.subheader("Your Life Wheel")
st.caption("Live preview: adjust the sliders to see your wheel, then save it when you are ready.")
render_radar_chart(
    {wheel_name.strip() or "Current scores": scores},
    "Your Life Wheel",
)

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

st.header("2. Compare Saved Wheels")
if len(st.session_state.saved_wheels) >= 2:
    selected_wheels = st.multiselect(
        "Choose up to 3 wheels to compare",
        options=list(st.session_state.saved_wheels.keys()),
        default=list(st.session_state.saved_wheels.keys())[:2],
        max_selections=3,
    )
    if selected_wheels:
        render_radar_chart(
            {name: st.session_state.saved_wheels[name] for name in selected_wheels},
            "Life Wheel Comparison",
        )
else:
    st.info("Save at least two wheels to compare saved assessments.")

st.header("3. View All Saved Wheels")
if st.session_state.saved_wheels:
    st.dataframe(
        {name: vals for name, vals in st.session_state.saved_wheels.items()},
        use_container_width=True,
    )
else:
    st.write("No wheels saved yet. Use the sliders above to create one.")
