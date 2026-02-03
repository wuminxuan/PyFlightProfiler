---
description: "Diagnose hang/deadlock issues - process stuck, no response, blocked threads"
argument-hint: "<pid>"
---

# Hang/Deadlock Diagnostics Workflow

You are diagnosing a **hang or deadlock issue** (process stuck, not responding, threads blocked).

## Input
- **PID**: $ARGUMENTS

## Diagnostic Strategy

Hang issues typically fall into these categories:
1. **Deadlock**: Two or more threads waiting for each other
2. **GIL starvation**: One thread holding GIL indefinitely
3. **I/O blocking**: Waiting on network/disk that never completes
4. **Infinite loop**: Code stuck in a loop without exit condition
5. **External dependency**: Waiting on external service that's down

## Step-by-Step Diagnosis

### Phase 1: Get Thread Stack Snapshot

**CRITICAL FIRST STEP** - Capture current state of all threads:

```bash
flight_profiler <pid> --cmd "stack"
```

**Analyze the stacks**:
- Are multiple threads waiting on the same lock?
- Is there a circular wait pattern?
- Which threads are active vs blocked?
- What are the topmost frames doing?

### Phase 2: Get Native Stack (Linux only)

For deeper insight including C-level blocking:

```bash
flight_profiler <pid> --cmd "stack --native"
```

**Look for**:
- System calls like `futex`, `poll`, `recv` indicating waits
- Mutex/lock acquisition in native code
- I/O operations at the system level

### Phase 3: Check GIL Status

GIL issues often cause apparent hangs:

```bash
flight_profiler <pid> --cmd "gilstat on 5 5"
```

Wait 10-15 seconds, then:
```bash
flight_profiler <pid> --cmd "gilstat off"
```

**Key indicators**:
- Very high `hold_all` on one thread = GIL hog
- Long `takeavg` times = severe contention
- One thread with many `takecnt`, others with zero = starvation

### Phase 4: Take Multiple Stack Snapshots

If the hang is intermittent, take multiple snapshots:

```bash
# First snapshot
flight_profiler <pid> --cmd "stack"

# Wait 5-10 seconds, take another
flight_profiler <pid> --cmd "stack"
```

**Compare snapshots**:
- Same stacks in both = confirmed hang/deadlock
- Different stacks = slow execution, not hang
- Some threads same, some different = partial deadlock

### Phase 5: Identify Blocking Resources

If stacks show lock waits, identify the lock holder:

Look for patterns in stack traces:
- `threading.Lock.acquire` / `threading.RLock.acquire`
- `queue.Queue.get` / `queue.Queue.put`
- `multiprocessing` synchronization primitives
- Database connection pool waits
- HTTP client timeouts

### Phase 6: Check for Infinite Loops

If a thread appears stuck in user code (not a wait):

```bash
flight_profiler <pid> --cmd "trace <module> <method> -d 3 -n 1"
```

If the method never returns, it's likely an infinite loop.

## Common Hang Patterns

### Pattern: Classic Deadlock
**Symptoms**: Two threads, each holding a lock the other needs
**Stack signature**: Thread A waiting on Lock B, Thread B waiting on Lock A
**Solution**: Acquire locks in consistent order, use timeout on lock acquisition

### Pattern: GIL Starvation
**Symptoms**: One thread runs continuously, others never get GIL
**Stack signature**: Worker threads stuck at GIL acquisition, one thread in CPU loop
**Solution**: Add `time.sleep(0)` in hot loops, use multiprocessing

### Pattern: Database Connection Pool Exhausted
**Symptoms**: All threads waiting for database connection
**Stack signature**: Multiple threads in connection pool `get()` or `acquire()`
**Solution**: Increase pool size, add connection timeouts, fix connection leaks

### Pattern: HTTP Client Timeout Missing
**Symptoms**: Thread stuck in `requests.get()` or similar
**Stack signature**: Thread in `socket.recv` or `select.select`
**Solution**: Always set timeouts on HTTP requests

### Pattern: Blocking Queue Without Timeout
**Symptoms**: Thread waiting on `queue.get()` forever
**Stack signature**: Thread in `Queue.get` with no producer
**Solution**: Use `queue.get(timeout=N)`, check queue before waiting

### Pattern: Subprocess Pipe Deadlock
**Symptoms**: Thread stuck in `subprocess.communicate()`
**Stack signature**: Thread in `_communicate` or `wait`
**Solution**: Use `communicate()` instead of manual pipe reading

## Report Template

After completing diagnosis, provide:

```markdown
## Hang/Deadlock Diagnosis Report

### Problem Summary
[e.g., "Classic deadlock between DatabaseConnection and CacheManager locks"]

### Thread State Summary
| Thread | State | Location | Waiting For |
|--------|-------|----------|-------------|
| MainThread | Blocked | Lock.acquire | CacheLock |
| Worker-1 | Blocked | Lock.acquire | DBLock |
| ... | ... | ... | ... |

### Evidence
1. Stack snapshot shows: [key observation]
2. GIL stats show: [key metrics]
3. Repeated snapshots confirm: [pattern]

### Root Cause
[Detailed explanation of the deadlock/hang mechanism]

### Recommendations
1. [Immediate fix - e.g., "Restart process, then apply code fix"]
2. [Code fix - e.g., "Change lock acquisition order in X and Y"]
3. [Prevention - e.g., "Add lock timeout, implement deadlock detection"]
```

## Execution Notes

- **Stack is your most important tool** - always start there
- Take multiple snapshots to confirm hang vs slow execution
- `gilstat` helps identify GIL-related hangs
- Native stacks reveal system-level blocking
- Compare thread states to identify circular waits
