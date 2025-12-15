import io
import pandas as pd


def calculate_fte(row):
    """
    FTE rules from slide:
    - Only staff with teaching load are counted
    - Full Time = 1
    - Part Time = 1 / 3
    """

    load = row.get("load", 0)

    # Exclude staff with no teaching load
    if pd.isna(load) or load <= 0:
        return 0

    contract = str(row["Contract Type"]).lower().strip()

    if "Full Time" in contract:
        return 1.0
    elif "Part Time" in contract:
        return round(1 / 3, 3)

    return 0


def compute_fte(staff_df: pd.DataFrame):
    staff_df["FTE"] = staff_df.apply(calculate_fte, axis=1)

    fte_summary = staff_df.groupby("FTE").size().reset_index(name="Headcount")

    fte_summary["Weighted_FTE"] = fte_summary["FTE"] * fte_summary["Headcount"]

    total_university_fte = fte_summary["Weighted_FTE"].sum()

    return staff_df, fte_summary, total_university_fte


def convert_df(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return output.getvalue()
