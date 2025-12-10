# Student-Project Allocation Matching Algorithm

## Overview

This project implements a matching algorithm for allocating students to capstone topics based on the **SPA-student algorithm** by Abraham, Irving, and Manlove (2007).

**Reference:** Abraham, D.J., Irving, R.W., and Manlove, D.M. (2007) Two algorithms for the student-project allocation problem. _Journal of Discrete Algorithms_, 5(1), pp. 73-90.

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit Web App

```bash
streamlit run app.py
```

Or use the provided script:

```bash
./run_app.sh
```

The app will open at `http://localhost:8501`

### 3. Using the Web Interface

1. **Input Data**: Upload or manually enter data for students, topics, and supervisors
2. **Load Example Data**: Click to load pre-configured example data
3. **Run Algorithm**: Execute the matching algorithm with sequential rounds
4. **View Results**: Analyze detailed metrics, visualizations, and unmatched students

## Project Structure

```
matching algorithm/
├── app.py                    # Streamlit web application
├── requirements.txt          # Python dependencies
├── run_app.sh               # Quick start script
├── README.md                # This file
├── STREAMLIT_GUIDE.md       # Streamlit app user guide
├── DATA_STRUCTURE.md        # Input data format specification
├── IMPROVING_MATCH_RATE.md  # Tips for better matching results
│
├── data/                    # Example data files
│   ├── students.txt         # 200 students (BDBA, BCSAI, BBA+BDBA)
│   ├── topics.txt           # 65 topics across 3 areas
│   └── supervisors.txt      # 40 supervisors with expertise levels
│
├── src/                     # Core algorithm implementation
│   ├── spa_algorithm.py     # SPA-student algorithm with sequential rounds
│   ├── data_loader.py       # Input file parsing and validation
│   └── main.py             # Command-line interface
│
├── evaluation/              # Evaluation framework
│   ├── metrics.py          # Evaluation metrics (stability, satisfaction, etc.)
│   ├── visualizations.py   # Charts and plots
│   └── reports.py          # Comprehensive reporting
│
└── tests/                   # Unit tests
    └── test_spa_algorithm.py
```

## Algorithm Features

### Sequential Rounds Matching

The algorithm runs in **multiple rounds** to maximize matches:

1. **Round 1**: All students apply to their first preference
2. **Round 2+**: Unmatched students continue with remaining preferences
3. **Stopping**: When all students matched or no new matches occur

### Key Features

- ✅ **Stable Matching**: Ensures no blocking pairs exist
- ✅ **Capacity Constraints**: Respects supervisor capacity limits (max 10 per supervisor)
- ✅ **Sequential Rounds**: Multiple rounds maximize match rate
- ✅ **Topic Preferences**: Students choose exactly 5 topics (compulsory)
- ✅ **Supervisor Expertise**: Supervisors specify expertise levels per bachelor-topic combination
- ✅ **No Topic Capacity Limit**: Only supervisor capacity matters
- ✅ **Constraint Verification**: Ensures no capacity violations

## Data Structure

### Students (`students.txt`)

```
StudentID: Topic1, Topic2, Topic3, Topic4, Topic5
```

- **Exactly 5 preferences** required (compulsory)
- Bachelor programs: **BDBA**, **BCSAI**, **BBA+BDBA**

Example:
```
BDBA001: T01, T05, T12, T18, T23
BCSAI001: T02, T06, T13, T19, T24
BBA_BDBA001: T01, T05, T12, T18, T23
```

### Topics (`topics.txt`)

```
TopicID: Area
```

- Topics have **no capacity limit** (only supervisor capacity matters)
- 3 Areas: Data Science, Machine Learning, Computer Science

Example:
```
T01: Data Science
T21: Machine Learning
T46: Computer Science
```

### Supervisors (`supervisors.txt`)

```
SupervisorID: MaxCapacity, Bachelor1:Topic1:ExpertiseLevel1, ...
```

- **Max capacity**: 10 students per supervisor (total across all topics)
- **No limit** on number of bachelor-topic combinations
- Expertise levels: Expert, Advanced, Intermediate, Beginner

Example:
```
SUP01: 8, BDBA:T01:Expert, BCSAI:T01:Advanced, BBA+BDBA:T05:Intermediate
SUP02: 10, BDBA:T02:Expert, BDBA:T03:Advanced
```

## Evaluation Metrics

The algorithm evaluates matching quality across multiple dimensions:

- **Stability**: Checks for blocking pairs (student-topic pairs that prefer each other)
- **Student Satisfaction**: Average rank of assigned topics (lower is better)
- **Efficiency**: Match rate and resource utilization
- **Fairness**: Distribution of satisfaction (Gini coefficient)
- **Constraint Satisfaction**: Verification of capacity limits

## Command-Line Usage

Run the algorithm from the command line:

```bash
python src/main.py \
  --students data/students.txt \
  --projects data/topics.txt \
  --supervisors data/supervisors.txt \
  --output output/result.csv
```

## Example Data

The included example data contains:
- **200 students** (67 BDBA, 67 BCSAI, 66 BBA+BDBA)
- **65 topics** (20 Data Science, 25 Machine Learning, 20 Computer Science)
- **40 supervisors** (capacity 8-10, with bachelor-topic expertise)

Expected match rate: **~96-97%** with no constraint violations

## Documentation

- **[STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)**: How to use the web interface
- **[DATA_STRUCTURE.md](DATA_STRUCTURE.md)**: Detailed input format specification
- **[IMPROVING_MATCH_RATE.md](IMPROVING_MATCH_RATE.md)**: Tips to improve matching results

## Requirements

- Python 3.8+
- streamlit
- pandas
- numpy
- matplotlib

See `requirements.txt` for full list.

## Testing

Run unit tests:

```bash
python -m pytest tests/
```

## License

This project is for academic use at IE University.

## References

- Abraham, D.J., Irving, R.W., and Manlove, D.M. (2007). Two algorithms for the student-project allocation problem. _Journal of Discrete Algorithms_, 5(1), pp. 73-90.
- Implementation inspired by: https://richarddmorey.github.io/studentProjectAllocation/
