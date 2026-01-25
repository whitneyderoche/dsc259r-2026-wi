# project.py


import pandas as pd
import numpy as np
import re
from pathlib import Path
from collections import defaultdict 

import plotly.express as px


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def get_assignment_names(grades):
    """
    Return a dictionary mapping assignment categories to lists of
    assignment names extracted from the grades DataFrame.
    """

    # Initialize dictionary
    assignments = {
        "lab": [],
        "project": [],
        "midterm": [],
        "final": [],
        "disc": [],
        "checkpoint": []
    }

    for col in grades.columns:

        # Skip meta columns and non-assignment columns
        if "Max Points" in col or "Lateness" in col or "Total Lateness" in col:
            continue

        # ----- LABS -----
        # Exactly matches labXX
        if re.fullmatch(r"lab\d\d", col):
            assignments["lab"].append(col)
            continue

        # ----- DISCUSSION -----
        if re.fullmatch(r"discussion\d\d", col):
            assignments["disc"].append(col)
            continue

        # ----- CHECKPOINTS -----
        # e.g., project02_checkpoint01
        if "checkpoint" in col:
            assignments["checkpoint"].append(col)
            continue

        # ----- PROJECTS -----
        # projectXX or projectXX_free_response
        if col.startswith("project") and "checkpoint" not in col:
            assignments["project"].append(col)
            continue

        # ----- MIDTERM -----
        if col == "Midterm":
            assignments["midterm"].append(col)
            continue

        # ----- FINAL -----
        if col == "Final":
            assignments["final"].append(col)
            continue

    return assignments


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def projects_total(grades):
    """
    Return a Series with each student's total project grade for the quarter,
    as a number between 0 and 1.

    Each project counts equally, regardless of its raw point total.
    Projects with multiple components (e.g., autograded + free response)
    are combined before averaging across projects.
    """
    from collections import defaultdict

    assignment_names = get_assignment_names(grades)
    project_cols = assignment_names["project"]   # list of project-related columns

    # Group project components (e.g., project01 + project01_free_response)
    # into their base project (project01, project02, ...)
    project_groups = defaultdict(list)
    for name in project_cols:
        base = name.split("_")[0]   # "project02_free_response" -> "project02"
        project_groups[base].append(name)

    per_project_scores = []

    for base, components in project_groups.items():
        # Per-project totals for each student
        proj_earned = pd.Series(0.0, index=grades.index)
        proj_max = 0.0

        for col in components:
            # Points earned for this component (missing -> 0)
            earned = grades[col].fillna(0)

            # Corresponding max points column
            max_col = f"{col} - Max Points"
            if max_col not in grades.columns:
                continue

            max_points = grades[max_col].iloc[0]  # same for all students
            proj_earned += earned
            proj_max += max_points

        if proj_max == 0:
            continue

        # Per-project score in [0,1] for this base project
        per_project_scores.append(proj_earned / proj_max)

    if not per_project_scores:
        # No projects (shouldn't happen), but be safe
        return pd.Series(0.0, index=grades.index)

    # Each project counts equally: average project scores across all projects
    project_scores = pd.concat(per_project_scores, axis=1).mean(axis=1)

    return project_scores


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def lateness_penalty(col):
    """
    Given a Series of lateness values (e.g. 'lab01 - Lateness (H:M:S)'),
    return a Series of lateness multipliers: 1.0, 0.9, 0.7, or 0.4.

    Rules (per syllabus + 2-hour grace period):
      - <= 2 hours late: multiplier = 1.0
      - > 2 hours and <= 1 week late: multiplier = 0.9
      - > 1 week and <= 2 weeks late: multiplier = 0.7
      - > 2 weeks late: multiplier = 0.4
    """
    
    # Convert to timedelta; missing = 0 (on time)
    td = pd.to_timedelta(col.fillna("0:00:00"))

    # Time thresholds
    two_hours = pd.Timedelta(hours=2)
    one_week = pd.Timedelta(weeks=1)
    two_weeks = pd.Timedelta(weeks=2)

    # Start all multipliers at 1.0 (on time or within grace period)
    mult = pd.Series(1.0, index=col.index, dtype=float)

    # Apply penalties (later conditions override earlier ones)
    mult[td > two_hours] = 0.9
    mult[td > one_week] = 0.7
    mult[td > two_weeks] = 0.4

    return mult


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def process_labs(grades):
    """
    Return a DataFrame of processed lab scores.

    - Same index as `grades`
    - One column per lab: 'lab01', 'lab02', ..., 'lab09'
    - Values are final lab scores in [0, 1], adjusted for lateness
      (using lateness_penalty) and normalized by max points.
    """

    # Use Q1 helper to get all lab assignment names
    assignment_names = get_assignment_names(grades)
    lab_names = assignment_names["lab"]   # e.g. ['lab01', ..., 'lab09']

    # Set up the output DataFrame with same index as grades
    processed = pd.DataFrame(index=grades.index)

    for lab in lab_names:
        # Raw points; missing submissions -> 0
        raw = grades[lab].fillna(0)

        # Related columns
        max_col = f"{lab} - Max Points"
        late_col = f"{lab} - Lateness (H:M:S)"

        # Safety: skip if expected columns are missing
        if max_col not in grades.columns or late_col not in grades.columns:
            continue

        # Max points is the same for all students
        max_points = grades[max_col].iloc[0]

        # Guard against weird zero-max case
        if max_points == 0:
            processed[lab] = 0.0
            continue

        # Lateness multipliers from Q3
        multipliers = lateness_penalty(grades[late_col])

        # Normalized + lateness-adjusted score
        scores = (raw / max_points) * multipliers

        processed[lab] = scores

    return processed


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def lab_total(processed):
    """
    Given a DataFrame of processed lab scores (each value in [0, 1]),
    return a Series with each student's total lab grade after dropping
    their lowest lab and averaging the rest.
    """
    # Number of lab assignments (columns)
    n_labs = processed.shape[1]

    # If somehow there is only 1 lab, just return that column's values
    if n_labs <= 1:
        return processed.mean(axis=1)

    # Sum of all labs per student
    sums = processed.sum(axis=1)

    # Lowest lab per student
    mins = processed.min(axis=1)

    # Drop the lowest and average the rest
    totals = (sums - mins) / (n_labs - 1)

    return totals

# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def total_points(grades):
    """
    Return a Series with each student's total course grade as a proportion in [0, 1],
    using the syllabus weights:
      - Labs: 20%  (drop lowest lab, lateness penalties already applied)
      - Projects: 30%
      - Checkpoints: 2.5%
      - Discussions: 2.5%
      - Midterm: 15%
      - Final: 30%
    """

    # Helper from Q1
    assignment_names = get_assignment_names(grades)

    # ---------- Labs (20%) ----------
    processed_labs = process_labs(grades)        # Q4
    lab_scores = lab_total(processed_labs)       # Q5, already in [0, 1]

    # ---------- Projects (30%) ----------
    project_scores = projects_total(grades)      # Q2, already in [0, 1]

    # ---------- Generic helper for checkpoint / discussion / exams ----------
    def average_component(names):
        """
        Given a list of assignment base names (e.g. ['discussion01', 'discussion02']),
        return a Series of per-student averages of (score / max_points) across them.
        Each assignment is weighted equally, regardless of raw points.
        """
        cols = []

        for name in names:
            if name not in grades.columns:
                continue
            max_col = f"{name} - Max Points"
            if max_col not in grades.columns:
                continue

            raw = grades[name].fillna(0)
            max_points = grades[max_col].iloc[0]

            if max_points > 0:
                cols.append(raw / max_points)

        if not cols:  # no assignments of this type
            return pd.Series(0.0, index=grades.index)

        return pd.concat(cols, axis=1).mean(axis=1)

    # ---------- Checkpoints (2.5%) ----------
    checkpoint_scores = average_component(assignment_names["checkpoint"])

    # ---------- Discussions (2.5%) ----------
    discussion_scores = average_component(assignment_names["disc"])

    # ---------- Midterm (15%) ----------
    midterm_scores = average_component(assignment_names["midterm"])

    # ---------- Final (30%) ----------
    final_scores = average_component(assignment_names["final"])

    # ---------- Weighted total in [0, 1] ----------
    total = (
        0.20 * lab_scores +
        0.30 * project_scores +
        0.025 * checkpoint_scores +
        0.025 * discussion_scores +
        0.15 * midterm_scores +
        0.30 * final_scores
    )

    return total


# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def final_grades(total):
    """
    Given a Series of final course grades (values in [0,1]),
    return a Series of letter grades based on the cutoffs:
        A: grade >= 0.9
        B: 0.8 <= grade < 0.9
        C: 0.7 <= grade < 0.8
        D: 0.6 <= grade < 0.7
        F: grade < 0.6
    """
    letters = []

    for g in total:
        if g >= 0.9:
            letters.append("A")
        elif g >= 0.8:
            letters.append("B")
        elif g >= 0.7:
            letters.append("C")
        elif g >= 0.6:
            letters.append("D")
        else:
            letters.append("F")

    return pd.Series(letters, index=total.index)

def letter_proportions(total):
    """
    Given a Series of final numeric grades, return a Series containing the
    proportion of the class that received each letter grade.
    Index should be letters and values sorted in decreasing order.
    """
    # Convert numeric -> letter
    letters = final_grades(total)

    # Count each letter and convert to proportions
    proportions = letters.value_counts(normalize=True)

    # Sort descending
    proportions = proportions.sort_values(ascending=False)

    return proportions


# ---------------------------------------------------------------------
# QUESTION 8
# ---------------------------------------------------------------------


def raw_redemption(final_breakdown, question_numbers):
    """
    final_breakdown: DataFrame with:
        - column 0 = PID
        - column k = scores for question k

    question_numbers: list of integers indicating which question numbers
        (i.e., column positions) to include in redemption.

    Returns a DataFrame with columns:
        - 'PID'
        - 'Raw Redemption Score' (proportion in [0,1])
    """
    # Select the question score columns by column position
    q_df = final_breakdown.iloc[:, question_numbers].copy()

    # Students who did not take the final → NaN → 0 earned
    q_df = q_df.fillna(0)

    # Assume someone got full credit on each question
    max_per_question = q_df.max(axis=0)
    total_max = max_per_question.sum()

    # Total earned points per student
    earned = q_df.sum(axis=1)

    raw_scores = earned / total_max

    return pd.DataFrame({
        "PID": final_breakdown["PID"],
        "Raw Redemption Score": raw_scores
    })
    
def combine_grades(grades, raw_redemption_scores):
    """
    grades: main grades DataFrame (must include 'PID')
    raw_redemption_scores: DataFrame returned by raw_redemption, with:
        - 'PID'
        - 'Raw Redemption Score'

    Returns a new DataFrame with all original grade columns plus:
        - 'Raw Redemption Score'
    """
    out = grades.copy()

    # Align redemption scores by PID
    redemption_map = raw_redemption_scores.set_index("PID")["Raw Redemption Score"]

    # Add column; students without redemption get 0
    out["Raw Redemption Score"] = out["PID"].map(redemption_map).fillna(0)

    return out


# ---------------------------------------------------------------------
# QUESTION 9
# ---------------------------------------------------------------------


def z_score(ser):
    """
    Convert a Series to z-scores using:
        z = (x - mean) / sd
    with ddof=0 (population SD).

    Do NOT fill NaNs; NaNs should remain NaN in the output.
    """
    mean = ser.mean(skipna=True)
    sd = ser.std(ddof=0, skipna=True)
    return (ser - mean) / sd
    
def add_post_redemption(grades_combined):
    
    df = grades_combined.copy()

    # Midterm proportion (fill NaN midterm as 0 BEFORE computing z-scores)
    midterm_raw = df["Midterm"].fillna(0)
    midterm_max = df["Midterm - Max Points"].iloc[0]
    midterm_pre = midterm_raw / midterm_max

    # Redemption raw score already a proportion; should have no NaNs
    redemption_raw = df["Raw Redemption Score"]

    # Z-scores
    midterm_z = z_score(midterm_pre)
    redemption_z = z_score(redemption_raw)

    # Convert redemption z-score back to a midterm proportion using midterm mean/SD
    midterm_mean = midterm_pre.mean()
    midterm_sd = midterm_pre.std(ddof=0)

    midterm_post = midterm_pre.copy()
    improve = redemption_z > midterm_z
    midterm_post.loc[improve] = redemption_z.loc[improve] * midterm_sd + midterm_mean

    # Cap at 1.0 (100%)
    midterm_post = midterm_post.clip(upper=1)

    # Add columns
    df["Midterm Score Pre-Redemption"] = midterm_pre
    df["Midterm Score Post-Redemption"] = midterm_post

    return df


# ---------------------------------------------------------------------
# QUESTION 10
# ---------------------------------------------------------------------


def total_points_post_redemption(grades_combined):
    
    df = add_post_redemption(grades_combined)

    assignment_names = get_assignment_names(df)

    # Labs (20%)
    lab_scores = lab_total(process_labs(df))

    # Projects (30%)
    project_scores = projects_total(df)

    # Helper: equal-weight average of (score / max) across a set of assignments
    def avg_component(names):
        cols = []
        for name in names:
            max_col = f"{name} - Max Points"
            if name in df.columns and max_col in df.columns:
                raw = df[name].fillna(0)
                max_points = df[max_col].iloc[0]
                if max_points > 0:
                    cols.append(raw / max_points)

        if not cols:
            return pd.Series(0.0, index=df.index)

        return pd.concat(cols, axis=1).mean(axis=1)

    # Checkpoints (2.5%)
    checkpoint_scores = avg_component(assignment_names["checkpoint"])

    # Discussions (2.5%)
    discussion_scores = avg_component(assignment_names["disc"])

    # Final (30%)
    final_scores = avg_component(assignment_names["final"])

    # Midterm post-redemption (15%)
    midterm_post = df["Midterm Score Post-Redemption"]

    total = (
        0.20 * lab_scores +
        0.30 * project_scores +
        0.025 * checkpoint_scores +
        0.025 * discussion_scores +
        0.15 * midterm_post +
        0.30 * final_scores
    )

    # Make sure dtype is float (autograder checks this)
    return total.astype(float)


    
def proportion_improved(grades_combined):

    pre_total = total_points(grades_combined)
    post_total = total_points_post_redemption(grades_combined)

    pre_letters = final_grades(pre_total)
    post_letters = final_grades(post_total)

    # Since grades cannot decrease with redemption, a change implies an increase
    return float((post_letters != pre_letters).mean())

# ---------------------------------------------------------------------
# QUESTION 11
# ---------------------------------------------------------------------


def section_most_improved(grades_analysis):
    
    improved = grades_analysis["Letter Grade Post-Redemption"] != grades_analysis["Letter Grade Pre-Redemption"]

    # Proportion improved within each section
    props = improved.groupby(grades_analysis["Section"]).mean()

    # Section with max proportion
    return props.idxmax()
    
def top_sections(grades_analysis, t, n):
    
    meets = grades_analysis["Raw Redemption Score"] >= t

    counts = meets.groupby(grades_analysis["Section"]).sum()

    sections = counts[counts >= n].index.to_numpy()

    return np.sort(sections)


# ---------------------------------------------------------------------
# QUESTION 12
# ---------------------------------------------------------------------


def rank_by_section(grades_analysis):
    
    df = grades_analysis[["PID", "Section", "Total Points Post-Redemption"]].copy()

    # Sort within each section by total points (descending); tie-break by PID for determinism
    df = df.sort_values(
        ["Section", "Total Points Post-Redemption", "PID"],
        ascending=[True, False, True]
    )

    # Assign ranks 1..k within each section
    df["Section Rank"] = df.groupby("Section").cumcount() + 1

    # Pivot to wide format: rows = rank, columns = section, values = PID
    wide = df.pivot(index="Section Rank", columns="Section", values="PID")

    # Determine n = size of largest section
    n = df.groupby("Section").size().max()

    # Ensure full row index 1..n
    wide = wide.reindex(range(1, n + 1))

    # Ensure columns A01..A30 in order (even if some sections don't exist)
    section_cols = [f"A{i:02d}" for i in range(1, 31)]
    wide = wide.reindex(columns=section_cols)

    # Fill missing with empty strings
    wide = wide.fillna("")

    return wide


# ---------------------------------------------------------------------
# QUESTION 13
# ---------------------------------------------------------------------


def letter_grade_heat_map(grades_analysis):
    
    grade_order = ["A", "B", "C", "D", "F"]
    section_order = [f"A{i:02d}" for i in range(1, 31)]

    # Count letter grades within each section
    counts = pd.crosstab(
        grades_analysis["Letter Grade Post-Redemption"],
        grades_analysis["Section"]
    )

    # Ensure full set/order of rows + columns, fill missing with 0
    counts = counts.reindex(index=grade_order, columns=section_order, fill_value=0)

    # Convert counts -> proportions within each section (column-normalize)
    props = counts.div(counts.sum(axis=0), axis=1).fillna(0)

    # Heatmap
    fig = px.imshow(
        props,
        x=section_order,
        y=grade_order,
        color_continuous_scale="Blues",  
        aspect="auto",
        title="Distribution of Letter Grades by Section"
    )

 
    fig.update_layout(font=dict(size=14))

    return fig