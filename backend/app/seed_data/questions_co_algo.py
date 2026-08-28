"""Seed questions: COMPUTER ORGANIZATION and ALGORITHMS."""

AR = [
    "Both A and R are true, and R is the correct explanation of A",
    "Both A and R are true, but R is NOT the correct explanation of A",
    "A is true, but R is false",
    "A is false, but R is true",
]

QUESTIONS = [
    # ------------------------------------------------------------------
    # COMPUTER ORGANIZATION
    # ------------------------------------------------------------------
    {
        "subject": "CO",
        "topic": "Pipelining",
        "difficulty": "very_hard",
        "experience_min": 5,
        "type": "numerical",
        "text": (
            "A 5-stage pipeline (F, D, EX, MEM, WB) with full forwarding has 20% branches with "
            "60% taken and a fixed 2-cycle branch penalty, and 10% of all instructions are loads "
            "whose result is used by the immediately following instruction (1 load-use stall "
            "each). What is the approximate CPI?"
        ),
        "options": ["1.0", "1.24", "1.34", "1.5"],
        "answer": [2],
        "explanation": (
            "Ideal CPI = 1. Branch stalls: 0.20 × 0.60 × 2 = 0.24. Load-use stalls: 0.10 × 1 = "
            "0.10. CPI = 1 + 0.24 + 0.10 = 1.34."
        ),
    },
    {
        "subject": "CO",
        "topic": "Cache Design",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "scenario",
        "text": (
            "Which type of cache miss is NOT reduced by increasing cache associativity?"
        ),
        "options": [
            "Conflict misses — more ways reduce thrashing between competing lines",
            "Compulsory (cold) misses — the first reference to a line must miss regardless of placement",
            "Capacity misses — more ways use existing capacity more flexibly",
            "All of the above are reduced by higher associativity",
        ],
        "answer": [1],
        "explanation": (
            "Compulsory misses occur the first time a line is touched and are independent of the "
            "replacement/placement policy — no associativity change can avoid them (only larger "
            "blocks or prefetching help). Associativity primarily trades conflict misses against "
            "hit time."
        ),
    },
    {
        "subject": "CO",
        "topic": "Cache Design",
        "difficulty": "very_hard",
        "experience_min": 7,
        "type": "single",
        "text": (
            "A write-back cache with write-allocate policies has a dirty line that is evicted. "
            "Which statement about the resulting traffic is correct?"
        ),
        "options": [
            "The dirty line is written to the next level of memory, and a fill of the new line follows — two transfers for one miss",
            "The dirty line is discarded because write-back means memory is always updated on every store",
            "Only the byte that was modified is written back",
            "The eviction stalls the pipeline until the next miss is serviced",
        ],
        "answer": [0],
        "explanation": (
            "Write-back + write-allocate means stores update the cache only; on eviction the whole "
            "dirty line is written back to the next level and the miss's fill transfers the new "
            "line in — this 'dirty miss' costs both write-back and fill bandwidth."
        ),
    },
    {
        "subject": "CO",
        "topic": "Instruction Sets",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "debugging",
        "text": (
            "After refactoring, a C loop over a large array compiles to a tight loop that "
            "runs 30% slower, and profiling shows 40% of cycles in 'instruction fetch / "
            "front-end stalls'. The branch predictor's accuracy is 99.9%. What is happening?"
        ),
        "options": [
            "The loop body exceeds the instruction cache (I-cache) working set, causing front-end misses",
            "The branch predictor is broken and every branch is mispredicted",
            "Data cache misses are being mislabeled as front-end stalls",
            "The compiler unrolled the loop too aggressively, increasing the branch count",
        ],
        "answer": [0],
        "explanation": (
            "Front-end stalls with an accurate predictor point to I-cache misses or decode "
            "bandwidth limits — the refactored loop's code footprint no longer fits the "
            "instruction working set. Branch mispredicts would show a low predictor accuracy; "
            "data misses would appear as load-use/back-end stalls."
        ),
    },
    {
        "subject": "CO",
        "topic": "Memory Hierarchy",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "single",
        "text": (
            "Which statement about the relationship between virtual memory, TLB, and cache is "
            "correct on a modern x86-64 system?"
        ),
        "options": [
            "The cache is always indexed by physical address (PIPT), so a TLB lookup is never on the critical path",
            "Virtually-indexed, physically-tagged (VIPT) caches can be indexed before the TLB translation, hiding TLB latency, but require page-offset aliasing care",
            "TLB misses are never serviced in hardware on x86-64",
            "The TLB is a cache of the page table entries and is always fully associative",
        ],
        "answer": [1],
        "explanation": (
            "L1 caches are VIPT: the index bits (within the page offset) come from the virtual "
            "address before translation, so the tag comparison waits only for the physical tag; "
            "aliasing is avoided by keeping cache size/associativity within the page size. TLB "
            "misses ARE serviced by hardware page-walkers on x86-64, and TLBs are usually "
            "set-associative, not fully associative."
        ),
    },
    {
        "subject": "CO",
        "topic": "Arithmetic",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "numerical",
        "text": (
            "In IEEE-754 single precision, what is the value of the bit pattern 0xBF800000, and "
            "what is the ulp (unit in the last place) of a number with exponent 0 in this format?"
        ),
        "options": [
            "-1.0; ulp = 2^-23",
            "-1.5; ulp = 2^-24",
            "1.0; ulp = 2^-23",
            "-1.0; ulp = 2^-22",
        ],
        "answer": [0],
        "explanation": (
            "0xBF800000: sign 1, exponent 0x7F (bias 127 → e=0), mantissa 0 → -(1.0)×2^0 = -1.0. "
            "The ulp for numbers in the binade [1,2) (exponent 0) is the mantissa's least "
            "significant bit: 2^-23."
        ),
    },
    {
        "subject": "CO",
        "topic": "ILP & Superscalar",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "single",
        "text": (
            "A 4-wide out-of-order processor sustains only 1.7 IPC on a loop with a long serial "
            "dependency chain. Adding more execution ports raises IPC to 1.8. What is the "
            "dominant limit, and which hardware change addresses it?"
        ),
        "options": [
            "Data dependencies bound the loop; deeper speculation or value prediction / restructuring the chain helps more than more ports",
            "The front-end is the bottleneck; widen fetch to 8 instructions per cycle",
            "The reorder buffer is too small; doubling ROB size is the correct fix",
            "The branch predictor is the bottleneck; use a larger TAGE predictor",
        ],
        "answer": [0],
        "explanation": (
            "A serial dependency chain of latency L per iteration caps IPC at 1/L regardless of "
            "width or ports (IPC only moved 1.7→1.8 with more ports). Breaking the chain "
            "(unrolling, reassociation, value prediction) attacks the true limit."
        ),
    },
    {
        "subject": "CO",
        "topic": "Performance",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "numerical",
        "text": (
            "A system spends 60% of time in one function F. You optimize F to run 3× faster. "
            "By how much does total execution time improve (Amdahl), and what happens if you "
            "then optimize F to run 1000× faster?"
        ),
        "options": [
            "Speedup 1.67; further optimization of F is capped at 2.5× total",
            "Speedup 3.0; further optimization gives 1000× total",
            "Speedup 2.5; further optimization is capped at 2.5× total",
            "Speedup 1.67; further optimization gives 2.4× total",
        ],
        "answer": [0],
        "explanation": (
            "Speedup = 1 / (0.4 + 0.6/3) = 1/0.6 = 1.67. As F approaches infinite speedup, total "
            "time → 0.4, so the total speedup is capped at 1/0.4 = 2.5× — the sequential 40% "
            "dominates."
        ),
    },
    # ------------------------------------------------------------------
    # ALGORITHMS
    # ------------------------------------------------------------------
    {
        "subject": "ALGO",
        "topic": "Divide & Conquer",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "single",
        "text": (
            "Given a sorted array rotated an unknown number of times, WITH possible duplicate "
            "values, the standard binary-search algorithm that compares arr[mid] with arr[high] "
            "to find the minimum element:"
        ),
        "options": [
            "Always runs in O(log n) regardless of the input",
            "Degrades to O(n) worst case when duplicates make the comparison ambiguous (e.g. an array of all equal values)",
            "Requires comparing arr[mid] with arr[low] instead to remain correct",
            "Cannot be solved faster than O(n log n) in any case",
        ],
        "answer": [1],
        "explanation": (
            "With distinct values the algorithm is O(log n). When arr[mid] == arr[high] the search "
            "cannot decide which half to discard, so the classic solution shrinks the window by one "
            "per step — worst case O(n) (an array of identical values needs linear scan)."
        ),
    },
    {
        "subject": "ALGO",
        "topic": "Dynamic Programming",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "single",
        "text": (
            "For the 0/1 knapsack with n items and capacity W, which statement about the "
            "standard DP is correct?"
        ),
        "options": [
            "Time is O(nW), which is pseudo-polynomial — polynomial in the numeric value of W but exponential in its bit length",
            "Time is O(nW), which is fully polynomial because W is a constant",
            "The problem becomes polynomial when W is part of the input in binary",
            "The DP is optimal only for fractional items",
        ],
        "answer": [0],
        "explanation": (
            "O(nW) is pseudo-polynomial: polynomial in the magnitude of W, exponential in the "
            "input size log W. This is exactly why 0/1 knapsack is NP-complete in general and "
            "why the DP is only usable when W is small."
        ),
    },
    {
        "subject": "ALGO",
        "topic": "Greedy",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "scenario",
        "text": (
            "Interval scheduling: given intervals [s_i, f_i), select the maximum number of "
            "non-overlapping intervals. Which greedy choice is correct, and which common "
            "alternative fails?"
        ),
        "options": [
            "Sort by finish time and always pick the interval that finishes earliest among compatible ones — optimal",
            "Sort by start time and pick the earliest-starting compatible interval — optimal",
            "Sort by duration and pick the shortest compatible interval — optimal",
            "Pick the interval with the fewest overlaps (interval graph coloring heuristic) — optimal",
        ],
        "answer": [0],
        "explanation": (
            "Earliest-finish-first is optimal by the classic exchange argument. Earliest start "
            "fails (a long interval starting early blocks many short ones), shortest-duration "
            "fails (one short interval in the middle can block two compatible longer ones), and "
            "the fewest-overlap heuristic is only for coloring."
        ),
    },
    {
        "subject": "ALGO",
        "topic": "Graph Algorithms",
        "difficulty": "very_hard",
        "experience_min": 7,
        "type": "single",
        "text": (
            "Which statement about running Bellman–Ford on a graph with negative-weight edges "
            "is correct?"
        ),
        "options": [
            "It detects negative cycles reachable from the source and reports 'no shortest path exists' for affected vertices",
            "It fails on any graph containing a negative edge, even without negative cycles",
            "It runs in O(V+E) and cannot handle negative edges",
            "It computes correct distances only if the graph is a DAG",
        ],
        "answer": [0],
        "explanation": (
            "Bellman–Ford relaxes all edges V−1 times; a final relaxation that still improves any "
            "edge proves a reachable negative cycle. It handles negative edges fine — Dijkstra is "
            "the one that fails with them."
        ),
    },
    {
        "subject": "ALGO",
        "topic": "String Algorithms",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "numerical",
        "text": (
            "You run the KMP algorithm with the failure function for pattern 'ABABACA'. What is "
            "the value of the failure function (longest proper border length) at each position of "
            "the pattern, 1-indexed?"
        ),
        "options": [
            "[0, 0, 1, 2, 3, 0, 1]",
            "[0, 0, 1, 2, 1, 0, 1]",
            "[0, 1, 2, 3, 4, 0, 0]",
            "[0, 0, 1, 2, 3, 0, 0]",
        ],
        "answer": [0],
        "explanation": (
            "Pattern A B A B A C A. Position 1 'A': 0. Position 2 'AB': 0. Position 3 'ABA': border "
            "'A' → 1. Position 4 'ABAB': border 'AB' → 2. Position 5 'ABABA': border 'ABA' → 3. "
            "Position 6 'ABABAC': 0. Position 7 'ABABACA': border 'A' → 1. Hence [0,0,1,2,3,0,1]."
        ),
    },
    {
        "subject": "ALGO",
        "topic": "Divide & Conquer",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "single",
        "text": (
            "The Master Theorem applies to T(n) = aT(n/b) + f(n). Which of the following "
            "recurrences CANNOT be solved directly with the standard Master Theorem form?"
        ),
        "options": [
            "T(n) = 2T(n/2) + n²",
            "T(n) = 3T(n/4) + n",
            "T(n) = 2T(n/2) + n/log n",
            "T(n) = 7T(n/2) + n²",
        ],
        "answer": [2],
        "explanation": (
            "The Master Theorem's case 2 requires f(n) to be Θ(n^(log_b a) · log^k n) for some "
            "k ≥ 0; n/log n is smaller than n^(log_2 2) = n by a non-polynomial factor (log), so "
            "the theorem's cases do not apply — the Akra–Bazzi method gives Θ(n log log n). The "
            "others fall cleanly into the three cases."
        ),
    },
    {
        "subject": "ALGO",
        "topic": "Randomized Algorithms",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "scenario",
        "text": (
            "You must test whether a polynomial P of degree d (d large, coefficients huge) is the "
            "zero polynomial. Evaluating at a fixed point is unreliable; evaluating at random "
            "points works probabilistically. What is the correct characterization?"
        ),
        "options": [
            "Evaluate P at k random values from a field of size m: false-positive probability ≤ d/m per trial, and k trials reduce it to (d/m)^k",
            "Evaluating at any one random point gives certainty because polynomials have finitely many roots",
            "The Schwartz–Zippel bound only applies to multivariate polynomials",
            "Random evaluation detects zero polynomials with probability exactly 1/d",
        ],
        "answer": [0],
        "explanation": (
            "Schwartz–Zippel: a nonzero degree-d polynomial vanishes at at most d points of an "
            "m-element domain, so one random evaluation errs with probability ≤ d/m; independent "
            "trials multiply the error. This is the basis of polynomial identity testing and "
            "fingerprinting."
        ),
    },
    {
        "subject": "ALGO",
        "topic": "Data Structures",
        "difficulty": "very_hard",
        "experience_min": 8,
        "type": "debugging",
        "text": (
            "A Fenwick tree (BIT) of size n is built, and the code computes prefix sums by "
            "'sum += tree[i]; i -= i & (-i)'. After a point update 'add(idx, delta)' implemented "
            "as 'while (idx <= n) { tree[idx] += delta; idx += idx & (-idx); }', prefix sums for "
            "an index just above idx are wrong. What is the most likely bug?"
        ),
        "options": [
            "The tree was initialized with a build that skipped the update propagation to ancestors",
            "The prefix-sum loop condition should be 'i > 0' and the update loop starts from idx (1-based); mixing 0-based and 1-based indexing corrupts the structure",
            "Fenwick trees cannot support point updates at all",
            "The delta must be multiplied by -1 on update",
        ],
        "answer": [1],
        "explanation": (
            "Fenwick trees are 1-indexed: the update loop must start at idx (1-based) and the "
            "query loop must run while i > 0. If the array is stored 0-based but the loops are "
            "mixed, ancestor propagation skips entries and prefix sums silently break for indices "
            "above the updated position."
        ),
    },
    {
        "subject": "ALGO",
        "topic": "Flow Networks",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "single",
        "text": (
            "In the Edmonds–Karp algorithm (BFS-based augmenting paths), which of the following "
            "is the tightest true bound, and why does BFS matter?"
        ),
        "options": [
            "O(VE²) because each of O(VE) augmentations takes O(E) BFS time",
            "O(VE²) because each of O(E) augmentations takes O(VE) BFS time",
            "O(V²E) because augmenting paths are at most V long and there are O(E) of them",
            "O(VE) because BFS finds the shortest augmenting path in O(E) and there are at most V of them",
        ],
        "answer": [0],
        "explanation": (
            "Edmonds–Karp performs O(VE) augmentations (each edge becomes critical at most V/2 "
            "times) and each BFS takes O(E) time, giving O(VE²) total. Choosing BFS (shortest "
            "augmenting path) is what bounds the number of augmentations; DFS (Ford–Fulkerson) "
            "has no such polynomial guarantee."
        ),
    },
    {
        "subject": "ALGO",
        "topic": "Complexity Theory",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "assertion_reason",
        "text": (
            "Assertion (A): If P = NP then every problem in NP can be solved in polynomial time.\n"
            "Reason (R): Every problem in NP reduces to every NP-complete problem in polynomial time."
        ),
        "options": AR,
        "answer": [0],
        "explanation": (
            "NP-hardness is defined via polynomial-time reductions FROM every NP problem; if some "
            "NP-complete problem is in P, following the reduction plus the polynomial solver "
            "solves every NP problem in polynomial time. Both statements are true and R is the "
            "mechanism behind A."
        ),
    },
]
