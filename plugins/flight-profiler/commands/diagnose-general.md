---
description: "General diagnostics for unclear or mixed issues"
argument-hint: "<pid> [problem description]"
---

# General Diagnostics Workflow

You are diagnosing an **unclear or mixed issue** that doesn't clearly fit into performance, memory, hang, exception, or PyTorch categories.

## Input
- **PID**: First argument from $ARGUMENTS
- **Problem Description**: Remaining arguments describing the issue

## Diagnostic Strategy

For unclear issues, use a systematic exploration approach:
1. Start broad with thread stacks
2. Narrow down based on observations
3. Apply specialized diagnostics as patterns emerge

## Step-by-Step Diagnosis

### Phase 1: Get Process Overview with Thread Stacks

Always start with thread stacks to understand what the process is doing:

```bash
flight_profiler <pid> --cmd "stack"
```

**Analyze the output**:
- How many threads exist?
- What are they doing (I/O, computation, waiting)?
- Any obvious issues visible in stacks?

### Phase 2: Quick Performance Sample

Get a 10-second performance sample:

```bash
flight_profiler <pid> --cmd "perf -d 10 -f /tmp/overview.svg"
```

**Review the flame graph**:
- Where is CPU time being spent?
- Are there unexpected hot spots?
- What's the call structure?

### Phase 3: Memory Overview

Get a quick memory summary:

```bash
flight_profiler <pid> --cmd "mem summary --limit 15"
```

**Check for**:
- Any type with unusually high count or size?
- Custom classes with many instances?
- Large collections (list, dict)?

### Phase 4: GIL Status Check

For multi-threaded processes, check GIL:

```bash
flight_profiler <pid> --cmd "gilstat on"
```

Wait 5 seconds, then:
```bash
flight_profiler <pid> --cmd "gilstat off"
```

**Look for**:
- Thread imbalance in GIL acquisition
- High hold times
- High wait times

### Phase 5: Identify and Investigate Suspicious Areas

Based on the overview, pick the most suspicious area and investigate deeper.

**If CPU-bound (from perf)**:
```bash
flight_profiler <pid> --cmd "trace <hot_module> <hot_method> -i 1 -n 5"
```

**If memory-related (from mem summary)**:
```bash
flight_profiler <pid> --cmd "vmtool -a getInstances -c <module> <class> -n 5 -x 2"
```

**If thread-related (from stack/gilstat)**:
```bash
flight_profiler <pid> --cmd "stack --native"
```

### Phase 6: Watch Suspicious Methods

If a specific method is identified:

```bash
flight_profiler <pid> --cmd "watch <module> [class] <method> -n 5 -x 2"
```

### Phase 7: Interactive Exploration (Advanced)

For complex issues, use the interactive console:

```bash
flight_profiler <pid> --cmd "console"
```

This allows custom inspection code to be executed in the target process.

## Decision Tree

```
Start: Get thread stacks
  │
  ├─ Threads stuck/waiting → Go to /diagnose-hang workflow
  │
  ├─ Threads actively running → Check perf
  │     │
  │     ├─ CPU hotspots found → Go to /diagnose-slow workflow
  │     │
  │     └─ No clear hotspots → Check memory
  │           │
  │           ├─ Memory issues → Go to /diagnose-memory workflow
  │           │
  │           └─ Memory normal → Check GIL
  │                 │
  │                 ├─ GIL contention → Go to /diagnose-slow workflow
  │                 │
  │                 └─ Normal → Continue general exploration
  │
  └─ Exception in stack → Go to /diagnose-exception workflow
```

## Comprehensive Data Collection

If the issue remains unclear, collect comprehensive data:

```bash
# 1. Full thread dump
flight_profiler <pid> --cmd "stack -f /tmp/stacks.txt"

# 2. Performance sample
flight_profiler <pid> --cmd "perf -d 30 -f /tmp/perf.svg"

# 3. Memory snapshot
flight_profiler <pid> --cmd "mem summary --limit 50 --order descending" > /tmp/mem.txt

# 4. GIL stats
# Run gilstat on, wait 30s, run gilstat off, capture output
```

## Questions to Ask User

If diagnosis is unclear, gather more information:

1. **When did the issue start?** (after deployment, load increase, etc.)
2. **What changed recently?** (code, config, dependencies)
3. **Is it reproducible?** (always, sometimes, specific conditions)
4. **What's the impact?** (slow, errors, crashes, resource exhaustion)
5. **What monitoring shows?** (CPU, memory, network metrics)

## Report Template

After completing diagnosis, provide:

```markdown
## General Diagnosis Report

### Problem Summary
[Best understanding of the issue based on exploration]

### Process Overview
- **Thread count**: [N]
- **CPU usage pattern**: [description]
- **Memory profile**: [summary]
- **GIL behavior**: [summary]

### Observations
1. Stack analysis: [findings]
2. Performance sample: [findings]
3. Memory check: [findings]
4. GIL status: [findings]

### Hypothesis
[Based on evidence, what's the most likely cause?]

### Recommended Next Steps
1. [Further investigation needed - which specialized diagnostic?]
2. [Data to collect]
3. [Questions for the user]

### If Cause Identified
- **Root Cause**: [explanation]
- **Recommendations**: [fixes]
```

## Execution Notes

- Always start with `stack` - it's the most informative single command
- Use the decision tree to route to specialized diagnostics
- When stuck, collect comprehensive data and analyze patterns
- Interactive console is powerful but use with caution
- Ask clarifying questions if the problem description is vague
