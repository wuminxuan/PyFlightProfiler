---
description: "Diagnose performance issues - slow response, high latency, CPU bottlenecks"
argument-hint: "<pid> [method location]"
---

# Performance Diagnostics Workflow

You are diagnosing a **performance issue** (slow response, high latency, CPU bottleneck).

## Input
- **PID**: $ARGUMENTS (first argument)
- **Method Location** (optional): Module/class/method to focus on

## Diagnostic Strategy

Performance issues typically fall into these categories:
1. **CPU-bound**: Hot methods consuming excessive CPU
2. **GIL contention**: Threads waiting for Python GIL
3. **I/O blocking**: Waiting on network/disk operations
4. **Inefficient algorithms**: Methods with high call counts or long execution

## Step-by-Step Diagnosis

### Phase 1: Get Overview with Flame Graph

First, sample the process to identify CPU hotspots:

```bash
flight_profiler <pid> --cmd "perf -d 10 -f /tmp/flamegraph.svg"
```

**Analyze the flame graph**:
- Wide bars = methods consuming most CPU time
- Deep stacks = complex call chains
- Look for unexpected methods taking time

### Phase 2: Check GIL Contention

If multiple threads exist, check GIL status:

```bash
flight_profiler <pid> --cmd "gilstat on"
```

Wait 5-10 seconds for statistics, then:
```bash
flight_profiler <pid> --cmd "gilstat off"
```

**Key metrics to analyze**:
- `holdavg`: High values (>5ms) indicate threads holding GIL too long
- `takeavg`: High values indicate threads waiting too long for GIL
- Compare `takecnt` across threads for imbalance

### Phase 3: Trace Suspicious Methods

If a specific method is identified (from flame graph or user input):

```bash
flight_profiler <pid> --cmd "trace <module> [class] <method> -i 1 -n 5"
```

**Analyze the trace output**:
- Look for internal methods taking disproportionate time
- Identify unexpected nested calls
- Check for methods called repeatedly

### Phase 4: Watch Method Details

For deeper inspection of a slow method:

```bash
flight_profiler <pid> --cmd "watch <module> [class] <method> --expr return_obj,cost -n 5"
```

**Check for**:
- Correlation between input size and execution time
- Specific inputs causing slowness
- Return values indicating errors or retries

### Phase 5: Check Thread Stacks (if still unclear)

Get current thread states:

```bash
flight_profiler <pid> --cmd "stack"
```

**Look for**:
- Threads stuck in the same location
- I/O wait patterns
- Lock acquisition patterns

## Common Performance Patterns

### Pattern: GIL Bottleneck
**Symptoms**: Multiple threads, high `takeavg` in gilstat
**Solution**: Consider multiprocessing, release GIL in C extensions, or reduce thread count

### Pattern: Hot Loop
**Symptoms**: Single method dominates flame graph with many self-time
**Solution**: Optimize algorithm, add caching, or use vectorized operations

### Pattern: Repeated Database/Network Calls
**Symptoms**: Trace shows many small calls to I/O methods
**Solution**: Batch operations, add connection pooling, implement caching

### Pattern: Serialization Overhead
**Symptoms**: JSON/pickle methods in hot path
**Solution**: Use faster serializers (msgpack, orjson), reduce data size

## Report Template

After completing diagnosis, provide:

```markdown
## Performance Diagnosis Report

### Problem Summary
[e.g., "API response time increased from 50ms to 2s due to GIL contention"]

### Evidence Chain
1. `perf` → [Top CPU consumers identified]
2. `gilstat` → [GIL metrics summary]
3. `trace` → [Specific bottleneck location]

### Root Cause
[Detailed explanation of why performance degraded]

### Recommendations
1. [Primary fix with expected impact]
2. [Alternative approaches]
3. [Monitoring suggestions]
```

## Execution Notes

- Start with `perf` for broad overview
- Use `gilstat` if multi-threaded
- Drill down with `trace` once you have a target
- Keep `-n` values low (5-10) to avoid output overload
