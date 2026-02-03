---
description: "Diagnose memory issues - leaks, OOM, high memory usage"
argument-hint: "<pid>"
---

# Memory Diagnostics Workflow

You are diagnosing a **memory issue** (memory leak, OOM, high memory usage, memory growth).

## Input
- **PID**: $ARGUMENTS

## Diagnostic Strategy

Memory issues typically fall into these categories:
1. **Memory leak**: Objects not being garbage collected
2. **Large object accumulation**: Growing collections (lists, dicts, caches)
3. **Reference cycles**: Objects preventing GC
4. **External library leaks**: C extensions not releasing memory

## Step-by-Step Diagnosis

### Phase 1: Get Memory Summary

First, get an overview of memory usage by type:

```bash
flight_profiler <pid> --cmd "mem summary --limit 20 --order descending"
```

**Analyze the output**:
- Which types consume most memory?
- Are there unexpected types with high counts?
- Look for custom classes with large instance counts

### Phase 2: Memory Diff Over Time

Capture memory changes over a time interval:

```bash
flight_profiler <pid> --cmd "mem diff --interval 30 --limit 20 --order descending"
```

**Key indicators**:
- Types with positive growth = potential leak sources
- Large growth in basic types (dict, list) = accumulating data
- Growth in custom classes = business logic leak

### Phase 3: Force Garbage Collection

Trigger GC to see if memory is reclaimable:

```bash
flight_profiler <pid> --cmd "vmtool -a forceGc"
```

Then re-run memory summary:
```bash
flight_profiler <pid> --cmd "mem summary --limit 20 --order descending"
```

**Compare results**:
- Significant drop after GC = delayed collection, not a leak
- No change after GC = true leak or intentional retention

### Phase 4: Inspect Specific Class Instances

For suspicious classes identified in previous steps:

```bash
flight_profiler <pid> --cmd "vmtool -a getInstances -c <module> <ClassName> -n 10 -x 2"
```

**Examine instances**:
- What data do they hold?
- Why might they not be collected?
- Are there obvious reference chains?

### Phase 5: Check Global Variables

Large global collections can cause memory issues:

```bash
flight_profiler <pid> --cmd "getglobal <module> <variable_name> -x 2"
```

**Look for**:
- Growing caches without eviction
- Event listeners accumulating
- Thread-local storage buildup

### Phase 6: Watch Memory-Related Methods

If you suspect a specific method is leaking:

```bash
flight_profiler <pid> --cmd "watch <module> [class] <method> --expr return_obj -n 5 -x 2"
```

## Common Memory Patterns

### Pattern: Cache Without Bounds
**Symptoms**: dict or list growing continuously in `mem diff`
**Solution**: Add LRU eviction, TTL expiry, or size limits

### Pattern: Event Listener Leak
**Symptoms**: Callback/handler objects accumulating
**Solution**: Properly unsubscribe, use weak references

### Pattern: Circular Reference
**Symptoms**: Custom objects not collected even after GC
**Solution**: Break cycles, implement `__del__` carefully, use weakref

### Pattern: Large DataFrame/Tensor Retention
**Symptoms**: numpy.ndarray or torch.Tensor high in memory summary
**Solution**: Explicitly delete, use context managers, process in chunks

### Pattern: Thread-Local Accumulation
**Symptoms**: Memory grows with thread count/requests
**Solution**: Clean up thread-local storage after use

## Report Template

After completing diagnosis, provide:

```markdown
## Memory Diagnosis Report

### Problem Summary
[e.g., "Memory leak caused by unbounded cache in UserSessionManager"]

### Memory Profile
- Total tracked objects: [count]
- Top memory consumers:
  1. [Type]: [size/count]
  2. [Type]: [size/count]

### Growth Analysis
- Objects growing: [list of types with growth rate]
- GC effectiveness: [reclaimable vs retained]

### Root Cause
[Detailed explanation of why memory is not being released]

### Recommendations
1. [Primary fix - e.g., "Add cache eviction policy"]
2. [Monitoring - e.g., "Add memory alerts at 80% threshold"]
3. [Prevention - e.g., "Code review checklist for memory management"]
```

## Execution Notes

- Always start with `mem summary` for baseline
- Use `mem diff` to identify growing objects
- `forceGc` helps distinguish leaks from delayed collection
- `vmtool getInstances` for deep inspection of specific types
- Keep sampling intervals reasonable (30-60s) to see meaningful changes
