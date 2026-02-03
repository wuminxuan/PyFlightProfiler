# PyFlightProfiler - AI-Powered Python Diagnostics

PyFlightProfiler is a non-intrusive diagnostic toolbox for Python applications. This plugin provides AI-powered troubleshooting capabilities.

## Prerequisites

Before running any diagnosis, ensure PyFlightProfiler is installed:
```bash
pip show flight-profiler || pip install flight-profiler
```

## How to Execute Commands

All PyFlightProfiler commands are executed via:
```bash
flight_profiler <pid> --cmd "<command>"
```

For example:
```bash
flight_profiler 12345 --cmd "stack"
flight_profiler 12345 --cmd "watch __main__ func -x 2"
```

## Available Commands Reference

### 1. watch - Method Execution Observation
Observe method input, output, and execution time.

```
watch module [class] method [options]

Options:
  --expr <value>     Expression to observe (default: args,kwargs)
  -x, --expand       Object tree expand level (default: 1, max: 4)
  -e, --exception    Only record when method throws exception
  -n, --limits       Max display count (default: 10)
  -f, --filter       Filter expression, e.g., args[0]=='hello'
  -r, --raw          Display raw string representation
  -v, --verbose      Display all nested items

Examples:
  watch __main__ func -x 2
  watch __main__ func -f "args[0]['query']=='hello'"
  watch __main__ ClassA func --expr return_obj,cost
```

### 2. trace - Method Call Path Tracing
Trace method execution time and internal call chain.

```
trace module [class] method [options]

Options:
  -i, --interval     Display calls with cost > interval ms (default: 0.1)
  -et, --entrance_time  Filter by total execution time
  -d, --depth        Limit call stack depth
  -n, --limits       Max trace count (default: 10)
  -f, --filter       Filter expression

Examples:
  trace __main__ func
  trace __main__ func -i 1
  trace __main__ ClassA func -et 30
```

### 3. stack - Thread Stack Analysis
Display Python stack frames for all threads.

```
stack [pid] [options]

Options:
  -f, --filepath     Export stack to file
  --native           Include native stack (Linux only)

Examples:
  stack
  stack --native
  stack -f ./stack.log
```

### 4. perf - Performance Flame Graph
Generate flame graph for CPU hotspot analysis.

```
perf [pid] [options]

Options:
  -f, --filepath     Output file (default: flamegraph.svg)
  -r, --rate         Samples per second (default: 100)
  -d, --duration     Duration in seconds

Examples:
  perf
  perf -d 30 -f ~/flamegraph.svg
```

### 5. mem - Memory Analysis
Analyze memory usage by type.

```
mem summary [options]
mem diff [options]

Options:
  --limit            Number of top items to display
  --order            Sort order: descending/ascending
  --interval         Diff interval in seconds (for diff)

Examples:
  mem summary --limit 100
  mem diff --interval 10 --limit 50
```

### 6. gilstat - GIL Lock Analysis
Monitor Global Interpreter Lock status.

```
gilstat on [take_threshold] [hold_threshold]

Examples:
  gilstat on              # Basic GIL statistics every 5s
  gilstat on 5 5          # Alert when take/hold > 5ms
  gilstat off             # Stop monitoring
```

### 7. tt (timetunnel) - Cross-Time Method Observation
Record and replay method calls over time.

```
tt -t module [class] method [options]  # Start recording
tt -l                                   # List recorded calls
tt -i <index>                          # View call details
tt -i <index> -p                       # Replay call

Options:
  -n, --limits       Max records (default: 50)
  -f, --filter       Filter expression
  -x, --expand       Expand level for details

Examples:
  tt -t __main__ func
  tt -l
  tt -i 1000 -x 3
  tt -i 1000 -p
```

### 8. getglobal - Global Variable Inspection
View module global variables and class static variables.

```
getglobal module [class] field [options]

Options:
  -e, --expr         Expression to observe
  -x, --expand       Expand level
  -r, --raw          Raw string output

Examples:
  getglobal __main__ g_list
  getglobal __main__ ClassA static_field -x 2
```

### 9. vmtool - Class Instance Management
Get and inspect live class instances.

```
vmtool -a getInstances -c module class [options]
vmtool -a forceGc

Options:
  -e, --expr         Expression for instances
  -n, --limits       Max instances (default: 10)
  -x, --expand       Expand level

Examples:
  vmtool -a getInstances -c __main__ MyClass
  vmtool -a getInstances -c __main__ MyClass -e instances[0].field
  vmtool -a forceGc
```

### 10. torch - PyTorch Profiling
Profile PyTorch function execution and GPU memory.

```
torch profile module [class] method [options]
torch memory -s                              # Snapshot
torch memory -r module [class] method        # Record allocation

Options:
  -f, --filepath     Output file

Examples:
  torch profile __main__ Model forward
  torch memory -s -f ~/snapshot.pickle
  torch memory -r __main__ Model forward
```

### 11. module - Locate Module by Filepath
Find the module name for a given file path.

```
module <filepath>

Examples:
  module /home/admin/app/compute.py
```

### 12. console - Interactive Console
Launch an interactive Python console in the target process.

```
console
```

## Method Location Format

PyFlightProfiler uses `module [class] method` format:
- `module`: Import path (e.g., `__main__`, `pkg_a.pkg_b`)
- `class`: Optional, only for class methods
- `method`: Function/method name

Use the `module` command to find the correct module name if unsure.

## Diagnostic Commands

Use `/diagnose` to start AI-powered diagnostics:
- `/diagnose <pid> <problem description>` - Auto-route to appropriate diagnostic
- `/diagnose-slow` - Performance/latency issues
- `/diagnose-memory` - Memory leaks/growth
- `/diagnose-hang` - Process hang/deadlock
- `/diagnose-exception` - Exception analysis
- `/diagnose-torch` - PyTorch specific issues
