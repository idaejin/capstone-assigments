# Streamlit App User Guide

## Quick Start

### Starting the App

```bash
streamlit run app.py
```

Or use the provided script:

```bash
./run_app.sh
```

The app will open at `http://localhost:8501`

## Main Pages

### 🏠 Home

Overview of the SPA-student algorithm with:
- Algorithm description
- Key features
- Quick statistics

### 📁 Input Data

Three ways to provide data:

#### Option 1: Load Example Data (Recommended for first-time users)
1. Click **"Load Example Data"**
2. Automatically loads 200 students, 65 topics, 40 supervisors
3. View statistics and data preview

#### Option 2: Manual Text Input
1. Enter data directly in text areas
2. Format must match specification (see DATA_STRUCTURE.md)
3. Click **"Save Input Data"**

#### Option 3: File Upload
1. Upload `.txt` files for students, topics, and supervisors
2. Files must follow correct format
3. Click **"Load Data"**

**Data Statistics Display:**
- Total counts for students, topics, supervisors
- Program breakdown (BDBA, BCSAI, BBA+BDBA)
- Topics by supervisor with expertise levels
- Capacity analysis

### 🚀 Run Algorithm

1. Ensure data is loaded (see Input Data page)
2. Click **"Run Algorithm"** button (full-width)
3. View results:
   - Matching rounds executed
   - Students matched (count and percentage)
   - Average satisfaction (lower rank is better)
   - Stability status
   - Interpretation and next steps

**Sequential Rounds:**
- Round 1: All students apply to first preference
- Round 2+: Unmatched students continue with remaining preferences
- Stops when all matched or no new matches

**Results Span Full Page:**
- All metrics displayed at full width
- Easy to read and interpret
- Clear visual feedback

### 📊 Results & Analysis

Comprehensive analysis of matching results:

#### Key Metrics Overview
- Stability (blocking pairs)
- Match rate (percentage matched)
- Student satisfaction (average rank)
- Constraint satisfaction (capacity violations)

#### Round Statistics
- Total rounds executed
- Students matched per round
- Cumulative totals
- Round-by-round breakdown

#### Unmatched Students Analysis
If students remain unmatched:
- Full list with student IDs and programs
- Their 5 preferences
- **Primary reason** for each (why they couldn't be matched):
  - No supervisor available for bachelor-topic combination
  - All preferred supervisors at capacity
  - Topics already allocated to other students
- Detailed breakdown per preference
- Summary statistics
- **Actionable recommendations**

#### Detailed Tabs
- **Stability**: Blocking pairs analysis
- **Satisfaction**: Student satisfaction metrics
- **Efficiency**: Match rates and utilization
- **Fairness**: Satisfaction distribution
- **Constraints**: Capacity verification

#### Visualizations
- Satisfaction distribution
- Matching summary dashboard
- Program-level breakdowns

#### Improvement Suggestions
Context-aware suggestions based on results:
- Low match rate: Capacity or preference issues
- Low satisfaction: Preference concentration
- Fairness concerns: Uneven distribution
- Stability issues: Blocking pairs detected

### ℹ️ About

Project information:
- Algorithm description and reference
- Bachelor programs (BDBA, BCSAI, BBA+BDBA)
- Data format specifications
- Implementation details
- Contact information

## Data Format Quick Reference

### Students
```
StudentID: Topic1, Topic2, Topic3, Topic4, Topic5
```
- Exactly 5 preferences (compulsory)
- Bachelor programs: BDBA, BCSAI, BBA+BDBA

### Topics
```
TopicID: Area
```
- No capacity limit (only supervisor capacity matters)
- Areas: Data Science, Machine Learning, Computer Science

### Supervisors
```
SupervisorID: MaxCapacity, Bachelor1:Topic1:Expertise1, ...
```
- Max capacity: 10 (total across all topics)
- No limit on number of bachelor-topic combinations
- Expertise: Expert, Advanced, Intermediate, Beginner

## Tips for Best Results

### For High Match Rates:
1. Ensure sufficient supervisor capacity (total capacity > total students)
2. Good supervisor coverage for all bachelor-topic combinations
3. Encourage diverse student preferences
4. Balance topic popularity

### For High Satisfaction:
1. Students provide realistic preferences
2. Adequate supervisor capacity for popular topics
3. Good distribution of supervisor expertise

### For Constraint Satisfaction:
1. Set reasonable supervisor capacities (≤ 10)
2. Ensure supervisors cover relevant bachelor-topic combinations
3. Verify data before running algorithm

## Troubleshooting

### Low Match Rate
- Check if total supervisor capacity ≥ total students
- Verify supervisor coverage for student preferences
- Review if preferences are too concentrated on few topics
- See diagnostics in Results & Analysis for specific issues

### Constraint Violations
- If violations appear, there's a bug in the algorithm
- Contact developers with your data files
- Check input data for errors

### Data Loading Errors
- Verify file format matches specification
- Check for exactly 5 preferences per student
- Ensure supervisor capacity ≤ 10
- Validate bachelor-topic-expertise format

## Navigation

Use the sidebar to switch between pages:
1. 🏠 Home
2. 📁 Input Data
3. 🚀 Run Algorithm
4. 📊 Results & Analysis
5. ℹ️ About

## Advanced Features

### Export Results
- Results can be viewed in the app
- Full matching table displayed
- Statistics and metrics available
- Copy data for external analysis

### Multiple Runs
- Load different datasets
- Compare results across runs
- Test different configurations
- Analyze sensitivity to changes

## Support

For issues or questions:
1. Check DATA_STRUCTURE.md for format details
2. Review IMPROVING_MATCH_RATE.md for optimization tips
3. Contact course administrators

## Example Workflow

1. **Start**: Open app, go to Input Data
2. **Load**: Click "Load Example Data" to see how it works
3. **Run**: Go to Run Algorithm, click the button
4. **Analyze**: Review results in Results & Analysis
5. **Understand**: Check unmatched students and reasons
6. **Iterate**: Make adjustments and run again
7. **Export**: Use the data for your needs

Happy matching! 🎓
