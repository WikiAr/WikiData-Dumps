# NumPy Optimization Plan for Wikidata Dump Processing

This document outlines a strategy to optimize the performance and memory usage of the Wikidata dump processing scripts in the `dump27` directory using NumPy.

## 1. Problem Statement
The current implementation relies heavily on Python dictionaries to aggregate counts for millions of Wikidata items (QIDs) and properties (PIDs). As the dump size exceeds 90GB and contains over 100 million items, dictionary-based aggregation becomes:
- **Memory Intensive**: Python dictionaries have significant overhead for each entry.
- **Slow**: Incremental updates in nested loops are bottlenecked by Python's interpreter speed.
- **I/O Bound**: Frequent reading/writing of small JSON files increases overhead.

## 2. Optimization Strategy

### A. Integer Encoding of Wikidata IDs
Wikidata IDs like `Q123` or `P31` are currently handled as strings. Converting these to integers (e.g., `123` and `31`) allows them to be stored in compact NumPy arrays.
- **Action**: Strip the 'Q' or 'P' prefix and store the numerical ID as a 32-bit or 64-bit integer (`np.int32` or `np.int64`).
- **Benefit**: Drastic reduction in memory footprint compared to strings.

### B. High-Performance Counting with NumPy
Instead of `dict[id] += 1`, we can use specialized NumPy functions for aggregation:
- **`np.bincount`**: Best for dense integer IDs. If IDs are within a reasonable range, `bincount` is extremely fast as it uses the ID directly as an index.
- **`np.unique(return_counts=True)`**: Ideal for sparse IDs. It sorts the array and counts occurrences in a single vectorized pass.
- **Implementation**: Accumulate IDs in a large array during processing, then call the counting function once.

### C. Memory-Mapped Files (`np.memmap`)
To handle data that exceeds available RAM, we can use memory-mapped files.
- **Action**: Store raw integer IDs directly to disk in a binary format using `np.memmap`.
- **Benefit**: Allows processing of billions of claims by treating disk space as virtual memory, with the OS handling page caching efficiently.

### D. Vectorized Data Processing
Replace row-by-row dictionary updates in `r_28.py` and `bot.py` with batch operations.
- **Workflow**:
    1. Parse a chunk of the JSON dump.
    2. Extract relevant IDs into a NumPy array.
    3. Perform counts or filters using NumPy's vectorized operations.
    4. Save results in a binary format instead of many small JSON files.

## 3. Implementation Steps

### Phase 1: `r_28.py` Refactoring
- Modify `dump_lines_claims` to collect claim IDs into NumPy arrays.
- Use `np.save` to write binary files for each PID instead of appending JSON lines to text files.

### Phase 2: `claims_max/bot.py` Refactoring
- Update `ClaimsProcessor` to read binary NumPy files.
- Use `np.unique` to aggregate counts across multiple files for the same PID.
- Convert the final results back to JSON only for the reporting step.

### Phase 3: Global ID Mapping (Optional)
- Maintain a global mapping of large QIDs if they cannot be easily converted to integers.

## 4. Expected Impact
- **Speed**: Processing time is expected to decrease by 5x - 10x for the aggregation phase.
- **Memory**: RAM usage will be more predictable and can be capped by using chunks and memory maps.
- **Scalability**: The system will be better prepared for the continued growth of the Wikidata dataset.
