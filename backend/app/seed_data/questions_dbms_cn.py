"""Seed questions: DATABASE MANAGEMENT SYSTEMS and COMPUTER NETWORKS."""

AR = [
    "Both A and R are true, and R is the correct explanation of A",
    "Both A and R are true, but R is NOT the correct explanation of A",
    "A is true, but R is false",
    "A is false, but R is true",
]

QUESTIONS = [
    # ------------------------------------------------------------------
    # DATABASE MANAGEMENT SYSTEMS
    # ------------------------------------------------------------------
    {
        "subject": "DBMS",
        "topic": "Query Optimization",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "scenario",
        "text": (
            "Consider the query plan choices for joining A ⋈ B on a single equality column. "
            "A has 1000 pages (10 rows/page), B has 100 pages (10 rows/page). Using block "
            "nested-loop join with 3 buffer pages, which plan has lower I/O cost and why?"
        ),
        "options": [
            "A as outer: 1000 + 1000×100 = 101000 I/Os; B as outer is better",
            "B as outer: 100 + 100×1000/3 ≈ 33433 I/Os; choosing the smaller relation as outer is better",
            "Both plans cost the same because block nested-loop cost is symmetric",
            "Hash join is always required; nested-loop is never competitive at these sizes",
        ],
        "answer": [1],
        "explanation": (
            "Block nested-loop join cost = M + ceil(M/(B−2))×N where M,N are pages of the two "
            "relations and B is buffers. With M=1000, N=100, B=3: A outer = 1000 + 500×100 = "
            "51000; B outer = 100 + 50×1000 = 50100. Either way, using the smaller relation as "
            "the outer loop (fewer, larger scans) is the standard heuristic."
        ),
    },
    {
        "subject": "DBMS",
        "topic": "Transactions & Concurrency",
        "difficulty": "very_hard",
        "experience_min": 7,
        "type": "single",
        "text": (
            "Two transactions T1 and T2 execute under strict two-phase locking. T1 holds S-lock "
            "on X; T2 requests X-lock on X; then T1 requests X-lock on Y which T2 holds as S-lock. "
            "Which situation arises, and what does the DBMS do?"
        ),
        "options": [
            "No deadlock: strict 2PL upgrades are non-blocking",
            "Deadlock: the waits-for graph has a cycle; the DBMS aborts one victim and rolls back its writes",
            "T1 waits forever; strict 2PL has no deadlock detection",
            "The locks are granted in order because lock compatibility is transitive",
        ],
        "answer": [1],
        "explanation": (
            "T1 waits on T2 (X on X) and T2 waits on T1 (X on Y) → cycle. The deadlock detector "
            "aborts a victim, releases its locks, and rolls back; strict 2PL guarantees the "
            "recovery is clean because a transaction's writes are held until commit."
        ),
    },
    {
        "subject": "DBMS",
        "topic": "Transactions & Concurrency",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "debugging",
        "text": (
            "An application performs 'SELECT ... WHERE balance >= amount FOR UPDATE', updates "
            "balance, and commits. Under READ COMMITTED, two concurrent transactions both pass "
            "the SELECT and both subtract the same amount, overdrawing the account. The row "
            "update itself was atomic. What is the actual defect?"
        ),
        "options": [
            "READ COMMITTED allows phantoms; the fix is SERIALIZABLE",
            "The SELECT FOR UPDATE did not actually lock because the WHERE used a non-indexed column under READ COMMITTED",
            "The check-then-act must be protected by a single atomic statement or an explicit lock covering the decision, not separate read/write steps the isolation level cannot reconcile",
            "The bug is a lost update; the fix is to use SELECT ... FOR SHARE instead",
        ],
        "answer": [2],
        "explanation": (
            "The read and write are separate steps; READ COMMITTED does not hold locks after the "
            "statement, so the check is stale before the update commits. FOR UPDATE does lock the "
            "row, but under READ COMMITTED the lock is released at statement end (or with "
            "statement-level locking, both can read before either writes). The robust fix is a "
            "single conditional UPDATE (atomic check-and-set) or holding the lock for the whole "
            "transaction under REPEATABLE READ."
        ),
    },
    {
        "subject": "DBMS",
        "topic": "Normalization",
        "difficulty": "very_hard",
        "experience_min": 5,
        "type": "numerical",
        "text": (
            "Relation R(A, B, C, D, E) with functional dependencies: AB→C, C→D, D→E, E→A. "
            "Which set of candidate keys is correct, and what is the highest normal form of R?"
        ),
        "options": [
            "Keys {AB, BC, BD, BE}; R is in BCNF",
            "Keys {AB, BC, BD, BE}; R is in 3NF but not BCNF",
            "Keys {A, B}; R is in 1NF",
            "Keys {AB, CD}; R is in 2NF but not 3NF",
        ],
        "answer": [1],
        "explanation": (
            "Closure of {A}: A→? From E→A no, D→E no... Recompute: {A}+ = {A} (no dependency has "
            "left side subset closing on A). {B}+={B}. {AB}+: AB→C, C→D, D→E, E→A → {A,B,C,D,E} "
            "so AB is a key. {BC}+: B,C → C→D→E→A → all, key. {BD}+: D→E→A and A,B → all, key. "
            "{BE}+: E→A, then AB → all, key. All other attributes are prime. The only dependency "
            "violating BCNF is C→D (C is not a superkey, D is prime so 3NF is satisfied). Hence "
            "3NF, not BCNF."
        ),
    },
    {
        "subject": "DBMS",
        "topic": "Indexing",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "single",
        "text": (
            "A B+ tree of order d = 100 (internal nodes hold 100–200 keys, leaves 100–200 keys) "
            "stores 10,000,000 keys. How many levels does the tree have, and how many disk reads "
            "does a point lookup require when the root is cached in memory?"
        ),
        "options": [
            "4 levels; 3 disk reads (root cached)",
            "5 levels; 4 disk reads (root cached)",
            "3 levels; 2 disk reads (root cached)",
            "4 levels; 1 disk read (root cached)",
        ],
        "answer": [0],
        "explanation": (
            "Worst case (half-full nodes): leaves = 10M/100 = 100k, their parents = 100k/101 ≈ 991, "
            "then ≈10, then the root → 4 levels. Best case (full): leaves = 10M/200 = 50k, parents "
            "≈ 249, ≈ 2, root → also 4 levels. A lookup reads one node per level; with the root "
            "cached that is 3 internal reads + 1 leaf read = 3 reads from disk."
        ),
    },
    {
        "subject": "DBMS",
        "topic": "Query Processing",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "single",
        "text": (
            "SELECT COUNT(*) FROM orders WHERE status='PENDING' AND created_at BETWEEN t1 AND t2. "
            "There are two single-column indexes: one on status, one on created_at. The optimizer "
            "reports 'Index Scan using idx_status' with 4.2M estimated rows out of 40M. Which is "
            "the best optimization?"
        ),
        "options": [
            "Force an index merge (Bitmap AND) of both indexes via hints",
            "Create a composite index on (status, created_at) so the scan touches exactly the matching index pages",
            "Drop the created_at index — it is useless for this query",
            "Rewrite with a JOIN to trick the optimizer into a hash join",
        ],
        "answer": [1],
        "explanation": (
            "A covering composite index (status, created_at) lets the engine scan only index "
            "entries satisfying both predicates, with no heap lookups for COUNT(*). Bitmap AND can "
            "help when both are selective, but here status alone is only ~10% selective and the "
            "composite index is the canonical fix."
        ),
    },
    {
        "subject": "DBMS",
        "topic": "Storage & Recovery",
        "difficulty": "very_hard",
        "experience_min": 8,
        "type": "debugging",
        "text": (
            "After a crash, ARIES recovery performs analysis, redo, then undo. The log contains: "
            "<T1 start>, <T1, X, 5→10>, <T1 commit>, <T2 start>, <T2, Y, 1→2>, <CRASH>. Which "
            "statement is true about the recovery outcome?"
        ),
        "options": [
            "T1's write to X is redone if X's page LSN is older than the log record LSN; T2's write to Y is undone",
            "Both T1 and T2 are undone because redo always precedes undo",
            "T1 is undone because its commit record was not flushed to disk",
            "T2's write is redone because it appears after T1's commit",
        ],
        "answer": [0],
        "explanation": (
            "ARIES redoes all updates that reached disk buffers out of order (based on page LSN "
            "comparison), then undoes losers (T2). T1 committed so its effects survive; whether its "
            "redo applies depends on whether the page already contained the update (page LSN "
            "check), which is exactly what ARIES encodes."
        ),
    },
    {
        "subject": "DBMS",
        "topic": "Relational Algebra",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "single",
        "text": (
            "Which relational algebra expression is guaranteed to be equivalent to "
            "π_{A,B}(R ⋈_{R.C=S.C} S) for arbitrary relations R and S?"
        ),
        "options": [
            "π_{A,B}(R) × π_{A,B}(S) — cross product then project",
            "π_{A,B}(R ⋈ S) where the join is natural",
            "R ⋈ π_{C}(S) then project A,B — projecting S before the join is always safe",
            "π_{A,B}(R × S) then filter on R.C=S.C",
        ],
        "answer": [3],
        "explanation": (
            "The join is equivalent to a cross product followed by the selection on R.C=S.C, so "
            "projecting after the selection gives the same result. Projecting S down to C before a "
            "non-natural join would lose other attributes referenced by the condition; the correct "
            "general identity is selection-then-projection, not projection-before-join."
        ),
    },
    {
        "subject": "DBMS",
        "topic": "Normalization",
        "difficulty": "hard",
        "experience_min": 2,
        "type": "assertion_reason",
        "text": (
            "Assertion (A): Every relation in BCNF is also in 3NF.\n"
            "Reason (R): BCNF requires every nontrivial functional dependency's left side to be a "
            "superkey, which is strictly stronger than 3NF's requirement that right-side attributes "
            "be prime."
        ),
        "options": AR,
        "answer": [0],
        "explanation": (
            "BCNF implies 3NF: the 3NF condition is a relaxation of the BCNF condition, so any "
            "dependency that passes the BCNF test passes the 3NF test. Both statements are true "
            "and R correctly explains A."
        ),
    },
    {
        "subject": "DBMS",
        "topic": "Indexing",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "scenario",
        "text": (
            "You must support: (1) exact lookups by user_id, (2) range queries on created_at, "
            "(3) ORDER BY created_at LIMIT 10 pagination, (4) frequent bulk deletes of rows older "
            "than a year. Storage is SSD with 4KiB pages. Which index/storage strategy is best?"
        ),
        "options": [
            "Clustered primary key on user_id plus a secondary index on created_at; partition the table by month and drop old partitions",
            "Two separate heap tables mirrored by a trigger",
            "A single B+ tree keyed by (created_at, user_id) and no other index",
            "Bitmaps on every column; bitmap indexes are optimal for all four workloads",
        ],
        "answer": [0],
        "explanation": (
            "Range + ORDER BY on created_at wants a B+ tree on created_at; exact user_id lookups "
            "want an index on user_id; and monthly partitioning turns 'delete old rows' into cheap "
            "partition drops instead of index churn. Bitmaps are for low-cardinality analytics, "
            "not OLTP."
        ),
    },
    {
        "subject": "DBMS",
        "topic": "SQL Semantics",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "code",
        "text": (
            "Given tables emp(id, dept, salary) and a SQL statement:\n"
            "SELECT dept, AVG(salary) FROM emp WHERE salary > 50000 GROUP BY dept HAVING COUNT(*) > 2 "
            "ORDER BY AVG(salary) DESC;\n"
            "Which of the following statements about the evaluation order is correct?"
        ),
        "options": [
            "WHERE filters before grouping; HAVING filters groups after aggregation; ORDER BY runs last on the grouped result",
            "HAVING filters rows before WHERE is applied",
            "AVG(salary) in ORDER BY recomputes per row, not per group",
            "The query is invalid because AVG cannot be used in ORDER BY when GROUP BY is present",
        ],
        "answer": [0],
        "explanation": (
            "Standard logical order: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY. HAVING "
            "operates on groups produced by aggregation, and ORDER BY can reference aggregate "
            "expressions over those groups."
        ),
    },
    {
        "subject": "DBMS",
        "topic": "Transactions & Concurrency",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "single",
        "text": (
            "A schedule is conflict-serializable if its precedence graph is acyclic. Which of the "
            "following is also always true?"
        ),
        "options": [
            "Every conflict-serializable schedule is view-serializable",
            "Every view-serializable schedule is conflict-serializable",
            "Conflict-serializability and view-serializability are identical for schedules with blind writes",
            "Conflict-serializable schedules cannot contain cascading aborts",
        ],
        "answer": [0],
        "explanation": (
            "Conflict-serializability implies view-serializability (the containment is strict). The "
            "reverse fails in the presence of blind writes. Conflict-serializability says nothing "
            "about cascading aborts — that is the separate property of cascadeless/recoverable "
            "schedules."
        ),
    },
    # ------------------------------------------------------------------
    # COMPUTER NETWORKS
    # ------------------------------------------------------------------
    {
        "subject": "CN",
        "topic": "Transport Layer",
        "difficulty": "very_hard",
        "experience_min": 5,
        "type": "scenario",
        "text": (
            "A TCP sender with cwnd=64 segments and ssthresh=32 receives three duplicate ACKs "
            "for the same sequence number. Under TCP Reno, what happens next, and how does the "
            "window evolve?"
        ),
        "options": [
            "Fast retransmit, cwnd = ssthresh = 16, then slow start",
            "Fast retransmit, ssthresh = 32, cwnd = 32, then linear (congestion-avoidance) growth from 32",
            "Timeout, ssthresh = 32, cwnd = 1, slow start",
            "Fast retransmit, cwnd = 64, then exponential growth",
        ],
        "answer": [1],
        "explanation": (
            "On three duplicate ACKs, Reno halves ssthresh to cwnd/2 (32) and sets cwnd to "
            "ssthresh, then grows additively (1 MSS per RTT). A timeout would reset cwnd to 1; "
            "the duplicate-ACK path is the milder recovery."
        ),
    },
    {
        "subject": "CN",
        "topic": "Network Layer",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "single",
        "text": (
            "An IPv4 datagram of total length 3000 bytes (20-byte header) must traverse a link "
            "with MTU 1500 bytes. How are the fragments formed (offsets in units of 8 bytes)?"
        ),
        "options": [
            "Fragment 1: offset 0, length 1500; Fragment 2: offset 185, length 1500; Fragment 3: offset 370, length 40",
            "Fragment 1: offset 0, length 1480; Fragment 2: offset 185, length 1480; Fragment 3: offset 370, length 40",
            "Fragment 1: offset 0, length 1480; Fragment 2: offset 1480, length 1480; Fragment 3: offset 2960, length 40",
            "Fragmenting is impossible; the datagram is dropped",
        ],
        "answer": [1],
        "explanation": (
            "Payload 2980 bytes; each fragment carries at most 1480 payload bytes (MTU − 20). "
            "Fragment 1: payload 1480, offset 0; Fragment 2: payload 1480, offset 1480/8 = 185; "
            "Fragment 3: payload 20, offset 2960/8 = 370. Fragment offsets are expressed in 8-byte "
            "units, so 1480→185, not 1480."
        ),
    },
    {
        "subject": "CN",
        "topic": "Transport Layer",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "debugging",
        "text": (
            "Throughput between two data centers collapses to ~45% of the link bandwidth while "
            "TCP retransmissions are near zero and the receiver advertises a large window. "
            "What is the most likely cause?"
        ),
        "options": [
            "The sender's window is capped by RTT×bandwidth product because the receive buffer is tiny",
            "The bottleneck is the application: the sender is not posting writes fast enough",
            "Tail-drop bufferbloat is inflating RTT",
            "The MTU is misconfigured, forcing fragmentation on every packet",
        ],
        "answer": [1],
        "explanation": (
            "No retransmits + large advertised window + 45% utilization points at the sender "
            "application or its local buffer as the limiter (or a shaper). Window/throughput "
            "capping would show small window; bufferbloat would show retransmits or huge RTT; "
            "fragmentation would show ICMP or packet loss."
        ),
    },
    {
        "subject": "CN",
        "topic": "Link Layer",
        "difficulty": "very_hard",
        "experience_min": 7,
        "type": "numerical",
        "text": (
            "An Ethernet CSMA/CD network spans 2500 m; signal speed is 2×10^8 m/s. What minimum "
            "frame size guarantees collision detection before the sender finishes transmitting "
            "at 10 Mbps?"
        ),
        "options": [
            "512 bits (64 bytes)",
            "250 bits (31.25 bytes)",
            "1024 bits (128 bytes)",
            "256 bits (32 bytes)",
        ],
        "answer": [0],
        "explanation": (
            "RTT = 2 × 2500 / 2×10^8 = 25 µs. To detect collisions the sender must still be "
            "transmitting after 1 RTT: 25 µs × 10 Mbps = 250 bits — and the 802.3 standard sets "
            "the minimum at 512 bits (64 bytes) to also cover repeaters' added delay."
        ),
    },
    {
        "subject": "CN",
        "topic": "Routing",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "single",
        "text": (
            "In OSPF, two routers with matching router IDs form an adjacency over a point-to-point "
            "link. Which state sequence do they pass through, and what is the purpose of the "
            "Designated Router on a multi-access segment?"
        ),
        "options": [
            "Down → Init → 2-Way → ExStart → Exchange → Loading → Full; the DR reduces the number of adjacencies from O(n²) to O(n)",
            "Down → 2-Way → Full immediately; the DR is only used for external routes",
            "The DR performs route aggregation; without it LSA flooding is impossible",
            "Down → Init → ExStart → Full; the BDR is chosen before the DR for faster convergence",
        ],
        "answer": [0],
        "explanation": (
            "The full neighbor state machine includes the exchange states; on broadcast segments "
            "all routers form adjacencies only with the DR/BDR, cutting LSA flooding from n(n−1)/2 "
            "adjacencies to n."
        ),
    },
    {
        "subject": "CN",
        "topic": "Application Layer",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "code",
        "text": (
            "A server sends: HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nTransfer-Encoding: "
            "chunked\r\n\r\n4\r\nWiki\r\n5\r\npedia\r\n0\r\n\r\n. What does the client learn "
            "from this response?"
        ),
        "options": [
            "The body is 9 bytes: 'Wikipedia', and the message ends at the 0-chunk without needing Content-Length",
            "The body is 4+5 = 9 bytes but the connection must close to delimit the message",
            "The response is malformed because chunked and Content-Type cannot coexist",
            "The body is 4 bytes followed by a 5-byte trailer",
        ],
        "answer": [0],
        "explanation": (
            "Chunked transfer encoding sizes each chunk in hex; the terminating 0-chunk ends the "
            "body, so the client knows the message boundaries without Content-Length and the "
            "connection can be kept alive."
        ),
    },
    {
        "subject": "CN",
        "topic": "Security",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "scenario",
        "text": (
            "An on-path attacker records a TLS 1.2 session. The server certificate chain is valid, "
            "the client verifies it, and the key exchange is ECDHE-RSA. Why can the attacker NOT "
            "decrypt the session — and what would still be visible?"
        ),
        "options": [
            "ECDHE provides forward secrecy, so the recorded ciphertext cannot be decrypted later even if the server's RSA key is stolen; metadata (SNI, sizes, timing) remains visible",
            "The attacker can decrypt because the RSA key exchange used the server's certificate",
            "The attacker can replay the session because TLS has no replay protection",
            "The attacker sees the plaintext because ECDHE-RSA does not encrypt the handshake",
        ],
        "answer": [0],
        "explanation": (
            "With ECDHE the session key derives from ephemeral DH values that are discarded; "
            "capturing the RSA private key later cannot recover it (forward secrecy). Passive "
            "observers still see unencrypted metadata such as SNI in the ClientHello and traffic "
            "sizes/timing."
        ),
    },
    {
        "subject": "CN",
        "topic": "Network Layer",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "assertion_reason",
        "text": (
            "Assertion (A): A host can send an ARP request for an IP address on a different subnet "
            "and receive no reply.\n"
            "Reason (R): ARP resolves IP addresses to MAC addresses only within the same "
            "broadcast domain; routers reply for remote destinations on behalf of the host."
        ),
        "options": AR,
        "answer": [0],
        "explanation": (
            "ARP is a link-local protocol; the host forwards the packet to the default gateway's "
            "MAC, resolved by ARP for the gateway's IP. An ARP request for a remote IP goes "
            "unanswered (no host on that L2 segment owns it). Both statements are true and R "
            "explains A."
        ),
    },
    {
        "subject": "CN",
        "topic": "Congestion Control",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "single",
        "text": (
            "Which statement correctly characterizes CUBIC versus TCP Reno in high-bandwidth "
            "long-RTT (BDP ≫ buffer) environments?"
        ),
        "options": [
            "CUBIC grows the window according to a cubic function of time since the last loss, so it recovers its pre-loss window faster than Reno's one-MSS-per-RTT growth",
            "CUBIC halves the window on loss exactly like Reno and therefore cannot outperform it",
            "CUBIC is unfair to Reno flows in all scenarios",
            "CUBIC ignores RTT entirely and relies on packet pacing",
        ],
        "answer": [0],
        "explanation": (
            "CUBIC's window is a cubic polynomial in elapsed time, giving aggressive growth right "
            "after a loss event and gentle growth near the equilibrium — it converges to a target "
            "window independent of RTT, unlike Reno's per-RTT additive increase."
        ),
    },
    {
        "subject": "CN",
        "topic": "DNS",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "debugging",
        "text": (
            "Users intermittently get 'server not found' for a popular domain. The authoritative "
            "nameserver is healthy and returns correct answers from external resolvers, but "
            "recursive resolvers report SERVFAIL 30% of the time. Which cause matches?"
        ),
        "options": [
            "The zone's SOA serial number never increments, so resolvers cache stale delegations",
            "One of the zone's NS records points to a nameserver whose glue is missing or whose address is invalid, and resolvers query nameservers in random order",
            "The TTL is too high, causing clients to pin a dead address",
            "DNSSEC is disabled and resolvers require it",
        ],
        "answer": [1],
        "explanation": (
            "SERVFAIL 'sometimes' with a healthy-looking zone is the classic symptom of a broken "
            "member in an NS set: resolvers pick a nameserver at random and fail when they hit the "
            "broken one. SOA serial does not affect resolution correctness, and DNSSEC-disabled "
            "resolvers do not require signatures."
        ),
    },
]
