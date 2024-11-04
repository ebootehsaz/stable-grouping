# Grouping Algorithm README

This repository contains two Python scripts for grouping students based on their preferences:

1. `main.py`: Implements a smart grouping algorithm using a graph-based approach, ensuring mutual preferences are prioritized and group sizes are strictly enforced.
2. `heuristic_grouping.py`: Implements a heuristic grouping algorithm as an alternative method.

## Table of Contents

- [Requirements](#requirements)
- [Files](#files)
- [Usage](#usage)
- [Algorithm Details](#algorithm-details)
  - [main.py](#mainpy)
  - [heuristic_grouping.py](#heuristic_groupingpy)
- [Data Preparation](#data-preparation)
- [Example Output](#example-output)
- [Notes](#notes)

## Requirements

- Python 3.x
- Required Python packages:
  - `pandas`
  - `networkx`

Install the required packages using:

```bash
pip install -r requirements.txt
```

## Files

- main.py: The main script implementing the smart grouping algorithm.
- heuristic_grouping.py: An alternative script using a heuristic approach.
- preferences.csv: A CSV file containing students' preferences.
- roster.csv: A CSV file containing the list of students.

## Usage

- Prepare the Data Files:
- preferences.csv should have the following columns:
  - I am _____ (your name)
  - Preference 1
  - Preference 2
  - Preference 3
  - Preference 4
  - Preference 5
- roster.csv should have a single column:
  - Name

## Algorithm Details

### main.py

The main.py script implements a smart grouping algorithm with the following features:

Graph-Based Approach: Constructs a weighted graph where nodes represent students, and edges represent the strength of mutual preferences.
Mutual Preference Prioritization: Gives higher weight to mutual high rankings and adjusts weights based on the combination of preferences.
Fixed Total Groups: Enforces a specified number of groups and strictly adheres to predefined group sizes.
Handling Missing Preferences: Accounts for students who didn't submit preferences by considering others' preferences for them.
Group Size Enforcement: Ensures that each group matches the specified size by adjusting assignments if necessary.

### heuristic_grouping.py

The heuristic_grouping.py script provides an alternative heuristic approach:

Heuristic Method: Uses a simple heuristic to assign students to groups based on their preferences.
Preference-Based Assignment: Prioritizes students with the most unassigned preferred peers.
Group Filling: Fills groups to the maximum size by adding unassigned students.

## Notes

- Data Consistency: Ensure that all student names are consistent across preferences.csv and roster.csv. Typos or mismatches can lead to incorrect groupings.
- Customization: You can adjust the total number of groups and other parameters within the scripts to suit your specific needs.
- Performance: The algorithms are designed to run efficiently. However, for very large datasets, execution time may increase.
- Dependencies: The pulp library is imported in heuristic_grouping.py but not used. If you plan to extend the script to use linear programming, pulp will be necessary.