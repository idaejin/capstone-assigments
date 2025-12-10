# How to Increase Match Rate

## Overview

The match rate is the percentage of students successfully assigned to topics. A low match rate indicates capacity constraints or preference misalignment. This guide provides actionable strategies to improve matching results.

## Key Factors Affecting Match Rate

1. **Supervisor Capacity** - Maximum students per supervisor (across all topics)
2. **Supervisor Coverage** - Whether supervisors can supervise bachelor-topic combinations
3. **Topic Availability** - Number of topics relative to students
4. **Preference Diversity** - How diverse student preferences are across topics

**Important**: Topics have **NO capacity limit**. Only supervisor capacity matters.

---

## Strategies to Increase Match Rate

### 1. **Increase Supervisor Capacities** ⭐ HIGHEST IMPACT

**What it does:** Allows supervisors to handle more students across all their topics.

**How to do it:**
- Edit `data/supervisors.txt`
- Increase capacity number (max 10)
- Example: Change `SUP01: 6, ...` to `SUP01: 10, ...`

**Example:**
```
# Before
SUP01: 6, BDBA:T01:Expert, BCSAI:T01:Advanced

# After  
SUP01: 10, BDBA:T01:Expert, BCSAI:T01:Advanced
```

**Impact:** ⭐⭐⭐⭐⭐ (Very High)

---

### 2. **Add More Supervisors** ⭐ HIGH IMPACT

**What it does:** Increases total capacity and coverage.

**How to do it:**
- Add new supervisor entries to `data/supervisors.txt`
- Assign them to topics that need more coverage
- Set appropriate capacity (1-10)

**Example:**
```
SUP41: 8, BDBA:T01:Expert, BCSAI:T02:Advanced, BBA+BDBA:T03:Intermediate
SUP42: 10, BDBA:T05:Expert, BDBA:T06:Advanced
```

**Impact:** ⭐⭐⭐⭐⭐ (Very High)

---

### 3. **Improve Supervisor Coverage** ⭐ HIGH IMPACT

**What it does:** Ensures all bachelor-topic combinations have supervisions available.

**How to do it:**
- Edit `data/supervisors.txt`
- Add bachelor-topic combinations for supervisors
- Format: `Bachelor:TopicID:ExpertiseLevel`
- No limit on number of combinations per supervisor

**Example:**
```
# Before (only covers BDBA students for T01)
SUP01: 8, BDBA:T01:Expert

# After (covers all bachelor programs for T01)
SUP01: 8, BDBA:T01:Expert, BCSAI:T01:Advanced, BBA+BDBA:T01:Intermediate
```

**Impact:** ⭐⭐⭐⭐ (High)

---

### 4. **Add More Topics** ⭐ MEDIUM IMPACT

**What it does:** Provides more options for students to choose from.

**How to do it:**
- Add new topics to `data/topics.txt`
- Format: `TopicID: Area`
- Assign supervisors to these topics

**Example:**
```
T66: Data Science
T67: Machine Learning  
T68: Computer Science
```

**Then assign supervisors:**
```
SUP01: 10, BDBA:T66:Expert, BCSAI:T66:Advanced
SUP02: 8, BDBA:T67:Expert, BBA+BDBA:T67:Intermediate
```

**Impact:** ⭐⭐⭐ (Medium - helps if topics are too concentrated)

---

### 5. **Encourage Diverse Student Preferences** ⭐ MEDIUM IMPACT

**What it does:** Spreads demand across more topics, reducing bottlenecks.

**How to do it:**
- Encourage students to explore different areas
- Provide information about less popular topics
- Highlight supervisor expertise in various areas

**Before (concentrated):**
```
BDBA001: T01, T02, T03, T04, T05
BDBA002: T01, T02, T03, T04, T06
BDBA003: T01, T02, T03, T05, T07
```

**After (diverse):**
```
BDBA001: T01, T10, T20, T30, T40
BDBA002: T02, T12, T22, T32, T42
BDBA003: T03, T13, T23, T33, T43
```

**Impact:** ⭐⭐⭐ (Medium)

---

### 6. **Run Multiple Rounds** ✅ AUTOMATIC

**What it does:** Gives unmatched students additional chances to match with remaining preferences.

**How it works:**
- Round 1: All students apply to their first preference
- Round 2+: Unmatched students continue with remaining preferences
- Automatically stops when all matched or no new matches

**This is already built into the algorithm!**

**Impact:** ⭐⭐⭐⭐ (High - automatic)

---

## Diagnostic Tools

### Use the Results & Analysis Page

After running the algorithm, check:

1. **Unmatched Students Section**
   - Shows exactly why each student couldn't be matched
   - Primary reasons for matching failures
   - Actionable recommendations

2. **Capacity Analysis**
   - Total supervisor capacity vs. students
   - Capacity gap warnings
   - Coverage analysis by bachelor program

3. **Popular Unmatched Topics**
   - Topics with many unmatched requests
   - Suggests where to add capacity

---

## Example Improvement Workflow

### Scenario: 70% Match Rate (30% unmatched)

**Step 1: Review Diagnostics**
```
- 60 students unmatched
- Primary reason: "All preferred supervisors at capacity"
- Popular unmatched topics: T01, T05, T12
```

**Step 2: Identify Root Cause**
- Supervisors for T01, T05, T12 are at capacity
- Need more capacity or supervisors for these topics

**Step 3: Take Action**
```
# Option A: Increase existing supervisor capacities
SUP01: 6 → SUP01: 10  (covers T01)
SUP05: 7 → SUP05: 10  (covers T05)

# Option B: Add new supervisors
SUP41: 10, BDBA:T01:Expert, BCSAI:T01:Advanced
SUP42: 8, BDBA:T05:Expert, BBA+BDBA:T05:Intermediate

# Option C: Add coverage for underrepresented bachelor programs
SUP10: 8, BDBA:T12:Expert → 
SUP10: 8, BDBA:T12:Expert, BCSAI:T12:Advanced, BBA+BDBA:T12:Intermediate
```

**Step 4: Re-run Algorithm**
- Expected: Match rate increases to 85-95%

---

## Quick Checklist

Before running the algorithm, verify:

- [ ] Total supervisor capacity ≥ total students
- [ ] Popular topics have sufficient supervisor capacity
- [ ] All bachelor-topic combinations have supervisor coverage
- [ ] Students have exactly 5 preferences
- [ ] Supervisors have capacity ≤ 10
- [ ] No supervisor capacity is significantly underutilized

---

## Understanding Match Rate Benchmarks

- **90-100%**: Excellent - Almost all students matched
- **70-89%**: Good - Most students matched, minor adjustments needed
- **50-69%**: Fair - Significant capacity or coverage issues
- **<50%**: Poor - Major structural problems

---

## Common Issues and Solutions

### Issue: "No supervisor available for bachelor-topic combination"

**Solution:** Add supervisors who can supervise these combinations
```
# If BCSAI students can't match to T10
SUP01: 8, BCSAI:T10:Expert
```

### Issue: "All preferred supervisors at capacity"

**Solutions:**
1. Increase supervisor capacities (max 10)
2. Add more supervisors for these topics
3. Encourage students to diversify preferences

### Issue: Low utilization of some topics

**Solution:** 
1. Review if topics are unpopular
2. Consider removing underutilized topics
3. Reallocate supervisor capacity to popular topics

---

## Advanced Tip: Balancing Capacity

Calculate total capacity needed:
```
Total Students: 200
Buffer (10%): +20
Target Capacity: 220

Current Capacity: Sum of all supervisor capacities
Gap: Target - Current

If Gap > 0: Need to add capacity
```

---

## Summary

**Top 3 Actions for Immediate Impact:**

1. ⭐ **Increase supervisor capacities** to max 10
2. ⭐ **Add supervisor coverage** for all bachelor-topic combinations
3. ⭐ **Add new supervisors** for popular topics with high demand

Remember: Topics have **no capacity limit**. Focus all efforts on supervisor capacity and coverage!
