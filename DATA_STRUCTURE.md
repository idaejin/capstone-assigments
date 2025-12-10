# Data Structure Requirements

## Overview

The matching algorithm requires three input files with specific formats. This document explains the data structure for each file.

## File 1: Students File (`students.txt`)

### Format
```
StudentID: Topic1, Topic2, Topic3, Topic4, Topic5
```

### Rules
- Each student must list **exactly 5 topic preferences** (compulsory)
- Preferences are ordered: Topic1 is most preferred, Topic5 is least preferred
- All students must have exactly 5 preferences (no more, no less)
- Lines starting with `#` are treated as comments and ignored
- Empty lines are ignored

### Example
```
# BDBA Students
BDBA001: T01, T05, T12, T18, T23
BDBA002: T05, T01, T18
BDBA003: T12, T05, T01, T28, T33

# BCSAI Students
BCSAI001: T02, T06, T13, T19, T24
BCSAI002: T06, T02, T19
```

### Validation
- ✅ Valid: Exactly 5 preferences per student
- ❌ Invalid: More than 5 preferences
- ❌ Invalid: Fewer than 5 preferences
- ❌ Invalid: No preferences (empty list)
- ❌ Invalid: Duplicate topics in same student's list

---

## File 2: Topics File (`topics.txt`)

### Format
```
TopicID: Area
```

### Rules
- **TopicID**: Unique identifier for the topic (e.g., T01, T02)
- **Area**: Academic area of the topic (e.g., "Data Science", "Machine Learning", "Computer Science", "Mathematics")
- **NO CAPACITY LIMIT**: Topics have no capacity limit - only supervisor capacity matters

### Example
```
# Data Science Topics
T01: Data Science
T02: Data Science
T03: Data Science

# Machine Learning Topics
T13: Machine Learning
T14: Machine Learning
```

### Notes
- Topics **must** have an area
- **NO CAPACITY LIMIT** - Topics can accept unlimited students (only supervisor capacity limits apply)
- **Area** categorizes topics by academic discipline
- Topics do **not** have student preferences - matching is based solely on student preferences for topics

### Validation
- ✅ Valid: Topic with area (e.g., `T01: Data Science`)
- ❌ Invalid: Missing area

---

## File 3: Supervisors File (`supervisors.txt`)

### Format
```
SupervisorID: MaximumCapacity, Topic1:ExpertiseLevel1, Topic2:ExpertiseLevel2, ...
```

### Rules
- **SupervisorID**: Unique identifier for the supervisor (e.g., SUP01, SUP02)
- **MaximumCapacity**: Maximum total number of students the supervisor can handle across **all topics** they supervise (integer, **maximum 10**)
- **Bachelor-Topic Expertise Combinations**: List of bachelor-topic combinations the supervisor can supervise with their expertise level
  - Format: `Bachelor:TopicID:ExpertiseLevel`
  - **At least 1 combination required** (no maximum limit)
  - A supervisor can supervise any number of bachelor-topic combinations
  - Expertise levels: Expert, Advanced, Intermediate, Beginner
  - Supervisors choose which bachelor-topic combinations they want to supervise

### Example
```
# Supervisors with bachelor-topic expertise (no limit on topics, max capacity 10)
SUP01: 8, BDBA:T01:Expert, BCSAI:T01:Advanced, BBA+BDBA:T03:Intermediate
SUP02: 7, BDBA:T02:Advanced, BDBA:T04:Expert, BCSAI:T02:Expert
SUP03: 10, BDBA:T01:Advanced, BCSAI:T03:Expert, BBA+BDBA:T05:Expert

# A supervisor can supervise many topics for different bachelor programs
SUP13: 8, BDBA:T13:Expert, BCSAI:T15:Expert, BBA+BDBA:T17:Advanced
SUP14: 6, BDBA:T14:Advanced, BCSAI:T16:Expert
```

### Notes
- Supervisors **choose** which bachelor-topic combinations they can supervise
- Each supervisor-bachelor-topic combination has an **expertise level**
- A supervisor can supervise the same topic for different bachelor programs with different expertise levels
- A supervisor can supervise any number of topics (no limit, but at least 1 required)
- Example: SUP01 can supervise T01 for BDBA (Expert), BCSAI (Advanced), and BBA+BDBA (Intermediate)
- The algorithm assigns each topic to the supervisor with highest expertise who listed it
- Supervisor capacity applies to the **total** across all topics they supervise

### Validation
- ✅ Valid: Supervisor with capacity (1-10) and at least 1 bachelor-topic combination
- ✅ Valid: Supervisor can list any number of bachelor-topic combinations (no limit)
- ❌ Invalid: Missing capacity
- ❌ Invalid: Non-numeric capacity
- ❌ Invalid: Capacity <= 0
- ❌ Invalid: Capacity > 10 (maximum allowed)
- ❌ Invalid: 0 bachelor-topic combinations (must have at least 1)
- ❌ Invalid: Invalid expertise level format (must be Bachelor:TopicID:ExpertiseLevel)

---

## Data Relationships

### Topic-Supervisor Relationship
- Topics are **not** directly assigned to supervisors in the topics file
- Supervisors **choose** topics they want to supervise (in supervisors file)
- Each topic is assigned to the supervisor with **highest expertise level** who listed it
- One supervisor can supervise multiple topics
- Supervisor capacity is the sum across all their topics

### Topic-Area Relationship
- Each topic belongs to an **academic area**
- Areas help organize and categorize topics
- Examples: Data Science, Machine Learning, Computer Science, Mathematics

### Topic-Student Relationship
- Students have preferences for topics (required, exactly 5)
- Topics do not have student preferences
- Matching is based solely on student preferences for topics

### Example Structure
```
Area: Data Science
  ├── Topic T01 (capacity: 5)
  ├── Topic T02 (capacity: 4)
  └── Topic T03 (capacity: 6)

Supervisor SUP01 (max capacity: 8)
  ├── Can supervise T01 (Expert level)
  ├── Can supervise T03 (Expert level)
  └── Can supervise T05 (Advanced level)

Student S1
  ├── Preferences: [T01, T02, T03, T04, T05]
  └── Will be matched based on topic preferences and capacities
```

---

## Complete Example

### students.txt
```
BDBA001: T01, T05, T12, T18, T23
BDBA002: T05, T01, T18
BCSAI001: T02, T06, T13, T19, T24
BBA_BDBA001: T01, T05, T12
```

### topics.txt
```
T01: Data Science, 5
T02: Machine Learning, 4
T05: Data Science, 4
T06: Machine Learning, 6
```

### supervisors.txt
```
SUP01: 8, T01:Expert, T05:Advanced
SUP02: 7, T02:Expert, T06:Advanced
SUP03: 9, T01:Advanced, T05:Expert
```

**Note:** In this example, T01 will be assigned to SUP01 (Expert level) rather than SUP03 (Advanced level), because SUP01 has higher expertise.

---

## Key Differences from Previous Version

### Changed
1. **Topics**: Now have areas instead of supervisor assignments
2. **Supervisors**: Now list topics they can supervise with expertise levels
3. **Supervisor-Topic Assignment**: Happens automatically based on expertise levels (highest expertise wins)

### Unchanged
1. Students still have 1-5 preferences
2. Topics can still have student preferences (optional)
3. Algorithm still produces stable matchings
4. Capacity constraints still apply

---

## Validation Checklist

Before running the algorithm, ensure:

- [ ] All students have 1-5 preferences
- [ ] All student preferences reference valid topics
- [ ] All topics have a valid area
- [ ] All topics have a valid capacity (> 0)
- [ ] All supervisors exist in supervisors file
- [ ] All supervisor topic references are valid topic IDs
- [ ] All expertise levels are valid (Expert, Advanced, Intermediate, Beginner)
- [ ] Supervisor capacities are reasonable (typically 1-10)
- [ ] Topic capacities are reasonable (typically 1-10)
- [ ] Each topic is listed by at least one supervisor

---

## Common Issues

### Issue: Student doesn't have exactly 5 preferences
**Solution**: Students must have exactly 5 preferences

### Issue: Topic has no supervisor
**Solution**: Ensure at least one supervisor lists this topic in their preferences

### Issue: Supervisor capacity too low
**Solution**: Increase supervisor max capacity or reduce number of topics they supervise

### Issue: Topic not listed by any supervisor
**Solution**: Add topic to at least one supervisor's preference list

### Issue: Invalid expertise level
**Solution**: Use one of: Expert, Advanced, Intermediate, Beginner
