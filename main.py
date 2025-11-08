import pandas as pd
from PIL import Image
import streamlit as st
from fte_logic import compute_fte

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
    st.image(logo, width=80)  # small logo at left

with col2:
    st.markdown(
        "<h1 style='text-align:center'>MSA University FTE Calculator</h1>",
        unsafe_allow_html=True,
    )

with col3:
    st.write("")  # empty to center title

# --- Top-level tabs for pages ---
tab_home, tab_templates = st.tabs(["🏠 Home", "📄 Excel Templates"])

# --- Home Tab ---
with tab_home:
    st.subheader("Upload Excel Files")
    load_standard_file = st.file_uploader(
        "Upload Standard Load for the University", type=["xlsx"]
    )
    staff_loads_file = st.file_uploader("Upload Current Staff Load", type=["xlsx"])

    if load_standard_file and staff_loads_file:
        load_standard = pd.read_excel(load_standard_file)
        staff_loads = pd.read_excel(staff_loads_file)

        if st.button("📊 Calculate FTE"):
            merged, fte_groups, total_university_fte = compute_fte(
                load_standard, staff_loads
            )

            st.session_state["merged"] = merged
            st.session_state["fte_groups"] = fte_groups
            st.session_state["total_fte"] = total_university_fte
            st.success("✅ Calculation completed!")

    # --- Sub-tabs for FTE results ---
    if "fte_groups" in st.session_state:
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(
            ["FTE Summary", "Individual Staff FTE", "Staff-to-Student Ratio"]
        )

        with sub_tab1:
            st.subheader("📊 FTE Group Summary")
            st.dataframe(
                st.session_state["fte_groups"].sort_values(by="FTE_Ratio"),
                use_container_width=True,
            )
            st.metric("✅ Total University FTE", f"{st.session_state['total_fte']:.2f}")

            def convert_df(df):
                import io

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name="Sheet1")
                return output.getvalue()

            fte_groups_excel = convert_df(st.session_state["fte_groups"])
            st.download_button(
                "📥 Download FTE Summary (Grouped)",
                data=fte_groups_excel,
                file_name="fte_summary_qs.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with sub_tab2:
            st.subheader("👥 Individual Staff FTE Details")
            st.dataframe(st.session_state["merged"], use_container_width=True)

            merged_excel = convert_df(st.session_state["merged"])
            st.download_button(
                "📥 Download Individual Staff FTE",
                data=merged_excel,
                file_name="fte_individuals_qs.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with sub_tab3:
            st.subheader("📏 Staff-to-Student Ratio")
            student_number = st.number_input(
                "Enter total number of students:",
                min_value=1,
                step=1,
                key="student_number",
            )
            fte_per_student = st.session_state["total_fte"] / student_number
            st.metric("FTE per Student", f"{fte_per_student:.4f}")
            st.info("This shows the average FTE per student across the university.")

# --- Excel Templates Tab ---
with tab_templates:
    st.subheader("Excel File Column Reference Samples")

    st.markdown("### 1️⃣ Standard Load Excel (load_standard.xlsx)")
    st.write(
        pd.DataFrame(
            columns=["FACULTYID", "JOB_TITLE_CODE", "MAX_LOAD"],
            data=[["SampleFaculty", "Prof", 12]],
        )
    )
    st.info("Required columns: FACULTYID, JOB_TITLE_CODE, MAX_LOAD")

    st.markdown("### 2️⃣ Current Staff Load Excel (staff_loads.xlsx)")
    st.write(
        pd.DataFrame(
            columns=["FACULTYID", "JOB_TITLE_CODE", "CURRENT_LOAD", "StaffName"],
            data=[["SampleFaculty", "Prof", 10, "John Doe"]],
        )
    )
    st.info(
        "Required columns: FACULTYID, JOB_TITLE_CODE, CURRENT_LOAD (StaffName optional)"
    )
