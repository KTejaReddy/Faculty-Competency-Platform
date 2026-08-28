"""Seed questions: DATA STRUCTURES and OPERATING SYSTEMS."""

AR = [
    "Both A and R are true, and R is the correct explanation of A",
    "Both A and R are true, but R is NOT the correct explanation of A",
    "A is true, but R is false",
    "A is false, but R is true",
]

QUESTIONS = [
    # ------------------------------------------------------------------
    # DATA STRUCTURES
    # ------------------------------------------------------------------
    {
        "subject": "DS",
        "topic": "Hash Tables",
        "difficulty": "very_hard",
        "experience_min": 5,
        "type": "numerical",
        "text": (
            "A hash table uses open addressing with linear probing, table size 11, and the hash "
            "function h(k) = k mod 11. Keys are inserted in this order: 22, 44, 15, 33, 26, 7. "
            "What is the average number of probes (including the initial slot) required to "
            "successfully search for all six keys?"
        ),
        "options": ["1.33", "1.5", "1.67", "2.0"],
        "answer": [2],
        "explanation": (
            "Insertions: 22→0, 44→0,1 (probe 0 busy, next 1), 15→4, 33→0,1,2 (0 and 1 busy, then 2), "
            "26→4,5 (4 busy, next 5), 7→7. Final layout: [22,44,33,_,15,26,_,7,_,_,_,_]. "
            "Search probes: 22:1, 44:2, 33:3, 15:1, 26:2, 7:1 → (1+2+3+1+2+1)/6 = 10/6 = 1.67."
        ),
    },
    {
        "subject": "DS",
        "topic": "Hash Tables",
        "difficulty": "expert",
        "experience_min": 8,
        "type": "single",
        "text": (
            "A dynamic hash table doubles its bucket count whenever the load factor exceeds 0.75 "
            "and halves it when the load factor drops below 0.25. Using the amortized accounting "
            "method with a potential function Phi = 2 * (number of elements) - capacity, which "
            "statement about insertion cost is correct?"
        ),
        "options": [
            "Each insertion costs O(1) worst case because rehashing never occurs more than once",
            "An insertion that triggers a rehash costs O(n), but the amortized cost of an insertion is O(1)",
            "The amortized cost is O(log n) because capacity grows geometrically",
            "The amortized cost is O(n) because each rehash redistributes every element",
        ],
        "answer": [1],
        "explanation": (
            "A single insertion that triggers a rehash is O(n) worst case, but with geometric "
            "resizing the number of such expensive operations is logarithmic per element, and the "
            "potential-function accounting argument shows each insertion has O(1) amortized cost."
        ),
    },
    {
        "subject": "DS",
        "topic": "Binary Search Trees",
        "difficulty": "very_hard",
        "experience_min": 4,
        "type": "single",
        "text": (
            "In a red-black tree, after a standard deletion that leaves the tree violating the "
            "invariant 'a red node cannot have a red child', the fix-up routine is entered with "
            "the 'double black' node as the sibling of a node X. Which rotation/recolor sequence "
            "is required when X is red?"
        ),
        "options": [
            "No rotation; simply recolor X's children to black and terminate",
            "Recolor X to black, rotate the double black node's parent, then re-enter the loop",
            "Rotate at X's parent, recolor X and its parent, then continue the loop with the sibling as X's parent's sibling",
            "Promote the double black node to red and recolor X to black",
        ],
        "answer": [2],
        "explanation": (
            "The CLRS case where the sibling (X) is red: rotate at the parent, recolor X and the "
            "parent (X becomes black, parent becomes red), which transforms the case into one where "
            "the sibling is black, and the loop continues."
        ),
    },
    {
        "subject": "DS",
        "topic": "Heaps",
        "difficulty": "hard",
        "experience_min": 2,
        "type": "single",
        "text": (
            "A binary min-heap stores 1023 elements (height 9). What is the maximum number of "
            "comparisons performed by a single extract-min, and where must the second-smallest "
            "element reside?"
        ),
        "options": [
            "18 comparisons; the second-smallest element is a child of the root (depth 1)",
            "20 comparisons; the second-smallest element is a child of the root (depth 1)",
            "18 comparisons; any leaf at depth 9",
            "20 comparisons; any node at depth 9 or shallower",
        ],
        "answer": [0],
        "explanation": (
            "Extract-min sift-downs the promoted last element along a path of length 9, doing at "
            "most 2 comparisons per level (two children, then child vs node) → 18 max. The second "
            "smallest element must be a child of the root: every other element has an ancestor "
            "between it and the root, so only the root's two children can be the second smallest."
        ),
    },
    {
        "subject": "DS",
        "topic": "Graphs",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "scenario",
        "text": (
            "You need a data structure for a live road network with 10^7 nodes and 2×10^7 edges "
            "where edge weights change continuously and shortest-path queries must be answered "
            "interactively. Which approach is most appropriate, and why?"
        ),
        "options": [
            "Run Dijkstra from the source on every query: recomputation is unavoidable and simple",
            "Precompute all-pairs shortest paths with Floyd-Warshall in O(V^3) and answer in O(1)",
            "Use A* with a Euclidean heuristic on every query: admissible and optimal with a consistent heuristic",
            "Precompute a contraction hierarchy (CH) offline and answer queries with bidirectional Dijkstra on the augmented graph",
        ],
        "answer": [3],
        "explanation": (
            "CH keeps full correctness (shortcut edges preserve shortest paths) and reduces query "
            "time by orders of magnitude versus plain Dijkstra; Floyd-Warshall is impossible at "
            "10^7 nodes; A* helps only one-to-one queries without the preprocessing advantage and "
            "does not beat CH in practice for dynamic-weight networks where weights change slowly."
        ),
    },
    {
        "subject": "DS",
        "topic": "Union-Find",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "single",
        "text": (
            "With union by rank and path compression, which tight characterization of m "
            "find/union operations on n elements is correct?"
        ),
        "options": [
            "O(m log* n) amortized, and O(log n) worst case per single operation",
            "O(m α(n)) amortized, and a single find can be O(log n) worst case",
            "O(m log n) amortized, and O(1) worst case per operation",
            "O(m α(n)) amortized, and O(α(n)) worst case per operation",
        ],
        "answer": [1],
        "explanation": (
            "The inverse-Ackermann bound O(m α(n)) is amortized; an individual find without "
            "compression benefit can still climb O(log n) rank levels before compression kicks in, "
            "so worst case per operation is O(log n)."
        ),
    },
    {
        "subject": "DS",
        "topic": "Skip Lists / Balanced Structures",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "assertion_reason",
        "text": (
            "Assertion (A): A skip list with randomized level assignment has expected O(log n) "
            "search time even though its structure is not deterministic.\n"
            "Reason (R): The expected number of pointers traversed at each level is bounded by a "
            "constant because the coin flips that generated the levels are independent."
        ),
        "options": AR,
        "answer": [0],
        "explanation": (
            "Both are true and R explains A: independence of the Bernoulli trials guarantees that "
            "the expected pointer count per level is O(1), yielding expected O(log n) search time."
        ),
    },
    {
        "subject": "DS",
        "topic": "Stacks & Queues",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "scenario",
        "text": (
            "You must implement a queue using two stacks such that each enqueue and dequeue "
            "operation has O(1) amortized cost. Which implementation achieves this, and which "
            "operation bears the amortized cost?"
        ),
        "options": [
            "Push onto stack1 on enqueue; on dequeue, if stack2 is empty, transfer all of stack1 into stack2; pop from stack2 — dequeue is amortized O(1)",
            "Push onto stack1 on enqueue; on dequeue pop from stack1 repeatedly — both are O(1) but order is reversed",
            "Use one stack only and reverse it on every operation — dequeue is O(n) worst case and O(1) amortized",
            "Push onto stack1 on enqueue and immediately transfer to stack2 — enqueue becomes O(1) amortized",
        ],
        "answer": [0],
        "explanation": (
            "Each element is pushed once and transferred at most once, so total work is O(1) per "
            "element amortized; the transfer makes individual dequeues occasionally O(k) but the "
            "amortized bound holds."
        ),
    },
    {
        "subject": "DS",
        "topic": "Tries",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "single",
        "text": (
            "A compressed trie (Patricia trie) is built over n strings with a total of L characters. "
            "Which of the following is the tightest true bound on the number of internal nodes?"
        ),
        "options": [
            "O(L) in the worst case",
            "O(n) always, regardless of L — at most n−1 internal nodes",
            "Between n and 2n−1 nodes in the worst case",
            "Exactly L nodes because every character maps to a node",
        ],
        "answer": [1],
        "explanation": (
            "In a Patricia trie every leaf is a distinct string and every internal node has at "
            "least two children, so with n leaves there can be at most n−1 internal nodes — "
            "independent of L. Two 10^6-character strings with no shared prefix produce a trie "
            "with just 3 nodes total."
        ),
    },
    {
        "subject": "DS",
        "topic": "Complexity Analysis",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "numerical",
        "text": (
            "Consider the recurrence T(n) = 2T(n/2) + n/log n (for n ≥ 2, with T(1)=1). Which "
            "asymptotic bound for T(n) is correct?"
        ),
        "options": [
            "Θ(n log n)",
            "Θ(n)",
            "Θ(n log log n)",
            "Θ(n²)",
        ],
        "answer": [2],
        "explanation": (
            "The Akra–Bazzi method (or recursion-tree analysis) gives T(n) = Θ(n log log n): the "
            "level cost n/log(n/2^k) sums to n·(1/log n + 1/log(n/2) + …) ≈ n·log log n, which is "
            "asymptotically smaller than n log n, so the standard Master Theorem does not apply "
            "directly (it applies only to polynomial factors)."
        ),
    },
    # ------------------------------------------------------------------
    # OPERATING SYSTEMS
    # ------------------------------------------------------------------
    {
        "subject": "OS",
        "topic": "Deadlocks",
        "difficulty": "hard",
        "experience_min": 2,
        "type": "numerical",
        "text": (
            "A system has 5 processes and 3 resource types: R1 (8 instances), R2 (6 instances), "
            "R3 (10 instances). At time t the allocation and maximum-need matrices are: "
            "P0:(2,0,2)/(4,1,4), P1:(2,1,1)/(3,2,3), P2:(1,2,1)/(2,3,2), P3:(1,1,2)/(2,2,3), "
            "P4:(1,1,1)/(3,2,2). Is the system in a safe state, and which process can be granted "
            "the request (1,0,1) from P4 if the banker's algorithm is used?"
        ),
        "options": [
            "Safe; P4 can be granted (1,0,1) and a safe sequence exists",
            "Safe; P4 cannot be granted (1,0,1) because it would enter an unsafe state",
            "Unsafe; the request must always be denied",
            "Safe; only P0 can receive the request",
        ],
        "answer": [0],
        "explanation": (
            "Available = (8,6,10)-(7,5,7) = (1,1,3). Need = Max-Allocation: P0(2,1,2), P1(1,1,2), "
            "P2(1,1,1), P3(1,1,1), P4(2,1,1). Safe sequence exists (e.g. P1→P3→P2→P4→P0). The "
            "request (1,0,1) ≤ Available: testing the state with P4 holding (2,1,2) leaves "
            "Available (0,1,2) and a safe sequence (P2→P3→P1→P0→P4) still exists, so it is granted."
        ),
    },
    {
        "subject": "OS",
        "topic": "Scheduling",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "single",
        "text": (
            "Under the Multilevel Feedback Queue scheduler (three queues: Q1 RR quantum 4ms, "
            "Q2 RR quantum 16ms, Q3 FCFS, priority boost every 200ms), a CPU-bound process that "
            "never blocks will eventually:"
        ),
        "options": [
            "Starve permanently in Q3 because lower queues have lower priority",
            "Receive at most 20ms of CPU per 200ms boost cycle and cycle between Q2 and Q3",
            "Be moved up to Q1 by the priority boost and receive guaranteed CPU each cycle",
            "Run to completion in Q1 because RR never preempts a completing process",
        ],
        "answer": [2],
        "explanation": (
            "With a periodic priority boost, processes in lower queues are demoted only by queue "
            "selection but are periodically moved back to the top queue, preventing starvation; "
            "a purely CPU-bound process stays in Q2/Q3 but is boosted regularly."
        ),
    },
    {
        "subject": "OS",
        "topic": "Memory Management",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "scenario",
        "text": (
            "A system uses two-level page tables with 4KiB pages and 48-bit virtual addresses; "
            "each page-table entry is 8 bytes. The process has a working set of exactly 64 pages "
            "scattered across 512 distinct 1GiB regions. Approximately how much memory do its "
            "page tables consume, and what is the main TLB consequence?"
        ),
        "options": [
            "About 4 MiB of page tables; TLB misses are cheap because the working set fits in L1",
            "About 16 MiB of page tables; every access potentially misses the TLB because pages are scattered",
            "About 2 MiB of page tables; TLB thrashing is unlikely since 64 pages fit in a large TLB",
            "Zero extra memory — page tables are paged out automatically",
        ],
        "answer": [2],
        "explanation": (
            "48-bit VA with 4KiB pages: 36 bits of offset/level index → 9 bits per level. Each "
            "level-2 table covers 512×4KiB=2MiB; 512 1GiB regions → 512×512 level-2 tables ≈ "
            "256K entries × 8B ≈ 2MiB, plus one level-1 table (4KiB) and one root table. A 64-page "
            "working set across scattered 2MiB regions means the 512-entry L2 TLB can hold all "
            "footprints if each region maps through a single L2 entry — with 4KiB pages and "
            "2MiB-aligned regions, 64 pages in 512 regions still needs ≤ 512 L2 entries, so "
            "thrashing is avoided."
        ),
    },
    {
        "subject": "OS",
        "topic": "Memory Management",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "debugging",
        "text": (
            "A database server starts thrashing: disk I/O explodes and CPU utilization collapses "
            "to ~5% while the RSS of the process stays constant. All heap allocations are correct "
            "and there is no leak. Which is the most likely cause and the correct first fix?"
        ),
        "options": [
            "Increase the heap size with -Xmx-style settings so the working set fits in RAM",
            "Enable transparent huge pages to reduce TLB misses",
            "The process's memory footprint exceeds the available physical memory; reduce the working set or increase available RAM / configure memory cgroups",
            "Switch the allocator to jemalloc; the default allocator is the bottleneck",
        ],
        "answer": [2],
        "explanation": (
            "Collapsed CPU + high I/O with constant RSS is the classic thrashing signature: the "
            "working set does not fit in RAM and every access faults. The fix is to shrink the "
            "working set (or add memory / set cgroup limits), not to tune the allocator or THP."
        ),
    },
    {
        "subject": "OS",
        "topic": "Concurrency",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "code",
        "text": (
            "Thread A holds mutex M1 and waits on condition variable C (spurious wakeups are "
            "possible). Which of the following wait patterns is correct?"
        ),
        "options": [
            "pthread_cond_wait(&C, &M1); unlock(M1);",
            "while (!predicate) pthread_cond_wait(&C, &M1);",
            "if (!predicate) pthread_cond_wait(&C, &M1);",
            "unlock(M1); pthread_cond_wait(&C, &M1); lock(M1);",
        ],
        "answer": [1],
        "explanation": (
            "pthread_cond_wait atomically releases M1 and re-acquires it on return; the standard "
            "pattern re-checks the predicate in a loop to handle spurious wakeups and lost "
            "wakeups. The if-pattern and unlock-before-wait are both incorrect."
        ),
    },
    {
        "subject": "OS",
        "topic": "Concurrency",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "scenario",
        "text": (
            "A reader–writer lock allows many readers or one writer. A writer has been waiting "
            "for 30 seconds while readers continuously acquire and release the lock (reader "
            "preference). You must fix the starvation. Which design change is minimal and correct?"
        ),
        "options": [
            "Add a writer-preference flag that blocks new readers once a writer is queued",
            "Increase the lock's read-side spin count so readers release faster",
            "Use a single global mutex for all accesses — it eliminates starvation by construction",
            "Let readers bypass the writer queue when the data is immutable",
        ],
        "answer": [0],
        "explanation": (
            "Writer starvation under reader preference is fixed by blocking new readers (or using "
            "a ticket/fairness scheme) once a writer is pending. A global mutex 'fixes' it by "
            "destroying read parallelism, not by fairness."
        ),
    },
    {
        "subject": "OS",
        "topic": "File Systems",
        "difficulty": "very_hard",
        "experience_min": 8,
        "type": "single",
        "text": (
            "An ext4 filesystem with a 4KiB block size uses direct pointers plus 1 single, 1 "
            "double and 1 triple indirect block. What is the maximum file size that can be "
            "represented with a 4-byte block pointer?"
        ),
        "options": [
            "About 4 GiB",
            "About 4 TiB",
            "About 4 PiB",
            "About 16 TiB",
        ],
        "answer": [1],
        "explanation": (
            "Per block: 4096/4 = 1024 pointers. Direct: 12 blocks; single indirect: 1024; double: "
            "1024²; triple: 1024³ → total ≈ 12 + 1024 + 1M + 1G blocks × 4KiB ≈ 4.0 TiB (the "
            "classic limit; ext4 lifts it further with extent trees)."
        ),
    },
    {
        "subject": "OS",
        "topic": "File Systems",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "debugging",
        "text": (
            "After a power failure, a journaling filesystem mounts cleanly, but a file that was "
            "being appended at the moment of the crash shows a length of 0 with journal recovery "
            "reporting no errors. What is the most plausible explanation?"
        ),
        "options": [
            "The journal only orders metadata; the data blocks of the append were never committed before the crash",
            "The filesystem is corrupt and the journal is lying",
            "The write was buffered in the page cache and the fsync returned success spuriously",
            "The file was deleted by another process between the crash and the mount",
        ],
        "answer": [0],
        "explanation": (
            "In ordered/data=ordered mode only metadata is journaled; if the data blocks were not "
            "flushed before the metadata commit, recovery can leave a zero-length or stale file "
            "while reporting a consistent journal. This is the classic data-consistency tradeoff "
            "of journaling."
        ),
    },
    {
        "subject": "OS",
        "topic": "Virtualization & Kernels",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "single",
        "text": (
            "On x86-64, which mechanism makes hardware-assisted virtualization (VT-x) able to "
            "run a guest OS with almost no binary translation, and what is the main remaining cost?"
        ),
        "options": [
            "Shadow page tables with write-protection; cost is TLB shootdowns on every page-table write",
            "VMX root/non-root modes with VM exits for privileged operations; cost is the VM-exit/VM-entry overhead",
            "Ring -1 with trapped I/O; cost is system-call emulation",
            "Paravirtualized ABI; cost is guest kernel modifications",
        ],
        "answer": [1],
        "explanation": (
            "VT-x adds a distinct non-root operation mode where most instructions execute "
            "natively; privileged/sensitive operations cause VM exits. The dominant remaining "
            "overhead is the exit/entry transition cost, which is why virtio and EPT exist to "
            "reduce exit frequency."
        ),
    },
    {
        "subject": "OS",
        "topic": "Processes & IPC",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "single",
        "text": (
            "A process forks a child, then calls execve on the child. Which statement about "
            "memory behavior is correct on a modern Linux with copy-on-write?"
        ),
        "options": [
            "The parent's entire address space is copied before execve runs",
            "The child shares all pages with the parent until either writes, so execve happens before any physical copy",
            "Only the stack and heap are copied; text segments are always shared",
            "The fork syscall itself performs a full page-table walk and copies every PTE into a new page table",
        ],
        "answer": [3],
        "explanation": (
            "fork copies the page tables (every PTE marked read-only) while the underlying frames "
            "are shared copy-on-write; pages are physically copied only on write. The PTE copy is "
            "the dominant O(VMA) cost — not a full physical memory copy."
        ),
    },
    {
        "subject": "OS",
        "topic": "Synchronization",
        "difficulty": "very_hard",
        "experience_min": 7,
        "type": "assertion_reason",
        "text": (
            "Assertion (A): Using spinlocks inside a process that can be preempted by the "
            "scheduler can deadlock a uniprocessor system.\n"
            "Reason (R): A preempted task holding a spinlock prevents the lock holder from "
            "making progress because no other task can run until the scheduler resumes it."
        ),
        "options": AR,
        "answer": [0],
        "explanation": (
            "On UP, if a task is preempted while holding a spinlock, the running task spins forever "
            "waiting for a CPU it can never get; Linux therefore disables preemption while "
            "holding spinlocks. Both statements are true and R explains A."
        ),
    },
    {
        "subject": "OS",
        "topic": "I/O Systems",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "scenario",
        "text": (
            "A storage array serves mixed 4KiB random reads and large sequential writes. Queue "
            "depth is 256. Which of the following is the correct prediction about elevator (SCAN) "
            "versus shortest-seek-time-first (SSTF) scheduling?"
        ),
        "options": [
            "SSTF minimizes total seek distance but can starve requests far from the current position",
            "SCAN can starve requests and has unbounded worst-case latency",
            "Both guarantee bounded latency for every request",
            "SSTF is always optimal in seek distance and never starves",
        ],
        "answer": [0],
        "explanation": (
            "SSTF greedily minimizes seek but can postpone far requests indefinitely; SCAN sweeps "
            "both directions and bounds worst-case latency. Neither is globally optimal, and in "
            "modern SSDs seek cost is negligible so logical ordering matters less."
        ),
    },
]
