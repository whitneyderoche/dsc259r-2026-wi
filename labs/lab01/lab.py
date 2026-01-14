# lab.py


from pathlib import Path
import io
import pandas as pd
import numpy as np

np.set_printoptions(legacy="1.21")


# ---------------------------------------------------------------------
# QUESTION 0
# ---------------------------------------------------------------------


def consecutive_ints(ints):
    # iterate over indices 0..len(lst)-2
    for i in range(len(ints) - 1):
        # check if adjacent numbers differ by exactly 1
        if abs(ints[i] - ints[i+1]) == 1:
            return True
    return False


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def median_vs_mean(nums):
    nums_sorted = sorted(nums)
    n = len(nums_sorted)

    # Compute mean
    mean = sum(nums_sorted) / n

    # Compute median
    if n % 2 == 1:
        median = nums_sorted[n // 2]
    else:
        mid1 = nums_sorted[n // 2 - 1]
        mid2 = nums_sorted[n // 2]
        median = (mid1 + mid2) / 2

    return median <= mean


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def n_prefixes(s, n):
    prefixes = []
    for i in range(1, n + 1):
        prefixes.append(s[:i])
    prefixes.reverse()
    return "".join(prefixes)


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def exploded_numbers(ints, n):
    # Step 1: Build exploded lists for each number
    exploded_lists = []
    for x in ints:
        exploded = list(range(x - n, x + n + 1))
        exploded_lists.append(exploded)

    # Step 2: Find the maximum number of digits across all exploded numbers
    max_num = max(max(lst) for lst in exploded_lists)
    width = len(str(max_num))

    # Step 3: Convert each exploded list into a zero-padded string
    result = []
    for lst in exploded_lists:
        padded = [str(num).zfill(width) for num in lst]
        result.append(" ".join(padded))

    return result


# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def last_chars(fh):
    result = ""
    for line in fh:
        line = line.rstrip("\n")   # remove the newline
        if len(line) > 0:          # only add if there's at least one character
            result += line[-1]     # append the last character
    return result

# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def add_root(A):
    indices = np.arange(len(A))      # [0, 1, 2, ..., n-1]
    return A + np.sqrt(indices)

def where_square(A):
    roots = np.sqrt(A)
    return roots == roots.astype(int)


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def filter_cutoff_loop(matrix, cutoff):
    num_rows, num_cols = matrix.shape
    kept_cols = []   # we’ll store columns that pass the cutoff

    for j in range(num_cols):
        # compute mean of column j manually
        col_sum = 0.0
        for i in range(num_rows):
            col_sum += matrix[i, j]
        col_mean = col_sum / num_rows

        # keep this column if its mean is > cutoff
        if col_mean > cutoff:
            col_vals = [matrix[i, j] for i in range(num_rows)]
            kept_cols.append(col_vals)

    # if no columns pass, return an empty (rows × 0) array
    if not kept_cols:
        return np.empty((num_rows, 0), dtype=matrix.dtype)

    # kept_cols is list of columns → transpose to get rows × cols
    return np.array(kept_cols).T


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def filter_cutoff_np(matrix, cutoff):
    # column means along axis 0
    col_means = matrix.mean(axis=0)

    # boolean mask: True where mean > cutoff
    mask = col_means > cutoff

    # use mask to select columns
    return matrix[:, mask]


# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def growth_rates(A):
    # differences between consecutive days
    diffs = A[1:] - A[:-1]
    rates = diffs / A[:-1]
    # round to 2 decimal places
    return np.round(rates, 2)


def with_leftover(A):
     # leftover from each day's $20
    daily_leftover = 20 % A              # vectorized modulo
    cum_leftover = np.cumsum(daily_leftover)

    # days where leftover is enough to buy 1 share at that day's price
    good_days = np.where(cum_leftover >= A)[0]

    if good_days.size == 0:
        return -1
    else:
        return int(good_days[0])


# ---------------------------------------------------------------------
# QUESTION 8
# ---------------------------------------------------------------------


def salary_stats(Salary):
     # 1
    num_players = len(Salary)
    
    # 2
    num_teams = Salary['Team'].nunique()
    
    # 3
    total_salary = Salary['Salary'].sum()
    
    # 4
    highest_salary_name = Salary.loc[Salary['Salary'].idxmax(), 'Player']
    
    # 5
    avg_los = round(Salary[Salary['Team'].str.contains("Los Angeles Lakers")]['Salary'].mean(), 2)
    
    # 6
    fifth_row = Salary.sort_values('Salary').iloc[4]
    fifth_lowest = f"{fifth_row['Player']}, {fifth_row['Team']}"
    
    # 7 — detect duplicate last names ignoring suffixes
    cleaned = Salary['Player'].str.replace(r"\b(Jr\.?|II|III|IV|V)\b", "", regex=True).str.strip()
    last_names = cleaned.str.split().str[-1]
    duplicates = last_names.duplicated().any()
    
    # 8 — sum of salaries on team of highest-paid player
    highest_team = Salary.loc[Salary['Salary'].idxmax(), 'Team']
    total_highest = Salary[Salary['Team'] == highest_team]['Salary'].sum()
    
    # return Series in correct order
    return pd.Series({
        'num_players': num_players,
        'num_teams': num_teams,
        'total_salary': total_salary,
        'highest_salary': highest_salary_name,
        'avg_los': avg_los,
        'fifth_lowest': fifth_lowest,
        'duplicates': duplicates,
        'total_highest': total_highest
    })


# ---------------------------------------------------------------------
# QUESTION 9
# ---------------------------------------------------------------------


def parse_malformed(fp):
    rows = []

    with open(fp, "r") as fh:
        # Skip header line
        header = fh.readline()

        for line in fh:
            line = line.strip()
            if not line:
                continue  # skip any empty lines

            # Remove quotes to simplify parsing
            line = line.replace('"', '')

            # Split and strip whitespace
            raw_parts = [p.strip() for p in line.split(',')]

            # Remove empty tokens caused by extra commas
            parts = [p for p in raw_parts if p != '']

            # From the RIGHT:
            # last two pieces are lat, lon → geo
            lon = parts[-1]
            lat = parts[-2]
            geo = f"{lat},{lon}"

            # Next two to the left are height and weight
            height_raw = parts[-3]
            weight_raw = parts[-4]

            height = float(height_raw)
            weight = float(weight_raw)

            # Everything before those 4 tokens is name info
            name_parts = parts[:-4]

            # Expect at least first and last name
            if len(name_parts) >= 2:
                first = name_parts[0]
                # join anything after first into last (in case of extra commas)
                last = " ".join(name_parts[1:]).strip()
            else:
                # fallback; shouldn't really happen with this dataset
                first = name_parts[0] if name_parts else ""
                last = ""

            rows.append((first, last, weight, height, geo))

    df = pd.DataFrame(rows, columns=["first", "last", "weight", "height", "geo"])
    return df