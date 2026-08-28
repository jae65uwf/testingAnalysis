# Certification Testing Data Analysis Program

## What Is This?

This program analyzes certification testing data and looks for patterns in test results.

It takes testing data from a CSV file, cleans the data, stores it in an SQLite database, and produces a report with statistics and analysis.

The goal is to build a long-term history of certification testing results so that trends can be compared across courses, exams, testing times, and semesters.

The program also creates an AI-ready prompt that can be used to help interpret the results and identify possible areas for improvement.

---

# What Does the Program Do?

The program:

1. Imports testing data from a CSV file.
2. Cleans and organizes the data.
3. Saves the data to an SQLite database.
4. Calculates overall testing results.
5. Breaks results down by course, professor, exam, section, and testing time.
6. Looks at testing time and test performance.
7. Looks at how long after the semester students take their certification test.
8. Performs statistical tests to look for meaningful patterns.
9. Warns when groups have small sample sizes.
10. Creates a TXT report with the results.
11. Creates an AI prompt for further interpretation.

---

# What Does It Measure?

The program calculates things such as:

* Total tests scheduled
* Tests completed
* No-shows
* Passes
* Fails
* Pass rate
* Failure rate
* No-show rate
* Average scores
* Median scores
* Performance compared with the passing score

Results can be viewed by:

* Course
* Professor
* Certification exam
* Section
* Testing time
* Time since the end of the semester

---

# Statistical Tests

The program uses several statistical tests to look for patterns.

These tests do not prove that one thing caused another. They simply help determine whether a pattern is strong enough to investigate further.

## Pearson Correlation

Looks at whether two numerical values tend to change together.

The program uses it to examine things such as:

* Days from semester end vs. test score
* Testing hour vs. test score
* Days from semester end vs. performance relative to the passing score

Does one number tend to increase or decrease as the other changes?

---

## Fisher's Exact Test

Looks at whether two categories appear to be related.

The program uses it to compare:

* Testing time vs. Pass/Fail

For example, it can compare morning and afternoon testing results.

This test is useful when there are small groups of students.

---

## Chi-Square Test

Looks at whether two categories appear to be related.

The program uses it to examine:

* Testing time vs. Pass/Fail

It provides another way to determine whether differences in results may be more than random variation.

Small groups should be interpreted carefully.

---

## Mann-Whitney U Test

Compares the results of two groups.

The program uses it to compare:

* 9 AM scores vs. 1 PM scores

It is useful when the data is not normally distributed or the dataset is small.

The program also reports the mean and median differences so the size of the difference can be seen.

---

## Kruskal-Wallis Test

Compares more than two groups.

The program uses it to compare scores based on how far the test was taken from the end of the semester.

The current groups are:

* 0–3 days
* 4–7 days
* 8–14 days
* 15–21 days
* 22+ days

If the test finds a significant difference, additional analysis is needed to determine which groups are different.

---

# Understanding P-Values

The statistical tests produce a p-value.

The program generally uses 0.05 as the significance level.

A p-value below 0.05 is commonly considered statistically significant.

However, a significant result does not automatically mean that one factor caused another.

Likewise, a result above 0.05 does not prove that there is no relationship.

Sample size and the size of the actual difference also matter.

---

# Sample Size

Sample size is important when looking at these results.

A small group can produce a very high or very low percentage that may change dramatically when more students are added.

For example:

> 2 students tested and both passed = 100% pass rate

That does not necessarily tell us that the group performed better than:

> 100 students tested and 90 passed = 90% pass rate

The program identifies small groups so their results can be interpreted carefully.

---

# Testing Time

The program looks at whether testing results appear to differ based on the time of day.

It compares:

* Pass rates
* Failure rates
* No-show rates
* Average scores
* Median scores
* Performance above or below the passing score
* Statistical significance

The goal is not to assume that one testing time is better.

Instead, the program looks for patterns that may be worth investigating.

Other factors could affect the results, such as the course, certification exam, testing date, or number of students tested.

---

# Distance From Semester End

The program calculates how many days separate the certification test from the end of the semester.

It groups tests into:

* 0–3 days
* 4–7 days
* 8–14 days
* 15–21 days
* 22+ days

This helps determine whether testing results appear to change depending on how long students wait to take their certification exam.

The program does not assume that waiting longer causes a change in performance.

It simply looks for patterns.

---

# Testing Time + Semester End

The program can also look at testing time and distance from semester end together.

This can reveal patterns that may not be visible when looking at each factor separately.

For example, afternoon testing might have a higher pass rate overall, but that difference could change depending on whether students tested a few days after the semester or several weeks later.

---

# Comparing Different Certification Exams

Different certification exams may use different scoring systems and passing standards.

Because of this, raw scores cannot always be compared directly.

For example, a score of 700 on one exam may not represent the same performance as a score of 700 on another exam.

The program therefore also looks at:

* Test score
* Passing score
* Points above or below passing
* Score relative to the passing standard

This provides a better way to compare performance across different exams.

---

# Professor Information

Professor information is included for reporting and record-keeping.

The program is not designed to rank or evaluate professors.

Differences between professors may be related to many other factors, including:

* Course
* Certification exam
* Student population
* Sample size
* Testing schedule
* Student preparation

Professor-level results should therefore not be treated as evidence of instructor effectiveness.

---

# AI Analysis

The program creates a prompt that can be given to an AI system.

The AI is asked to:

* Find meaningful patterns
* Identify positive trends
* Identify areas of concern
* Explain the statistics in plain language
* Consider sample size
* Separate facts from possible explanations
* Avoid assuming causation
* Avoid evaluating professors
* Suggest possible improvements
* Identify information that could be collected in the future

The AI is an interpretation tool, not the source of the statistical evidence.

The actual data and statistical results should remain the primary evidence.

---

# Important Rules for Reading the Results

When looking at the results, remember:

### Correlation does not mean causation

If two things are related, that does not mean one caused the other.

### Statistical significance does not always mean practical importance

A difference can be statistically significant but too small to matter in practice.

### A non-significant result does not prove there is no relationship

A small dataset may not have enough information to detect a relationship.

### Small groups can be misleading

Percentages based on only a few students can change significantly as more data is collected.

### Context matters

Test difficulty, student preparation, course structure, testing schedule, and other factors may affect the results.

---

# Long-Term Goal

This project is designed to become a historical certification testing database.

As more data is added, the program can be used to look at:

* Semester-to-semester trends
* Course trends
* Certification exam trends
* Testing-time patterns
* No-show patterns
* Testing delays
* Pass-rate changes
* Relationships between different factors
* Areas that may need further investigation

The more data collected, the more useful the system should become.

---

# Project Structure

A typical project looks like this:

```text
PythonProject/
│
├── main.py
│
├── data/
│   └── certification_testing.csv
│
├── database/
│   └── analysis.db
│
├── reports/
│   └── testing_analysis_YYYY-MM-DD_HH-MM-SS.txt
│
└── README.md
```

---

# Requirements

The program requires:

* Python
* pandas
* scipy

SQLite is included with Python.

Install the required packages with:

```text
pip install pandas scipy
```

---

# Future Improvements

Possible future additions include:

* Importing multiple semesters
* Automatically identifying semesters
* Comparing semesters
* Adding charts
* Adding a graphical interface
* Adding filters
* Adding more statistical tests
* Tracking first attempts vs. retakes
* Tracking testing locations
* Tracking time between course completion and testing
* Creating PDF or HTML reports
* Connecting directly to an AI service
* Creating an interactive dashboard

---

# The Main Idea

The purpose of this program is not to make the data say something.

It is to help answer:

What happened?

What patterns do we see?

How strong is the evidence?

What might explain the pattern?

What information are we missing?

What should we investigate next?

The goal is to use testing data to make better decisions while avoiding unsupported conclusions.
