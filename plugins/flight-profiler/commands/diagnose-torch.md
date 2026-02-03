---
description: "Diagnose PyTorch issues - GPU memory, CUDA errors, model performance"
argument-hint: "<pid> <module> [class] <method>"
---

# PyTorch Diagnostics Workflow

You are diagnosing a **PyTorch-related issue** (GPU memory, CUDA errors, model inference/training performance).

## Input
- **PID**: First argument from $ARGUMENTS
- **Method Location**: Module [class] method to profile (optional)

## Diagnostic Strategy

PyTorch issues typically fall into these categories:
1. **GPU memory leak**: VRAM growing without release
2. **CUDA OOM**: Out of memory on GPU
3. **Slow inference**: Model forward pass taking too long
4. **Slow training**: Training loop performance issues
5. **CPU-GPU transfer bottleneck**: Data movement overhead

## Step-by-Step Diagnosis

### Phase 1: GPU Memory Snapshot

First, capture current GPU memory state:

```bash
flight_profiler <pid> --cmd "torch memory -s -f /tmp/snapshot.pickle"
```

**Analyze with PyTorch Memory Viz**:
1. Open https://pytorch.org/memory_viz
2. Upload the snapshot.pickle file
3. Look for:
   - Large allocations
   - Fragmentation
   - Unexpected tensor retention

### Phase 2: Profile Method Execution

Profile a specific method (e.g., model forward pass):

```bash
flight_profiler <pid> --cmd "torch profile <module> [class] <method> -f /tmp/trace.json"
```

**Analyze the trace**:
1. Open `chrome://tracing` in Chrome browser
2. Load the trace.json file
3. Look for:
   - Which operations take most time?
   - CPU vs GPU time breakdown
   - Kernel launch overhead
   - Data transfer operations

### Phase 3: Record Memory Allocation During Execution

Track memory allocation during method execution:

```bash
flight_profiler <pid> --cmd "torch memory -r <module> [class] <method> -f /tmp/mem_trace.pickle"
```

**Analyze allocation pattern**:
1. Upload to PyTorch Memory Viz
2. Check allocation timeline
3. Look for:
   - Memory spikes during operation
   - Allocations not being freed
   - Fragmentation patterns

### Phase 4: Watch Method Performance

Monitor method execution characteristics:

```bash
flight_profiler <pid> --cmd "watch <module> [class] <method> --expr cost,return_obj -n 10"
```

**Look for**:
- Execution time consistency
- Return value sizes
- Correlation between input and execution time

### Phase 5: Trace Internal Calls

Get detailed breakdown of PyTorch operations:

```bash
flight_profiler <pid> --cmd "trace <module> [class] <method> -i 0.5 -n 5"
```

**Identify**:
- Which sub-operations are slow?
- Are there unexpected synchronization points?
- Data movement overhead

### Phase 6: Check for Memory Leaks

Run memory analysis over time:

```bash
# First snapshot
flight_profiler <pid> --cmd "torch memory -s -f /tmp/snap1.pickle"

# Trigger some operations, then take another
flight_profiler <pid> --cmd "torch memory -s -f /tmp/snap2.pickle"
```

Compare snapshots to identify growing allocations.

## Common PyTorch Patterns

### Pattern: GPU Memory Leak
**Symptoms**: VRAM grows over time, eventually OOM
**Diagnosis**: Compare memory snapshots, look for growing tensors
**Solution**: 
- Ensure tensors are deleted or go out of scope
- Use `torch.no_grad()` for inference
- Clear intermediate results with `del`
- Call `torch.cuda.empty_cache()` periodically

### Pattern: Gradient Accumulation Leak
**Symptoms**: Memory grows during training
**Diagnosis**: Profile training loop, check tensor retention
**Solution**:
- Use `loss.detach()` before logging
- Ensure `optimizer.zero_grad()` is called
- Don't store tensors that require grad

### Pattern: CPU-GPU Transfer Bottleneck
**Symptoms**: High CPU time in trace, GPU underutilized
**Diagnosis**: Profile shows `to(device)` or `cpu()` calls taking time
**Solution**:
- Pre-load data to GPU
- Use `pin_memory=True` in DataLoader
- Batch transfers
- Use async transfers with `non_blocking=True`

### Pattern: Small Kernel Launch Overhead
**Symptoms**: Many small operations, GPU not fully utilized
**Diagnosis**: Trace shows many short GPU kernels
**Solution**:
- Fuse operations
- Use `torch.compile()` (PyTorch 2.0+)
- Increase batch size
- Use fused optimizers

### Pattern: Synchronization Bottleneck
**Symptoms**: Trace shows gaps between GPU kernels
**Diagnosis**: Profile shows CPU waiting for GPU
**Solution**:
- Avoid unnecessary `torch.cuda.synchronize()`
- Move `.item()` and `.cpu()` calls out of hot path
- Use async operations

### Pattern: Memory Fragmentation
**Symptoms**: OOM despite sufficient total memory
**Diagnosis**: Memory viz shows fragmented allocation
**Solution**:
- Use memory pools
- Pre-allocate tensors
- Restart process periodically
- Use `torch.cuda.memory.set_per_process_memory_fraction()`

## Report Template

After completing diagnosis, provide:

```markdown
## PyTorch Diagnosis Report

### Problem Summary
[e.g., "GPU memory leak during inference due to cached activations"]

### GPU Memory State
- **Total GPU Memory**: [X GB]
- **Currently Allocated**: [Y GB]
- **Peak Allocation**: [Z GB]

### Performance Analysis
- **Forward Pass Time**: [X ms]
- **Key Operations**:
  1. [Operation]: [time]
  2. [Operation]: [time]

### Evidence Chain
1. Memory snapshot shows: [key findings]
2. Profile trace shows: [key findings]
3. Method watch shows: [patterns]

### Root Cause
[Detailed explanation of the PyTorch issue]

### Recommendations
1. [Code fix - e.g., "Wrap inference in torch.no_grad()"]
2. [Memory management - e.g., "Add periodic cache clearing"]
3. [Performance - e.g., "Increase batch size to improve GPU utilization"]
```

## Execution Notes

- Memory snapshots require PyTorch CUDA support
- Profile traces can be large; keep duration short
- Use Chrome tracing for visualization (chrome://tracing)
- PyTorch Memory Viz: https://pytorch.org/memory_viz
- Check both CPU and GPU time in profiles
- Memory issues often compound over time - compare multiple snapshots
