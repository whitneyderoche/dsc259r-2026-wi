# lab.py


import os
import io
from pathlib import Path
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def read_linkedin_survey(dirname):
    
    target_cols = [
        "first name",
        "last name",
        "current company",
        "job title",
        "email",
        "university"
    ]

    d = Path(dirname)

    # If the directory doesn't exist, raise FileNotFoundError
    if not d.exists():
        raise FileNotFoundError(f"{dirname} does not exist")

    files = sorted(d.glob("survey*.csv"))

    # If there are no matching files, also raise FileNotFoundError
    if len(files) == 0:
        raise FileNotFoundError(f"No survey files found in {dirname}")

    dfs = []
    for fp in files:
        df = pd.read_csv(fp)

        df.columns = (
            df.columns
              .str.lower()
              .str.replace("_", " ", regex=False)
              .str.strip()
        )

        df = df.reindex(columns=target_cols)
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


def com_stats(df):
    titles = df["job title"]
    unis = df["university"]

    # 1) Proportion: among people whose university contains 'Ohio',
    #    proportion whose job title contains 'Programmer'
    ohio_mask = unis.fillna("").str.contains("Ohio", na=False)
    programmer_mask = titles.fillna("").str.contains("Programmer", na=False)

    ohio_total = int(ohio_mask.sum())
    if ohio_total == 0:
        prop_ohio_programmer = 0.0
    else:
        prop_ohio_programmer = (ohio_mask & programmer_mask).sum() / ohio_total

    # 2) UNIQUE job titles that end with exact string 'Engineer'
    num_unique_engineer_titles = (
        titles
        .dropna()
        .loc[titles.str.endswith("Engineer", na=False)]
        .nunique()
    )

    # 3) Job title with the longest name (no ties)
    #    Ignore missing job titles
    non_null_titles = titles.dropna()
    longest_title = non_null_titles.loc[non_null_titles.str.len().idxmax()]

    # 4) Number of people with 'manager' in job title, any case
    num_people_manager = titles.fillna("").str.contains("manager", case=False, na=False).sum()

    return [
        prop_ohio_programmer,
        int(num_unique_engineer_titles),
        longest_title,
        int(num_people_manager),
    ]



# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def read_student_surveys(dirname):
    d = Path(dirname)
    files = sorted(d.glob("favorite*.csv"))
    if len(files) == 0:
        raise FileNotFoundError(f"No favorite*.csv files found in {dirname}")

    def _find_id_col(cols):
        lowered = [c.lower().strip() for c in cols]
        for target in ["id", "student id", "student_id", "sid"]:
            if target in lowered:
                return cols[lowered.index(target)]
        return cols[0]

    # --- Read favorite1.csv (often includes name AND a response) ---
    f1 = d / "favorite1.csv"
    if not f1.exists():
        raise FileNotFoundError(f"Missing {f1}")

    base = pd.read_csv(f1)
    id_col = _find_id_col(base.columns)

    # find name column
    name_col = None
    for c in base.columns:
        if c.lower().strip() == "name":
            name_col = c
            break
    if name_col is None:
        non_id_cols = [c for c in base.columns if c != id_col]
        name_col = non_id_cols[0]

    # any remaining column besides id + name is the favorite1 response (if present)
    other_cols = [c for c in base.columns if c not in [id_col, name_col]]

    keep_cols = [id_col, name_col] + other_cols
    out = base[keep_cols].rename(columns={name_col: "name"}).set_index(id_col)
    out.index.name = "id"

    # If favorite1 has a response column, rename it to "favorite1"
    if len(other_cols) >= 1:
        # if there are multiple, keep the first (lab usually has exactly one)
        out = out.rename(columns={other_cols[0]: "favorite1"})

    # --- Read the rest as question columns ---
    for fp in files:
        if fp.name == "favorite1.csv":
            continue

        tmp = pd.read_csv(fp)
        tmp_id_col = _find_id_col(tmp.columns)
        non_id_cols = [c for c in tmp.columns if c != tmp_id_col]
        resp_col = non_id_cols[0]

        question_name = fp.stem  # "favorite2", "favorite3", ...
        tmp = tmp[[tmp_id_col, resp_col]].rename(columns={resp_col: question_name}).set_index(tmp_id_col)
        tmp.index.name = "id"

        out = out.join(tmp, how="left")

    # Ensure 1..1000 index
    out = out.reindex(range(1, 1001))
    return out


def check_credit(df):
    # survey question columns only
    question_cols = [c for c in df.columns if c != "name"]

    def is_valid_answer(colname, series):
        s = series.astype("string")
        valid = s.notna() & (s.str.strip() != "")

        # genres rule
        if colname == "favorite3":
            valid = valid & (s.str.strip() != "(no genres listed)")

        return valid

    # validity matrix
    valid_df = pd.DataFrame(
        {c: is_valid_answer(c, df[c]) for c in question_cols},
        index=df.index
    )

    # 5 points if student answered at least 50% of questions
    num_questions = len(question_cols)
    student_bonus = (valid_df.sum(axis=1) >= 0.5 * num_questions).astype(int) * 5

    # class-wide bonus: count questions >=90%, cap at 2
    class_bonus = min(2, (valid_df.mean(axis=0) >= 0.9).sum())

    ec = (student_bonus + class_bonus).astype(int)

    return pd.DataFrame(
        {"name": df["name"], "ec": ec},
        index=df.index
    )

# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def most_popular_procedure(pets, procedure_history):
    # keep only procedures for pets that exist in pets
    merged = procedure_history.merge(
        pets[["PetID"]],
        on="PetID",
        how="inner"
    )
    # most common ProcedureType
    return merged["ProcedureType"].value_counts().idxmax()


def pet_name_by_owner(owners, pets):
    # Pet names per OwnerID (list)
    pet_lists = pets.groupby("OwnerID")["Name"].apply(list)

    # Ensure every owner appears (owners with no pets -> empty list)
    pet_lists = pet_lists.reindex(owners["OwnerID"], fill_value=[])

    # Replace OwnerID index with owner first name (not unique is fine)
    owner_first = owners.set_index("OwnerID")["Name"]
    out = pet_lists.rename(index=owner_first)

    # Single pet -> string, multiple pets -> list
    out = out.apply(lambda xs: xs[0] if isinstance(xs, list) and len(xs) == 1 else xs)

    return out

def total_cost_per_city(owners, pets, procedure_history, procedure_detail):
    # Pet -> Owner -> City
    pet_city = pets.merge(
        owners[["OwnerID", "City"]],
        on="OwnerID",
        how="left"
    )[["PetID", "City"]]

    # Procedure history + City
    ph_city = procedure_history.merge(pet_city, on="PetID", how="left")

    # Add prices (merge on multiple columns)
    full = ph_city.merge(
        procedure_detail[["ProcedureType", "ProcedureSubCode", "Price"]],
        on=["ProcedureType", "ProcedureSubCode"],
        how="left"
    )

    # Sum by city, and include cities with zero spend
    city_totals = (
        full.groupby("City")["Price"].sum()
        .reindex(owners["City"].unique(), fill_value=0)
        .sort_index()
    )

    return city_totals


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def average_seller(sales):
    out = sales.pivot_table(
        index="Name",
        values="Total",
        aggfunc="mean"
    )
    out = out.rename(columns={"Total": "Average Sales"}).fillna(0)
    return out

def product_name(sales):
    return sales.pivot_table(
        index="Name",
        columns="Product",
        values="Total",
        aggfunc="sum"
    )

def count_product(sales):
    out = sales.pivot_table(
        index=["Product", "Name"],
        columns="Date",
        values="Total",
        aggfunc="count"
    )
    
    out = out.fillna(0)
    return out

def total_by_month(sales):
    # make a copy so we don't mutate the original df
    df = sales.copy()
    
    # extract month name from Date
    df["Month"] = pd.to_datetime(df["Date"]).dt.month_name()
    
    # pivot table
    out = df.pivot_table(
        index=["Name", "Product"],
        columns="Month",
        values="Total",
        aggfunc="sum"
    )
    
    # replace NaNs with 0
    out = out.fillna(0)
    
    return out