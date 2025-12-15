import pandas as pd
from PIL import Image
import streamlit as st
from fte_logic import compute_fte, convert_df

# --- Page config ---
st.set_page_config(
    page_title="MSA University FTE Calculator",
    layout="wide",
    page_icon="MSA_Logo.png",
)

# --- Logo and centered title ---
logo = Image.open("MSA_Logo.png")

col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    st.image(logo, width=80)

with col2:
    st.markdown(
        "<h1 style='text-align:center'>MSA University FTE Calculator</h1>",
        unsafe_allow_html=True,
    )

with col3:
    st.write("")

# --- Top-level tabs ---
tab_home, tab_templates = st.tabs(["🏠 Home", "📄 Excel Templates"])

# --- Home Tab ---
with tab_home:
    st.subheader("Upload Staff Load Excel File")

    staff_file = st.file_uploader("Upload Staff Load File (.xlsx)", type=["xlsx"])

    if staff_file:
        staff_df = pd.read_excel(staff_file)
        st.success("✅ File uploaded successfully")

        if st.button("📊 Calculate FTE"):
            staff_with_fte, fte_summary, total_university_fte = compute_fte(staff_df)

            st.session_state["staff_with_fte"] = staff_with_fte
            st.session_state["fte_summary"] = fte_summary
            st.session_state["total_fte"] = total_university_fte
            st.success("✅ FTE calculation completed!")

    # --- Results Tabs ---
    if "fte_summary" in st.session_state:
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(
            ["FTE Summary", "Individual Staff FTE", "Faculty-to-Student Ratio"]
        )

        with sub_tab1:
            st.subheader("📊 FTE Summary")
            st.dataframe(
                st.session_state["fte_summary"].sort_values(by="FTE"),
                use_container_width=True,
            )
            st.metric(
                "✅ Total University FTE",
                f"{st.session_state['total_fte']:.2f}",
            )

            fte_summary_excel = convert_df(st.session_state["fte_summary"])
            st.download_button(
                "📥 Download FTE Summary",
                data=fte_summary_excel,
                file_name="fte_summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with sub_tab2:
            st.subheader("👥 Individual Staff FTE")
            st.dataframe(
                st.session_state["staff_with_fte"],
                use_container_width=True,
            )

            staff_excel = convert_df(st.session_state["staff_with_fte"])
            st.download_button(
                "📥 Download Individual Staff FTE",
                data=staff_excel,
                file_name="fte_individual_staff.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with sub_tab3:
            st.subheader("📏 Faculty-to-Student Ratio")

            student_number = st.number_input(
                "Enter total number of students:",
                min_value=1,
                step=1,
            )

            ratio = st.session_state["total_fte"] / student_number
            st.metric("Faculty-to-Student Ratio", f"{ratio:.4f}")

            st.info("Ratio is calculated as: FTE University / Total Students")

# --- Excel Templates Tab ---
with tab_templates:
    st.subheader("Excel Template Reference")

    st.markdown("### Required Excel Columns")
    st.write(
        pd.DataFrame(
            columns=[
                "UniID",
                "Name",
                "Faculty",
                "Contract Type",
                "Edu Degree",
                "load",
                "Job Title",
                "Max Load",
                "Load Difference",
            ],
            data=[
                [
                    "MSA",
                    "John Doe",
                    "Engineering",
                    "Full Time",
                    "PhD",
                    9,
                    "Teaching Assistant",
                    12,
                    -3,
                ]
            ],
        )
    )

    st.info(
        "Only the following columns are required for calculation:\n\n"
        "- Contract Type\n"
        "- load\n\n"
        "All other columns are optional and kept for reporting."
    )
