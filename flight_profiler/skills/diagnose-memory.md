---
description: "Diagnose memory issues - analyze memory usage, leaks, and growth"
argument-hint: "<pid>"
---

# Memory Diagnostics

You are diagnosing **memory issues** for a Python process using PyFlightProfiler.

## Input
- **PID**: $ARGUMENTS

## Diagnostic Steps

### Step 1: Get Memory Summary

```bash
flight_profiler <pid> --cmd "mem summary --limit 20 --order descending"
```

**Analyze**: Which types consume most memory?

### Step 2: Memory Diff (find growing objects)

```bash
flight_profiler <pid> --cmd "mem diff --interval 30 --limit 20 --order descending"
```

**Analyze**: Types with positive growth = potential leak.

### Step 3: Force GC and Re-check

```bash
flight_profiler <pid> --cmd "mem summary --limit 20 --order descending"
```

**Analyze**: Memory drops → delayed GC. No change → true leak.


## Output Report

```markdown
## Memory Diagnosis Report

### Summary
[One sentence summary]

### Memory Profile
| Type | Size/Count |
|------|------------|
| ... | ... |

### Findings
[Key observations]

### Recommendations
1. [Actionable fix]
```
