
# ============================================================
# CERTIFICATION TESTING DATA ANALYSIS PROGRAM
# ============================================================
#
# This program:
#
# 1. Imports certification testing data from a CSV file.
# 2. Stores the data in an SQLite database.
# 3. Cleans and standardizes the data.
# 4. Performs descriptive statistical analysis.
# 5. Performs statistical significance testing.
# 6. Examines testing time and distance from semester end.
# 7. Calculates correlations.
# 8. Calculates effect sizes where appropriate.
# 9. Identifies small sample sizes.
# 10. Creates a full TXT statistical report.
# 11. Creates an AI-ready analysis prompt in the terminal.
#
# IMPORTANT:
#
# Correlation does NOT prove causation.
#
# Statistical significance does NOT prove practical importance.
#
# Small sample sizes should be interpreted cautiously.
#
# Professor-level results are descriptive/record-keeping
# information only and should NOT be interpreted as measures
# of instructor effectiveness.
#
# ============================================================


import os
import sqlite3
from datetime import datetime

import pandas as pd

from scipy.stats import (
    fisher_exact,
    chi2_contingency,
    mannwhitneyu,
    kruskal,
    pearsonr
)


# ============================================================
# SETTINGS
# ============================================================

CSV_FILE = "data/2026_summerTesting.csv"

DATABASE_FILE = "database/analysis.db"

REPORT_FOLDER = "reports"


# ============================================================
# CREATE REQUIRED FOLDERS
# ============================================================

os.makedirs(
    "database",
    exist_ok=True
)

os.makedirs(
    REPORT_FOLDER,
    exist_ok=True
)


# ============================================================
# READ CSV FILE
# ============================================================

try:

    df = pd.read_csv(
        CSV_FILE
    )

except FileNotFoundError:

    print(
        "\nERROR: CSV file could not be found."
    )

    print(
        f"Expected file: {CSV_FILE}"
    )

    print(
        "\nMake sure your CSV is inside the data folder."
    )

    exit()


# ============================================================
# REMOVE EMPTY RECORDS
# ============================================================

df = df.dropna(
    subset=["Course Number"]
)


# ============================================================
# CONNECT TO SQLITE DATABASE
# ============================================================

connection = sqlite3.connect(
    DATABASE_FILE
)


# ============================================================
# SAVE CSV DATA INTO DATABASE
# ============================================================

df.to_sql(
    "results",
    connection,
    if_exists="replace",
    index=False
)


# ============================================================
# READ DATA FROM DATABASE
# ============================================================

query = """
SELECT *
FROM results
"""

database_df = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# CLEAN RESULT COLUMN
# ============================================================

database_df["Result"] = (
    database_df["Result"]
    .astype(str)
    .str.strip()
    .str.title()
)


# ============================================================
# CLEAN TEST NAMES
# ============================================================

database_df["Test"] = (
    database_df["Test"]
    .astype(str)
    .str.strip()
)


database_df["Test"] = (
    database_df["Test"]
    .replace(
        "Network +",
        "Network+"
    )
)


# ============================================================
# CLEAN NO-SHOW COLUMN
# ============================================================

database_df["No Show"] = (
    database_df["No Show"]
    .astype(str)
    .str.strip()
    .str.upper()
    .map(
        {
            "TRUE": 1,
            "FALSE": 0,
            "1": 1,
            "0": 0
        }
    )
)


database_df["No Show"] = (
    database_df["No Show"]
    .fillna(0)
)


# ============================================================
# CLEAN DATE COLUMNS
# ============================================================

database_df["Test Date"] = pd.to_datetime(
    database_df["Test Date"],
    format="mixed",
    errors="coerce"
)


database_df["Semester End Date"] = pd.to_datetime(
    database_df["Semester End Date"],
    format="mixed",
    errors="coerce"
)


# ============================================================
# CLEAN TIME
# ============================================================

database_df["Time"] = (
    database_df["Time"]
    .astype(str)
    .str.strip()
    .str.lower()
)


# ============================================================
# CONVERT TIME TO HOUR
# ============================================================

def convert_time_to_hour(time_value):

    try:

        parsed_time = pd.to_datetime(
            time_value
        )

        return parsed_time.hour

    except:

        return None


database_df["Testing Hour"] = (
    database_df["Time"]
    .apply(
        convert_time_to_hour
    )
)


# ============================================================
# CALCULATE DAYS FROM SEMESTER END
# ============================================================

database_df[
    "Days From Semester End"
] = (
    database_df["Test Date"]
    -
    database_df["Semester End Date"]
).dt.days


# ============================================================
# SCORE RELATIVE TO PASSING
# ============================================================

database_df[
    "Score Percent of Passing"
] = (
    database_df["Score"]
    /
    database_df["Passing Score"]
    *
    100
)


# ============================================================
# POINTS ABOVE / BELOW PASSING
# ============================================================

database_df[
    "Points From Passing"
] = (
    database_df["Score"]
    -
    database_df["Passing Score"]
)


# ============================================================
# CREATE DATASETS
# ============================================================

total_tests = len(
    database_df
)


no_show_tests = database_df[
    database_df["No Show"] == 1
].copy()


completed_df = database_df[
    database_df["No Show"] == 0
].copy()


# ============================================================
# BASIC COUNTS
# ============================================================

no_show_count = len(
    no_show_tests
)


completed_count = len(
    completed_df
)


passed_tests = completed_df[
    completed_df["Result"] == "Pass"
]


failed_tests = completed_df[
    completed_df["Result"] == "Fail"
]


passed_count = len(
    passed_tests
)


failed_count = len(
    failed_tests
)


# ============================================================
# OVERALL RATES
# ============================================================

if completed_count > 0:

    pass_rate = (
        passed_count
        /
        completed_count
        *
        100
    )

    failure_rate = (
        failed_count
        /
        completed_count
        *
        100
    )

else:

    pass_rate = 0

    failure_rate = 0


if total_tests > 0:

    no_show_rate = (
        no_show_count
        /
        total_tests
        *
        100
    )

else:

    no_show_rate = 0


# ============================================================
# REPORT BUILDER
# ============================================================

report = ""


def add_section(title):

    global report

    report += "\n"

    report += "=" * 60

    report += "\n"

    report += title.center(60)

    report += "\n"

    report += "=" * 60

    report += "\n"


def add_text(text=""):

    global report

    report += str(text)

    report += "\n"


# ============================================================
# HEADER
# ============================================================

generated_date = datetime.now().strftime(
    "%B %d, %Y at %I:%M %p"
)


add_section(
    "CERTIFICATION TESTING DATA ANALYSIS"
)


add_text(
    f"Report Generated: {generated_date}"
)


add_text(
    f"Source File: {CSV_FILE}"
)


# ============================================================
# OVERALL RESULTS
# ============================================================

add_section(
    "OVERALL RESULTS"
)


add_text(
    f"Total Scheduled Tests: {total_tests}"
)

add_text(
    f"Completed Tests: {completed_count}"
)

add_text(
    f"No Shows: {no_show_count}"
)

add_text(
    f"Passed: {passed_count}"
)

add_text(
    f"Failed: {failed_count}"
)

add_text()

add_text(
    f"Pass Rate: {pass_rate:.2f}%"
)

add_text(
    f"Failure Rate: {failure_rate:.2f}%"
)

add_text(
    f"No-Show Rate: {no_show_rate:.2f}%"
)


# ============================================================
# RESULTS BY COURSE
# ============================================================

course_results = pd.crosstab(
    completed_df["Course Number"],
    completed_df["Result"]
)


if "Pass" not in course_results.columns:

    course_results["Pass"] = 0


if "Fail" not in course_results.columns:

    course_results["Fail"] = 0


course_results["Completed"] = (
    course_results["Pass"]
    +
    course_results["Fail"]
)


course_results["Pass Rate"] = (
    course_results["Pass"]
    /
    course_results["Completed"]
    *
    100
).round(2)


add_section(
    "RESULTS BY COURSE"
)


add_text(
    course_results.to_string()
)


# ============================================================
# RESULTS BY PROFESSOR
# ============================================================

professor_results = pd.crosstab(
    completed_df["Professor"],
    completed_df["Result"]
)


if "Pass" not in professor_results.columns:

    professor_results["Pass"] = 0


if "Fail" not in professor_results.columns:

    professor_results["Fail"] = 0


professor_results["Completed"] = (
    professor_results["Pass"]
    +
    professor_results["Fail"]
)


professor_results["Pass Rate"] = (
    professor_results["Pass"]
    /
    professor_results["Completed"]
    *
    100
).round(2)


add_section(
    "RESULTS BY PROFESSOR"
)


add_text(
    "DESCRIPTIVE / RECORD-KEEPING INFORMATION ONLY"
)


add_text(
    "Professor results should NOT be interpreted "
    "as instructor effectiveness."
)


add_text()


add_text(
    professor_results.to_string()
)


# ============================================================
# RESULTS BY CERTIFICATION TEST
# ============================================================

test_results = pd.crosstab(
    completed_df["Test"],
    completed_df["Result"]
)


if "Pass" not in test_results.columns:

    test_results["Pass"] = 0


if "Fail" not in test_results.columns:

    test_results["Fail"] = 0


test_results["Completed"] = (
    test_results["Pass"]
    +
    test_results["Fail"]
)


test_results["Pass Rate"] = (
    test_results["Pass"]
    /
    test_results["Completed"]
    *
    100
).round(2)


add_section(
    "RESULTS BY CERTIFICATION TEST"
)


add_text(
    test_results.to_string()
)


# ============================================================
# RESULTS BY SECTION
# ============================================================

section_results = pd.crosstab(
    completed_df["Section Number"],
    completed_df["Result"]
)


if "Pass" not in section_results.columns:

    section_results["Pass"] = 0


if "Fail" not in section_results.columns:

    section_results["Fail"] = 0


section_results["Completed"] = (
    section_results["Pass"]
    +
    section_results["Fail"]
)


section_results["Pass Rate"] = (
    section_results["Pass"]
    /
    section_results["Completed"]
    *
    100
).round(2)


add_section(
    "RESULTS BY SECTION"
)


add_text(
    section_results.to_string()
)


# ============================================================
# NO-SHOW RATE BY COURSE
# ============================================================

course_total = (
    database_df
    .groupby("Course Number")
    .size()
)


course_no_shows = (
    no_show_tests
    .groupby("Course Number")
    .size()
)


no_show_course_analysis = pd.DataFrame(
    {
        "Scheduled": course_total,
        "No Shows": course_no_shows
    }
).fillna(0)


no_show_course_analysis[
    "No Show Rate"
] = (
    no_show_course_analysis["No Shows"]
    /
    no_show_course_analysis["Scheduled"]
    *
    100
).round(2)


add_section(
    "NO-SHOW RATE BY COURSE"
)


add_text(
    no_show_course_analysis
    .sort_values(
        "No Show Rate",
        ascending=False
    )
    .to_string()
)


# ============================================================
# TESTING TIME ANALYSIS
# ============================================================

time_completed = pd.crosstab(
    completed_df["Time"],
    completed_df["Result"]
)


if "Pass" not in time_completed.columns:

    time_completed["Pass"] = 0


if "Fail" not in time_completed.columns:

    time_completed["Fail"] = 0


time_scheduled = (
    database_df
    .groupby("Time")
    .size()
)


time_no_shows = (
    no_show_tests
    .groupby("Time")
    .size()
)


time_analysis = time_completed.copy()


time_analysis["Scheduled"] = (
    time_scheduled
)


time_analysis["No Shows"] = (
    time_no_shows
    .fillna(0)
)


time_analysis["Completed"] = (
    time_analysis["Pass"]
    +
    time_analysis["Fail"]
)


time_analysis["Pass Rate"] = (
    time_analysis["Pass"]
    /
    time_analysis["Completed"]
    *
    100
).round(2)


time_analysis["No Show Rate"] = (
    time_analysis["No Shows"]
    /
    time_analysis["Scheduled"]
    *
    100
).round(2)


add_section(
    "RESULTS BY TESTING TIME"
)


add_text(
    time_analysis.to_string()
)


# ============================================================
# SCORE BY TESTING TIME
# ============================================================

average_score_by_time = (
    completed_df
    .groupby("Time")["Score"]
    .agg(
        [
            "count",
            "mean",
            "median"
        ]
    )
    .round(2)
)


add_section(
    "SCORE BY TESTING TIME"
)


add_text(
    average_score_by_time.to_string()
)


# ============================================================
# POINTS FROM PASSING BY TIME
# ============================================================

points_from_passing_time = (
    completed_df
    .groupby("Time")["Points From Passing"]
    .agg(
        [
            "count",
            "mean",
            "median"
        ]
    )
    .round(2)
)


add_section(
    "POINTS ABOVE / BELOW PASSING BY TIME"
)


add_text(
    "Positive values = above passing."
)

add_text(
    "Negative values = below passing."
)

add_text()

add_text(
    points_from_passing_time.to_string()
)


# ============================================================
# PERFORMANCE RELATIVE TO PASSING
# ============================================================

average_relative_score = (
    completed_df[
        "Score Percent of Passing"
    ]
    .mean()
)


median_relative_score = (
    completed_df[
        "Score Percent of Passing"
    ]
    .median()
)


average_points_from_passing = (
    completed_df[
        "Points From Passing"
    ]
    .mean()
)


median_points_from_passing = (
    completed_df[
        "Points From Passing"
    ]
    .median()
)


add_section(
    "PERFORMANCE RELATIVE TO PASSING STANDARD"
)


add_text(
    f"Average Score as % of Passing Standard: "
    f"{average_relative_score:.2f}%"
)


add_text(
    f"Median Score as % of Passing Standard: "
    f"{median_relative_score:.2f}%"
)


add_text()


add_text(
    f"Average Points From Passing: "
    f"{average_points_from_passing:.2f}"
)


add_text(
    f"Median Points From Passing: "
    f"{median_points_from_passing:.2f}"
)


# ============================================================
# DISTANCE FROM SEMESTER END
# ============================================================

def distance_group(days):

    if pd.isna(days):

        return "Unknown"

    if days < 0:

        return "Before Semester End"

    elif days <= 3:

        return "0-3 Days After"

    elif days <= 7:

        return "4-7 Days After"

    elif days <= 14:

        return "8-14 Days After"

    elif days <= 21:

        return "15-21 Days After"

    else:

        return "22+ Days After"


database_df[
    "Semester End Distance Group"
] = (
    database_df[
        "Days From Semester End"
    ]
    .apply(distance_group)
)


distance_completed = (
    completed_df.copy()
)


distance_completed[
    "Distance Group"
] = (
    distance_completed[
        "Days From Semester End"
    ]
    .apply(distance_group)
)


distance_analysis = (
    distance_completed
    .groupby("Distance Group")
    .agg(

        Completed=("Result", "count"),

        Passes=(
            "Result",
            lambda x:
            (x == "Pass").sum()
        ),

        Failures=(
            "Result",
            lambda x:
            (x == "Fail").sum()
        ),

        Average_Score=(
            "Score",
            "mean"
        ),

        Median_Score=(
            "Score",
            "median"
        )
    )
)


distance_analysis["Pass Rate"] = (
    distance_analysis["Passes"]
    /
    distance_analysis["Completed"]
    *
    100
).round(2)


distance_analysis["Average_Score"] = (
    distance_analysis["Average_Score"]
    .round(2)
)


distance_analysis["Median_Score"] = (
    distance_analysis["Median_Score"]
    .round(2)
)


add_section(
    "PERFORMANCE BY DISTANCE FROM SEMESTER END"
)


add_text(
    distance_analysis.to_string()
)


# ============================================================
# NO-SHOW RATE BY DISTANCE
# ============================================================

distance_scheduled = (
    database_df
    .groupby(
        "Semester End Distance Group"
    )
    .size()
)


distance_no_shows = (
    database_df[
        database_df["No Show"] == 1
    ]
    .groupby(
        "Semester End Distance Group"
    )
    .size()
)


distance_no_show_analysis = pd.DataFrame(
    {
        "Scheduled": distance_scheduled,
        "No Shows": distance_no_shows
    }
).fillna(0)


distance_no_show_analysis[
    "No Show Rate"
] = (
    distance_no_show_analysis["No Shows"]
    /
    distance_no_show_analysis["Scheduled"]
    *
    100
).round(2)


add_section(
    "NO-SHOW RATE BY DISTANCE FROM SEMESTER END"
)


add_text(
    distance_no_show_analysis.to_string()
)


# ============================================================
# TESTING TIME × DISTANCE
# ============================================================

time_distance_analysis = (
    completed_df.copy()
)


time_distance_analysis[
    "Distance Group"
] = (
    time_distance_analysis[
        "Days From Semester End"
    ]
    .apply(distance_group)
)


time_distance_table = (
    time_distance_analysis
    .groupby(
        [
            "Distance Group",
            "Time"
        ]
    )
    .agg(

        Completed=("Result", "count"),

        Passes=(
            "Result",
            lambda x:
            (x == "Pass").sum()
        ),

        Average_Score=(
            "Score",
            "mean"
        )
    )
)


time_distance_table[
    "Pass Rate"
] = (
    time_distance_table["Passes"]
    /
    time_distance_table["Completed"]
    *
    100
).round(2)


time_distance_table[
    "Average_Score"
] = (
    time_distance_table[
        "Average_Score"
    ]
    .round(2)
)


add_section(
    "TESTING TIME × DISTANCE FROM SEMESTER END"
)


add_text(
    time_distance_table.to_string()
)


# ============================================================
# CORRELATIONS
# ============================================================

correlation_df = completed_df[
    [
        "Days From Semester End",
        "Score"
    ]
].dropna()


if len(correlation_df) >= 3:

    days_score_r, days_score_p = pearsonr(
        correlation_df[
            "Days From Semester End"
        ],
        correlation_df["Score"]
    )

else:

    days_score_r = None

    days_score_p = None


# ------------------------------------------------------------
# TESTING HOUR VS SCORE
# ------------------------------------------------------------

time_score_df = completed_df[
    [
        "Testing Hour",
        "Score"
    ]
].dropna()


if (
    len(time_score_df) >= 3
    and time_score_df["Testing Hour"].nunique() >= 2
):

    time_score_r, time_score_p = pearsonr(
        time_score_df["Testing Hour"],
        time_score_df["Score"]
    )

else:

    time_score_r = None

    time_score_p = None


# ------------------------------------------------------------
# DAYS VS RELATIVE SCORE
# ------------------------------------------------------------

relative_score_df = completed_df[
    [
        "Days From Semester End",
        "Score Percent of Passing"
    ]
].dropna()


if len(relative_score_df) >= 3:

    days_relative_r, days_relative_p = pearsonr(
        relative_score_df[
            "Days From Semester End"
        ],
        relative_score_df[
            "Score Percent of Passing"
        ]
    )

else:

    days_relative_r = None

    days_relative_p = None


# ============================================================
# CORRELATION INTERPRETATION
# ============================================================

def interpret_correlation(value):

    if value is None:

        return "Not enough data."

    absolute_value = abs(value)


    if absolute_value < 0.20:

        strength = "Very weak"

    elif absolute_value < 0.40:

        strength = "Weak"

    elif absolute_value < 0.60:

        strength = "Moderate"

    elif absolute_value < 0.80:

        strength = "Strong"

    else:

        strength = "Very strong"


    if value > 0:

        direction = "positive"

    elif value < 0:

        direction = "negative"

    else:

        direction = "no"


    return (
        f"{strength} {direction} relationship"
    )


# ============================================================
# CORRELATION REPORT
# ============================================================

add_section(
    "CORRELATION ANALYSIS"
)


add_text(
    "Correlations indicate association, not causation."
)


add_text()


if days_score_r is not None:

    add_text(
        f"Days From Semester End vs Score: "
        f"r = {days_score_r:.3f}"
    )

    add_text(
        f"p-value = {days_score_p:.4f}"
    )

    add_text(
        interpret_correlation(
            days_score_r
        )
    )

else:

    add_text(
        "Days From Semester End vs Score: "
        "Not enough data."
    )


add_text()


if time_score_r is not None:

    add_text(
        f"Testing Hour vs Score: "
        f"r = {time_score_r:.3f}"
    )

    add_text(
        f"p-value = {time_score_p:.4f}"
    )

    add_text(
        interpret_correlation(
            time_score_r
        )
    )

else:

    add_text(
        "Testing Hour vs Score: "
        "Not enough data."
    )


add_text()


if days_relative_r is not None:

    add_text(
        f"Days From Semester End vs Relative Score: "
        f"r = {days_relative_r:.3f}"
    )

    add_text(
        f"p-value = {days_relative_p:.4f}"
    )

    add_text(
        interpret_correlation(
            days_relative_r
        )
    )

else:

    add_text(
        "Days From Semester End vs Relative Score: "
        "Not enough data."
    )


# ============================================================
# FISHER'S EXACT TEST
# TESTING TIME VS PASS/FAIL
# ============================================================

statistical_tests = []


# Create 2x2 table

time_pass_fail = pd.crosstab(
    completed_df["Time"],
    completed_df["Result"]
)


if (
    "9am" in time_pass_fail.index
    and "1pm" in time_pass_fail.index
):

    if "Pass" not in time_pass_fail.columns:

        time_pass_fail["Pass"] = 0

    if "Fail" not in time_pass_fail.columns:

        time_pass_fail["Fail"] = 0


    contingency_table = [
        [
            time_pass_fail.loc[
                "9am",
                "Pass"
            ],

            time_pass_fail.loc[
                "9am",
                "Fail"
            ]
        ],

        [
            time_pass_fail.loc[
                "1pm",
                "Pass"
            ],

            time_pass_fail.loc[
                "1pm",
                "Fail"
            ]
        ]
    ]


    odds_ratio, fisher_p = fisher_exact(
        contingency_table
    )


    statistical_tests.append(
        (
            "Fisher's Exact Test",
            fisher_p
        )
    )

else:

    odds_ratio = None

    fisher_p = None


# ============================================================
# CHI-SQUARE TEST
# TESTING TIME VS PASS/FAIL
# ============================================================

if (
    len(time_pass_fail) >= 2
    and time_pass_fail.shape[1] >= 2
):

    chi_table = time_pass_fail[
        ["Pass", "Fail"]
    ]

    chi2, chi_p, chi_dof, chi_expected = (
        chi2_contingency(
            chi_table
        )
    )

else:

    chi2 = None

    chi_p = None

    chi_dof = None

    chi_expected = None


# ============================================================
# MANN-WHITNEY U TEST
# 9 AM VS 1 PM SCORES
# ============================================================

nine_am_scores = completed_df[
    completed_df["Time"] == "9am"
]["Score"].dropna()


one_pm_scores = completed_df[
    completed_df["Time"] == "1pm"
]["Score"].dropna()


if (
    len(nine_am_scores) >= 2
    and len(one_pm_scores) >= 2
):

    mw_stat, mw_p = mannwhitneyu(
        nine_am_scores,
        one_pm_scores,
        alternative="two-sided"
    )

else:

    mw_stat = None

    mw_p = None


# ============================================================
# EFFECT SIZE FOR 9 AM VS 1 PM
# ============================================================

if (
    len(nine_am_scores) >= 2
    and len(one_pm_scores) >= 2
):

    median_difference = (
        one_pm_scores.median()
        -
        nine_am_scores.median()
    )

    mean_difference = (
        one_pm_scores.mean()
        -
        nine_am_scores.mean()
    )

else:

    median_difference = None

    mean_difference = None


# ============================================================
# KRUSKAL-WALLIS
# DISTANCE GROUP VS SCORE
# ============================================================

distance_score_groups = []

distance_group_names = []


for group_name, group_data in (
    completed_df
    .assign(
        Distance_Group=
        completed_df[
            "Days From Semester End"
        ].apply(distance_group)
    )
    .groupby(
        "Distance_Group"
    )
):

    scores = (
        group_data["Score"]
        .dropna()
    )


    if len(scores) >= 2:

        distance_score_groups.append(
            scores
        )

        distance_group_names.append(
            group_name
        )


if len(distance_score_groups) >= 2:

    kruskal_stat, kruskal_p = kruskal(
        *distance_score_groups
    )

else:

    kruskal_stat = None

    kruskal_p = None


# ============================================================
# STATISTICAL TEST REPORT
# ============================================================

add_section(
    "STATISTICAL SIGNIFICANCE TESTS"
)


add_text(
    "Significance level used: alpha = 0.05"
)


add_text(
    "A p-value below 0.05 is commonly considered "
    "statistically significant."
)


add_text(
    "Statistical significance does NOT prove causation "
    "or practical importance."
)


# ------------------------------------------------------------
# FISHER
# ------------------------------------------------------------

add_text()


add_text(
    "TEST 1: TESTING TIME VS PASS/FAIL"
)


add_text(
    "Fisher's Exact Test"
)


if fisher_p is not None:

    add_text(
        f"Odds Ratio: {odds_ratio:.3f}"
    )

    add_text(
        f"p-value: {fisher_p:.4f}"
    )

    if fisher_p < 0.05:

        add_text(
            "Result: Statistically significant "
            "association at the 0.05 level."
        )

    else:

        add_text(
            "Result: Not statistically significant "
            "at the 0.05 level."
        )

else:

    add_text(
        "Not enough data to perform this test."
    )


# ------------------------------------------------------------
# CHI-SQUARE
# ------------------------------------------------------------

add_text()


add_text(
    "TEST 2: TESTING TIME VS PASS/FAIL"
)


add_text(
    "Chi-Square Test of Independence"
)


if chi_p is not None:

    add_text(
        f"Chi-square statistic: {chi2:.3f}"
    )

    add_text(
        f"Degrees of freedom: {chi_dof}"
    )

    add_text(
        f"p-value: {chi_p:.4f}"
    )

    if chi_p < 0.05:

        add_text(
            "Result: Statistically significant "
            "association at the 0.05 level."
        )

    else:

        add_text(
            "Result: Not statistically significant "
            "at the 0.05 level."
        )

else:

    add_text(
        "Not enough data to perform this test."
    )


# ------------------------------------------------------------
# MANN-WHITNEY
# ------------------------------------------------------------

add_text()


add_text(
    "TEST 3: 9 AM VS 1 PM SCORES"
)


add_text(
    "Mann-Whitney U Test"
)


if mw_p is not None:

    add_text(
        f"U statistic: {mw_stat:.3f}"
    )

    add_text(
        f"p-value: {mw_p:.4f}"
    )

    add_text(
        f"Mean score difference (1 PM - 9 AM): "
        f"{mean_difference:.2f}"
    )

    add_text(
        f"Median score difference (1 PM - 9 AM): "
        f"{median_difference:.2f}"
    )

    if mw_p < 0.05:

        add_text(
            "Result: The score distributions differ "
            "statistically at the 0.05 level."
        )

    else:

        add_text(
            "Result: No statistically significant "
            "difference detected at the 0.05 level."
        )

else:

    add_text(
        "Not enough data to perform this test."
    )


# ------------------------------------------------------------
# KRUSKAL-WALLIS
# ------------------------------------------------------------

add_text()


add_text(
    "TEST 4: SCORE VS DISTANCE FROM SEMESTER END"
)


add_text(
    "Kruskal-Wallis Test"
)


if kruskal_p is not None:

    add_text(
        f"H statistic: {kruskal_stat:.3f}"
    )

    add_text(
        f"p-value: {kruskal_p:.4f}"
    )

    add_text(
        f"Groups tested: "
        f"{', '.join(distance_group_names)}"
    )

    if kruskal_p < 0.05:

        add_text(
            "Result: At least one distance group "
            "differs statistically from another."
        )

        add_text(
            "Additional testing would be needed to "
            "identify which groups differ."
        )

    else:

        add_text(
            "Result: No statistically significant "
            "difference detected between the groups."
        )

else:

    add_text(
        "Not enough data to perform this test."
    )


# ============================================================
# SAMPLE SIZE CONSIDERATIONS
# ============================================================

add_section(
    "SAMPLE SIZE CONSIDERATIONS"
)


add_text(
    "Small samples can produce unstable percentages "
    "and unreliable statistical conclusions."
)


add_text()


small_courses = course_results[
    course_results["Completed"] < 5
]


if len(small_courses) > 0:

    add_text(
        "COURSES WITH FEWER THAN 5 COMPLETED TESTS:"
    )

    add_text(
        small_courses[
            [
                "Completed",
                "Pass Rate"
            ]
        ].to_string()
    )

else:

    add_text(
        "No courses have fewer than 5 completed tests."
    )


add_text()


small_tests = test_results[
    test_results["Completed"] < 5
]


if len(small_tests) > 0:

    add_text(
        "CERTIFICATION TESTS WITH FEWER THAN "
        "5 COMPLETED TESTS:"
    )

    add_text(
        small_tests[
            [
                "Completed",
                "Pass Rate"
            ]
        ].to_string()
    )

else:

    add_text(
        "No certification tests have fewer than "
        "5 completed tests."
    )


add_text()


small_sections = section_results[
    section_results["Completed"] < 5
]


if len(small_sections) > 0:

    add_text(
        "SECTIONS WITH FEWER THAN 5 COMPLETED TESTS:"
    )

    add_text(
        small_sections[
            [
                "Completed",
                "Pass Rate"
            ]
        ].to_string()
    )

else:

    add_text(
        "No sections have fewer than 5 completed tests."
    )


# ============================================================
# BUILD AI PROMPT
# ============================================================

if days_score_r is not None:

    days_correlation_text = (
        f"r = {days_score_r:.3f}, "
        f"p = {days_score_p:.4f}"
    )

else:

    days_correlation_text = (
        "Not enough data."
    )


if time_score_r is not None:

    time_correlation_text = (
        f"r = {time_score_r:.3f}, "
        f"p = {time_score_p:.4f}"
    )

else:

    time_correlation_text = (
        "Not enough data."
    )


if days_relative_r is not None:

    relative_correlation_text = (
        f"r = {days_relative_r:.3f}, "
        f"p = {days_relative_p:.4f}"
    )

else:

    relative_correlation_text = (
        "Not enough data."
    )


if fisher_p is not None:

    fisher_text = (
        f"Odds Ratio = {odds_ratio:.3f}, "
        f"p = {fisher_p:.4f}"
    )

else:

    fisher_text = (
        "Not enough data."
    )


if mw_p is not None:

    mw_text = (
        f"U = {mw_stat:.3f}, "
        f"p = {mw_p:.4f}"
    )

else:

    mw_text = (
        "Not enough data."
    )


if kruskal_p is not None:

    kruskal_text = (
        f"H = {kruskal_stat:.3f}, "
        f"p = {kruskal_p:.4f}"
    )

else:

    kruskal_text = (
        "Not enough data."
    )


ai_prompt = f"""

I am analyzing certification testing data for an educational
testing program.

Please analyze the data below and provide a clear, practical,
evidence-based interpretation.

The purpose is to identify patterns, relationships, areas of
concern, positive trends, and opportunities for improvement.

IMPORTANT RULES:

1. Do not simply repeat the numbers.

2. Clearly distinguish between what the data directly shows
   and possible explanations.

3. Correlation does NOT prove causation.

4. Statistical significance does NOT prove causation.

5. Statistical significance does NOT necessarily mean a
   difference is practically important.

6. Consider sample size before drawing conclusions.

7. Treat groups with fewer than 5 observations very cautiously.

8. Professor-level results are descriptive and for
   record-keeping only.

9. Do NOT rank, criticize, or evaluate professors.

10. Do NOT interpret professor results as evidence of teaching
    effectiveness.

11. Do NOT assign responsibility to professors for student
    outcomes.

12. Course and section differences should also be treated
    cautiously because student populations and other factors
    may differ.

13. Identify positive trends as well as areas of concern.

14. Clearly explain statistical tests in plain language.

15. If a result is statistically significant, explain what
    that means without implying causation.

16. If a result is not statistically significant, do not say
    that this proves there is no relationship.

17. Pay particular attention to whether observed patterns
    are large enough and consistent enough to warrant
    further investigation.


============================================================
OVERALL RESULTS
============================================================

Total Scheduled Tests: {total_tests}
Completed Tests: {completed_count}
No Shows: {no_show_count}

Passed: {passed_count}
Failed: {failed_count}

Pass Rate: {pass_rate:.2f}%
Failure Rate: {failure_rate:.2f}%
No-Show Rate: {no_show_rate:.2f}%


============================================================
RESULTS BY COURSE
============================================================

{course_results.to_string()}


============================================================
RESULTS BY PROFESSOR
============================================================

{professor_results.to_string()}

Professor results are descriptive only and must not be used
to evaluate instructor performance.


============================================================
RESULTS BY CERTIFICATION TEST
============================================================

{test_results.to_string()}


============================================================
RESULTS BY SECTION
============================================================

{section_results.to_string()}


============================================================
NO-SHOW RATE BY COURSE
============================================================

{no_show_course_analysis.to_string()}


============================================================
TESTING TIME
============================================================

{time_analysis.to_string()}


============================================================
SCORES BY TESTING TIME
============================================================

{average_score_by_time.to_string()}


============================================================
POINTS FROM PASSING BY TESTING TIME
============================================================

{points_from_passing_time.to_string()}


============================================================
PERFORMANCE RELATIVE TO PASSING
============================================================

Average Score as % of Passing:
{average_relative_score:.2f}%

Median Score as % of Passing:
{median_relative_score:.2f}%

Average Points From Passing:
{average_points_from_passing:.2f}

Median Points From Passing:
{median_points_from_passing:.2f}


============================================================
DISTANCE FROM SEMESTER END
============================================================

{distance_analysis.to_string()}


============================================================
NO-SHOW RATE BY DISTANCE
============================================================

{distance_no_show_analysis.to_string()}


============================================================
TIME × DISTANCE FROM SEMESTER END
============================================================

{time_distance_table.to_string()}


============================================================
CORRELATIONS
============================================================

Days From Semester End vs Score:
{days_correlation_text}

Testing Hour vs Score:
{time_correlation_text}

Days From Semester End vs Relative Score:
{relative_correlation_text}


============================================================
STATISTICAL SIGNIFICANCE TESTS
============================================================

Fisher's Exact Test:
Testing Time vs Pass/Fail

{fisher_text}


Mann-Whitney U Test:
9 AM vs 1 PM Scores

{mw_text}


Kruskal-Wallis Test:
Distance From Semester End vs Score

{kruskal_text}


============================================================
ANALYSIS REQUESTED
============================================================

1. EXECUTIVE SUMMARY

Summarize the most important findings in plain language.


2. POSITIVE TRENDS

Identify meaningful areas of stronger performance.


3. AREAS OF CONCERN

Identify patterns that deserve additional attention.


4. TESTING TIME

Analyze differences between 9 AM and 1 PM.

Discuss:
- Pass rate
- No-show rate
- Average score
- Median score
- Points from passing
- Statistical significance

Do not assume testing time caused any difference.


5. DISTANCE FROM SEMESTER END

Analyze performance and attendance based on how far testing
occurred from the end of the semester.


6. TIME × DISTANCE

Determine whether the apparent testing-time pattern remains
consistent when considering distance from semester end.


7. CORRELATIONS

Explain each correlation and its p-value.

Explain:
- Direction
- Strength
- Statistical significance
- Practical importance
- Limitations


8. STATISTICAL TESTS

Explain each statistical test in plain language.

For each test discuss:
- What was tested
- Result
- p-value
- Whether statistically significant
- What the result does and does not tell us


9. SAMPLE SIZE

Identify conclusions that are limited by small sample sizes.


10. PROFESSOR DATA

Treat professor information strictly as descriptive
record-keeping.

Do not rank or evaluate professors.


11. POSSIBLE EXPLANATIONS

Suggest possible explanations for meaningful patterns.

Clearly label explanations as possibilities rather than facts.


12. RECOMMENDATIONS

Provide 3 to 5 practical recommendations.

Focus on things the testing program can investigate,
measure, or potentially change.


13. FUTURE DATA COLLECTION

Recommend additional data that would make the analysis
stronger over time.

Examples may include:
- Student preparation
- Previous attempts
- Course attendance
- Tutoring
- Testing location
- Time between course completion and certification exam
- Number of days between final exam and certification exam


14. PRIORITY FINDINGS

Identify the three findings that deserve the most attention.

For each:
- Explain what the data shows.
- Explain why it may matter.
- Explain what should be investigated next.

Remember:

The purpose of this analysis is to identify patterns and
opportunities for investigation, NOT to assign blame.

"""


# ============================================================
# SAVE STATISTICAL REPORT TO TXT
# ============================================================

report_date = datetime.now().strftime(
    "%Y-%m-%d_%H-%M-%S"
)


report_filename = (
    f"testing_analysis_{report_date}.txt"
)


report_path = os.path.join(
    REPORT_FOLDER,
    report_filename
)


with open(
    report_path,
    "w",
    encoding="utf-8"
) as report_file:

    report_file.write(
        report
    )


# ============================================================
# PRINT ONLY AI PROMPT TO TERMINAL
# ============================================================

print()

print(
    "=" * 60
)

print(
    "AI ANALYSIS PROMPT".center(60)
)

print(
    "=" * 60
)

print()

print(
    ai_prompt
)

print()

print(
    "=" * 60
)

print(
    "STATISTICAL REPORT SAVED"
)

print(
    "=" * 60
)

print(
    report_path
)

print()

print(
    "The full statistical results are in the TXT file."
)

print(
    "The text above is the AI-ready analysis prompt."
)


# ============================================================
# CLOSE DATABASE
# ============================================================

connection.close()

