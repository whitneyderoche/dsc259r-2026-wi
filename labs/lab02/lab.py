# lab.py


import os
import io
from pathlib import Path
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def trick_me():
    # Create DataFrame with duplicate column names
    tricky_1 = pd.DataFrame(
        [
            ["Alice", "A", 25],
            ["Bob", "B", 30],
            ["Carol", "C", 22],
            ["Dave", "D", 28],
            ["Eve", "E", 35]
        ],
        columns=["Name", "Name", "Age"]
    )

    # Save to CSV
    tricky_1.to_csv("tricky_1.csv", index=False)

    # Read back
    tricky_2 = pd.read_csv("tricky_1.csv")

    # Observation:
    # Column names change due to pandas auto-renaming duplicates
    
    return 3



def trick_bool():
    return [4, 4, 12]


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def population_stats(df):
    num_nonnull = df.notna().sum()
    prop_nonnull = num_nonnull / len(df)

    num_distinct = df.nunique(dropna=True)
    prop_distinct = num_distinct / num_nonnull

    return pd.DataFrame({
        'num_nonnull': num_nonnull,
        'prop_nonnull': prop_nonnull,
        'num_distinct': num_distinct,
        'prop_distinct': prop_distinct
    })


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def most_common(df, N):
    result = pd.DataFrame(index=range(N))

    for col in df.columns:
        vc = df[col].value_counts()

        # Take top N and drop the original value_counts index by using numpy arrays
        values = pd.Series(vc.index.to_numpy()).reindex(range(N))
        counts = pd.Series(vc.to_numpy()).reindex(range(N))

        result[f"{col}_values"] = values
        result[f"{col}_counts"] = counts

    return result



# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def super_hero_powers(powers):
    # Identify columns
    name_col = powers.columns[0]                  # e.g., 'hero_names'
    power_cols = powers.columns[powers.dtypes == bool]

    # 1) Superhero with the greatest number of superpowers
    power_counts = powers[power_cols].sum(axis=1)
    hero_most_powers = powers.loc[power_counts.idxmax(), name_col]

    # 2) Most common superpower among flyers, excluding 'Flight'
    flyers = powers[powers.get("Flight", False) == True]  # safe if 'Flight' missing
    flyer_power_cols = [c for c in power_cols if c != "Flight"]
    most_common_among_flyers = flyers[flyer_power_cols].sum().idxmax()

    # 3) Most common superpower among superheroes with only one superpower
    single_power_mask = power_counts == 1
    single_power_names = powers.loc[single_power_mask, power_cols].idxmax(axis=1)
    most_common_single_power = single_power_names.value_counts().idxmax()

    return [hero_most_powers, most_common_among_flyers, most_common_single_power]


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def clean_heroes(heroes):
    return heroes.replace(["-", -99.0], np.nan)


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def super_hero_stats():
    return ['Onslaught', 'George Lucas', 'bad', 'Marvel Comics', 'NBC - Heroes', 'Groot']


# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def clean_universities(df):
    df = df.copy()

    # Replace '\n' with ', ' in institution
    df["institution"] = df["institution"].str.replace("\n", ", ", regex=False)

    # broad_impact -> int
    df["broad_impact"] = df["broad_impact"].astype(int)

    # Split national_rank from the right into nation + rank
    nation_rank = df["national_rank"].astype(str).str.rsplit(" ", n=1, expand=True)
    df["nation"] = nation_rank[0].str.rstrip(",")              # <-- remove trailing comma
    df["national_rank_cleaned"] = nation_rank[1].astype(int)

    # Normalize the 3 country variants (shorter -> longer)
    country_map = {
        "Czechia": "Czech Republic",
        "UK": "United Kingdom",
        "USA": "United States",
    }
    df["nation"] = df["nation"].replace(country_map)

    # Drop original national_rank
    df = df.drop(columns=["national_rank"])

    # is_r1_public: Public AND R1 (control/city/state all non-null); NaNs -> False naturally
    is_r1 = df["control"].notna() & df["city"].notna() & df["state"].notna()
    df["is_r1_public"] = is_r1 & (df["control"] == "Public")

    return df

def university_info(cleaned):
    # 1) Among states with >= 3 institutions, lowest mean score
    state_counts = cleaned["state"].value_counts()
    eligible_states = state_counts[state_counts >= 3].index
    mean_scores = cleaned[cleaned["state"].isin(eligible_states)].groupby("state")["score"].mean()
    ans1 = mean_scores.idxmin()

    # 2) Proportion of world top-100 whose quality_of_faculty is also top-100
    top100 = cleaned[cleaned["world_rank"] <= 100]
    ans2 = float((top100["quality_of_faculty"] <= 100).mean())  # <-- cast to python float

    # 3) Number of states where >=50% are private (is_r1_public == False)
    by_state = cleaned.dropna(subset=["state"]).groupby("state")["is_r1_public"]
    private_prop = by_state.apply(lambda s: (~s).mean())
    ans3 = int((private_prop >= 0.5).sum())

    # 4) Worst world_rank among universities that are #1 in their nation
    best_in_nation = cleaned[cleaned["national_rank_cleaned"] == 1]
    ans4 = best_in_nation.loc[best_in_nation["world_rank"].idxmax(), "institution"]

    return [ans1, ans2, ans3, ans4]