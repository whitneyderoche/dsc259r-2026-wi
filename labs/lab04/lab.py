# lab.py


import pandas as pd
import numpy as np
import io
from pathlib import Path
import os


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def prime_time_logins(login):
    # Parse timestamps
    t = pd.to_datetime(login["Time"], errors="coerce")

    # Prime time: 16:00 (inclusive) to 20:00 (exclusive)
    is_prime = (t.dt.hour >= 16) & (t.dt.hour < 20)

    # Count prime-time logins per user
    out = is_prime.groupby(login["Login Id"]).sum().to_frame("Time")
    out["Time"] = out["Time"].astype(int)
    out.index.name = "Login Id"

    return out


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------


def count_frequency(login):
    # Fixed "current time"
    now = pd.Timestamp("2024-01-31 23:59:00")

    # Ensure Time is datetime
    t = pd.to_datetime(login["Time"], errors="coerce")

    # Aggregate per user: total logins + first login time
    agg = (
        login.assign(Time=t)
             .groupby("Login Id")
             .agg(
                 total_logins=("Time", "count"),
                 first_login=("Time", "min")
             )
    )

    # Compute full days since first login
    days = (now - agg["first_login"]).dt.days

    # Logins per day
    frequency = agg["total_logins"] / days

    frequency.name = None  # match typical otter expectations
    return frequency


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def cookies_null_hypothesis():
    return [1, 2]

                         
def cookies_p_value(N):
    n_cookies = 250
    p_burnt = 0.04
    observed = 15
    
    sims = np.random.binomial(n=n_cookies, p=p_burnt, size=N)
    return np.mean(sims >= observed)



# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def car_null_hypothesis():
    return [1, 4]

def car_alt_hypothesis():
    return [2, 6]

def car_test_statistic():
    return [1, 4]

def car_p_value():
    return 4


# ---------------------------------------------------------------------
# QUESTION 5
# ---------------------------------------------------------------------


def superheroes_test_statistic():
    return [1, 2]

def bhbe_col(heroes):
    # Boolean Series: True if hair contains 'blond' and eyes contain 'blue' (case-insensitive)
    hair = heroes["Hair color"].astype(str).str.contains("blond", case=False, na=False)
    eyes = heroes["Eye color"].astype(str).str.contains("blue", case=False, na=False)
    return (hair & eyes).astype(bool)

def superheroes_observed_statistic(heroes):
    bhbe = bhbe_col(heroes)
    is_good = heroes["Alignment"].astype(str).str.lower().eq("good")
    # proportion of good among BHBE
    return is_good[bhbe].mean()
    
def simulate_bhbe_null(heroes, N):
    bhbe = bhbe_col(heroes)
    m = int(bhbe.sum())  # number of BHBE characters

    is_good = heroes["Alignment"].astype(str).str.lower().eq("good")
    p = is_good.mean()   # overall proportion good

    # simulate good counts in BHBE group under null, then convert to proportions
    sims = np.random.binomial(n=m, p=p, size=N)
    return sims / m

def superheroes_p_value(heroes):
    obs = superheroes_observed_statistic(heroes)
    sims = simulate_bhbe_null(heroes, 100_000)

    # One-sided: "greater" (BHBE good proportion is higher)
    pval = np.mean(sims >= obs)
    decision = "Reject" if pval < 0.01 else "Fail to reject"
    return [pval, decision]


# ---------------------------------------------------------------------
# QUESTION 6
# ---------------------------------------------------------------------


def diff_of_means(data, col='orange'):
    york_mean = data.loc[data["Factory"] == "Yorkville", col].mean()
    waco_mean = data.loc[data["Factory"] == "Waco", col].mean()
    return abs(york_mean - waco_mean)


def simulate_null(data, col='orange'):
    shuffled = data.copy()
    shuffled["Factory"] = np.random.permutation(shuffled["Factory"].values)
    return diff_of_means(shuffled, col)


def color_p_value(data, col='orange'):
    observed = diff_of_means(data, col)

    sims = np.array([simulate_null(data, col) for _ in range(1000)])
    p_value = np.mean(sims >= observed)

    return float(p_value)


# ---------------------------------------------------------------------
# QUESTION 7
# ---------------------------------------------------------------------


def ordered_colors():
    return [
        ('yellow', 0.000),
        ('orange', 0.051),
        ('red', 0.221),
        ('green', 0.470),
        ('purple', 0.972)
    ]


# ---------------------------------------------------------------------
# QUESTION 8
# ---------------------------------------------------------------------


    
def same_color_distribution():
    return (0.003, "Reject")


# ---------------------------------------------------------------------
# QUESTION 9
# ---------------------------------------------------------------------


def perm_vs_hyp():
    return ['P', 'P', 'H', 'H', 'P']
