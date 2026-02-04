---
description: "Diagnose memory issues - analyze memory usage, leaks, and growth"
argument-hint: "<pid>"
---

# Memory Diagnostics

You are diagnosing **memory issues** for a Python process using PyFlightProfiler.

## Input
- **PID**: $ARGUMENTS

## Prerequisites

Ensure PyFlightProfiler is installed:
```bash
pip show flight-profiler || pip install flight-profiler
```

## Diagnostic Steps

### Step 1: Get Memory Summary

```bash
flight_profiler <pid> --cmd "mem summary --limit 20 --order descending"
```

**Analyze**: Which types consume most memory? Any unexpected types?

### Step 2: Memory Diff (if needed)

```bash
flight_profiler <pid> --cmd "mem diff --interval 30 --limit 20 --order descending"
```

**Analyze**: Types with positive growth = potential leak sources.

### Step 3: Force GC and Re-check

```bash
flight_profiler <pid> --cmd "vmtool -a forceGc"
flight_profiler <pid> --cmd "mem summary --limit 20 --order descending"
```

**Analyze**: Memory drops → delayed GC. No change → true leak.

### Step 4: Inspect Suspicious Classes (optional)

```bash
flight_profiler <pid> --cmd "vmtool -a getInstances -c <module> <ClassName> -n 5 -x 2"
```

## Output Report

```markdown
## Memory Diagnosis Report

### Summary
[One sentence summary]

### Memory Profile
- Top consumers:
  1. [Type]: [size/count]
  2. [Type]: [size/count]

### Findings
[Key observations]

### Recommendations
1. [Actionable fix]
```

## Commands Reference

- `mem summary`: Memory usage by type
- `mem diff --interval N`: Compare memory before/after N seconds
- `vmtool -a forceGc`: Force garbage collection
- `vmtool -a getInstances -c module class`: Get class instances
