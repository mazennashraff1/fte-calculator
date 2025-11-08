import pandas as pd


def calculate_fte_ratio(row):
    job = str(row["JOB_TITLE_CODE"]).strip().lower()
    if "teaching assistant" in job:
        return 0.5
    max_load = row.get("MAX_LOAD", 0)
    if pd.isna(max_load) or max_load == 0:
        return 0
    return round(row["CURRENT_LOAD"] / max_load, 2)


def compute_fte(load_standard: pd.DataFrame, staff_loads: pd.DataFrame):
    merged = pd.merge(
        staff_loads,
        load_standard,
        on=["FACULTYID", "JOB_TITLE_CODE"],
        how="left",
    )
    merged["FTE_Ratio"] = merged.apply(calculate_fte_ratio, axis=1)

    fte_groups = merged.groupby("FTE_Ratio").size().reset_index(name="Headcount")
    fte_groups["Weighted_FTE"] = fte_groups["Headcount"] * fte_groups["FTE_Ratio"]
    total_university_fte = fte_groups["Weighted_FTE"].sum()

    return merged, fte_groups, total_university_fte
