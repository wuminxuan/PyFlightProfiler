---
description: "Diagnose exception issues - errors, crashes, unexpected behavior"
argument-hint: "<pid> <module> [class] <method>"
---

# Exception Diagnostics Workflow

You are diagnosing an **exception or error issue** (crashes, errors, unexpected behavior).

## Input
- **PID**: First argument from $ARGUMENTS
- **Method Location**: Module [class] method where exception occurs (if known)

## Diagnostic Strategy

Exception issues typically fall into these categories:
1. **Uncaught exception**: Exception propagating without handler
2. **Silent failure**: Exception caught but not properly handled
3. **Intermittent error**: Exception occurring under specific conditions
4. **Data-dependent error**: Exception caused by specific input values

## Step-by-Step Diagnosis

### Phase 1: Watch Method for Exceptions

If the problematic method is known, watch for exceptions:

```bash
flight_profiler <pid> --cmd "watch <module> [class] <method> -e -n 10 -x 2"
```

The `-e` flag captures only exception-throwing invocations.

**Analyze output**:
- Exception type and message
- Input arguments that triggered the exception
- Execution context (self/target state)

### Phase 2: Trace the Call Path

Get the full call chain leading to the exception:

```bash
flight_profiler <pid> --cmd "trace <module> [class] <method> -n 5"
```

**Look for**:
- Which internal call is failing?
- What's the execution flow before failure?
- Are there unexpected code paths?

### Phase 3: Record with Time Tunnel

For intermittent exceptions, record calls over time:

```bash
flight_profiler <pid> --cmd "tt -t <module> [class] <method> -n 50"
```

After some exceptions occur, list them:
```bash
flight_profiler <pid> --cmd "tt -l"
```

Inspect specific failures:
```bash
flight_profiler <pid> --cmd "tt -i <index> -x 3"
```

### Phase 4: Compare Success vs Failure

Record multiple calls, then compare:

```bash
# Look at a successful call
flight_profiler <pid> --cmd "tt -i <success_index> -x 3"

# Look at a failed call
flight_profiler <pid> --cmd "tt -i <failure_index> -x 3"
```

**Identify**:
- What's different in the inputs?
- Are there state differences?
- Environmental factors?

### Phase 5: Check Global State

If exception depends on global state:

```bash
flight_profiler <pid> --cmd "getglobal <module> <variable> -x 2"
```

**Look for**:
- Uninitialized variables
- Stale configuration
- Resource exhaustion (connections, file handles)

### Phase 6: Inspect Class Instances

If exception relates to object state:

```bash
flight_profiler <pid> --cmd "vmtool -a getInstances -c <module> <class> -n 5 -x 2"
```

**Check for**:
- Corrupted object state
- Missing required attributes
- Invalid internal values

### Phase 7: Filter by Condition

If you have a hypothesis about what causes the exception:

```bash
flight_profiler <pid> --cmd "watch <module> [class] <method> -f \"args[0] is None\" -n 10"
```

Or filter for specific return values:
```bash
flight_profiler <pid> --cmd "watch <module> [class] <method> -f \"return_obj is None\" -n 10"
```

## Common Exception Patterns

### Pattern: NoneType Error
**Symptoms**: `AttributeError: 'NoneType' object has no attribute 'X'`
**Diagnosis**: Watch with filter `-f "return_obj is None"` on suspected method
**Solution**: Add null checks, investigate why None is returned

### Pattern: Key/Index Error
**Symptoms**: `KeyError` or `IndexError`
**Diagnosis**: Watch the method with `-x 3` to see full data structure
**Solution**: Add bounds checking, handle missing keys gracefully

### Pattern: Type Mismatch
**Symptoms**: `TypeError: expected X but got Y`
**Diagnosis**: Watch method inputs, check what's being passed
**Solution**: Add type validation, fix caller

### Pattern: Resource Exhaustion
**Symptoms**: Connection errors, file handle errors
**Diagnosis**: Check global state for pool/connection objects
**Solution**: Proper resource cleanup, increase limits, add pooling

### Pattern: Race Condition Error
**Symptoms**: Intermittent exceptions, hard to reproduce
**Diagnosis**: Use time tunnel to capture many calls, compare timings
**Solution**: Add proper synchronization, review threading logic

### Pattern: External Service Error
**Symptoms**: Network/API related exceptions
**Diagnosis**: Watch the calling method, check return values
**Solution**: Add retry logic, circuit breaker, proper error handling

## Report Template

After completing diagnosis, provide:

```markdown
## Exception Diagnosis Report

### Problem Summary
[e.g., "NullPointerException in UserService.getProfile() due to missing cache entry"]

### Exception Details
- **Type**: [Exception class]
- **Message**: [Error message]
- **Location**: [File:line or module.class.method]

### Triggering Conditions
- **Input pattern**: [What inputs cause this?]
- **Frequency**: [How often does it occur?]
- **Reproducibility**: [Always/Sometimes/Rare]

### Evidence Chain
1. `watch -e` captured: [exception details]
2. `trace` showed: [call path]
3. `tt` comparison: [success vs failure difference]

### Root Cause
[Detailed explanation of why the exception occurs]

### Recommendations
1. [Immediate fix - e.g., "Add null check before access"]
2. [Defensive coding - e.g., "Validate input at entry point"]
3. [Testing - e.g., "Add unit test for edge case"]
```

## Execution Notes

- Use `-e` flag with `watch` to capture only exceptions
- Time tunnel (`tt`) is excellent for intermittent issues
- Compare successful and failed calls to find the difference
- Filter expressions help narrow down trigger conditions
- Check both inputs (`args`) and state (`target`) for clues
