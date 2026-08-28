"""Seed questions: JAVA PROGRAMMING and SOFTWARE ENGINEERING."""

AR = [
    "Both A and R are true, and R is the correct explanation of A",
    "Both A and R are true, but R is NOT the correct explanation of A",
    "A is true, but R is false",
    "A is false, but R is true",
]

QUESTIONS = [
    # ------------------------------------------------------------------
    # JAVA PROGRAMMING
    # ------------------------------------------------------------------
    {
        "subject": "JAVA",
        "topic": "Concurrency",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "debugging",
        "text": (
            "A service uses a volatile boolean flag 'running' to stop a worker thread that "
            "periodically calls a blocking queue's take(). The worker never stops. Why?"
        ),
        "options": [
            "volatile does not provide visibility across threads — the worker must use synchronized",
            "The worker is blocked in take() and will not re-read the flag until it returns; interruption is required to break out of the blocking call",
            "volatile is only for primitives, not booleans",
            "The flag must be declared final to be shared safely",
        ],
        "answer": [1],
        "explanation": (
            "volatile DOES provide visibility; the real problem is the worker is parked inside "
            "take(), so it never observes the flag. The correct pattern is Thread.interrupt() "
            "(which makes take() throw InterruptedException) or a timed poll so the loop re-checks "
            "the flag."
        ),
    },
    {
        "subject": "JAVA",
        "topic": "Memory Model",
        "difficulty": "very_hard",
        "experience_min": 7,
        "type": "single",
        "text": (
            "Thread A writes x = 1 then y = 2; Thread B reads y then x, both through plain "
            "(non-volatile, unsynchronized) fields with no happens-before between the threads. "
            "Which outcomes are possible on a real JVM?"
        ),
        "options": [
            "B can see y == 2 and x == 0, or x == 1 and y == 0 — without synchronization the JMM allows reordering of the writes and reads",
            "B always sees y == 2 before x == 1 because writes happen in program order",
            "B always sees both writes or neither, because of the JMM's coherence guarantee",
            "The program is guaranteed to print x==1 and y==2 because the JMM forbids data races",
        ],
        "answer": [0],
        "explanation": (
            "Without a happens-before edge the JMM permits reordering: B may observe y=2 but stale "
            "x=0 (or vice versa). The JMM only guarantees program-order visibility within a "
            "thread; cross-thread ordering requires synchronization, volatile, or other "
            "happens-before edges."
        ),
    },
    {
        "subject": "JAVA",
        "topic": "Collections",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "scenario",
        "text": (
            "Two threads concurrently put() into a HashMap without external synchronization. "
            "Which of the following is a guaranteed risk on modern JDKs (Java 8+)?"
        ),
        "options": [
            "An infinite loop during resize is still possible because rehashing is not atomic",
            "Data loss and corruption are possible (lost updates, overwritten entries) but the infinite-resize loop is the signature JDK 8 issue",
            "HashMap is thread-safe as long as both threads only call put()",
            "ConcurrentHashMap is exactly HashMap with locks, so no change is needed",
        ],
        "answer": [1],
        "explanation": (
            "Concurrent put() without synchronization can lose entries and corrupt structure "
            "(especially during resize or treeification). The classic JDK 7 infinite loop was "
            "fixed in JDK 8 by replacing the resize algorithm, but unsynchronized mutation is "
            "still unsafe."
        ),
    },
    {
        "subject": "JAVA",
        "topic": "JVM Internals",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "single",
        "text": (
            "A long-running server periodically throws OutOfMemoryError: Metaspace. Heap usage "
            "is stable. Which is the correct diagnosis and fix?"
        ),
        "options": [
            "Increase -Xmx; the heap is exhausted by object churn",
            "Metaspace holds class metadata; the leak is caused by unbounded class loading (e.g. per-request proxies/generators) — fix the loader leak or bound -XX:MaxMetaspaceSize",
            "Enable G1GC to compact class metadata automatically",
            "Reduce the number of worker threads; threads occupy Metaspace",
        ],
        "answer": [1],
        "explanation": (
            "Metaspace stores class/loader metadata, not objects — a stable heap with Metaspace "
            "exhaustion means class loaders (and their classes) are being leaked, typically by "
            "dynamic proxy/generation per request. G1 does not manage Metaspace, and -Xmx only "
            "caps the heap."
        ),
    },
    {
        "subject": "JAVA",
        "topic": "Language Semantics",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "code",
        "text": (
            "What does this print?\n"
            "String a = \"abc\"; String b = new String(\"abc\");\n"
            "System.out.println(a == b);\n"
            "System.out.println(a.equals(b));\n"
            "System.out.println(a.intern() == b.intern());"
        ),
        "options": [
            "false, true, true",
            "true, true, true",
            "false, false, true",
            "true, false, false",
        ],
        "answer": [0],
        "explanation": (
            "== compares references: a is the interned literal, b is a fresh object → false. "
            "equals compares content → true. intern() returns the canonical string-pool instance "
            "for both → same reference → true."
        ),
    },
    {
        "subject": "JAVA",
        "topic": "Exceptions",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "code",
        "text": (
            "try { throw new IOException(); } catch (Exception e) { throw new RuntimeException(e); } "
            "finally { System.out.print(\"F\"); }\n"
            "What is printed, and what does the caller receive?"
        ),
        "options": [
            "\"F\" is printed; the caller receives the RuntimeException (with IOException as its cause)",
            "Nothing prints; the caller receives only the IOException",
            "\"F\" prints; the caller receives the IOException, and the RuntimeException is silently discarded",
            "The program does not compile because RuntimeException is not declared",
        ],
        "answer": [0],
        "explanation": (
            "finally always runs before the exception propagates, so \"F\" prints. The thrown "
            "RuntimeException propagates; Java suppresses the original IOException and chains it "
            "as the cause (accessible via getCause())."
        ),
    },
    {
        "subject": "JAVA",
        "topic": "Streams & Lambdas",
        "difficulty": "very_hard",
        "experience_min": 5,
        "type": "single",
        "text": (
            "List<Integer> nums = List.of(1, 2, 3, 4, 5);\n"
            "int r = nums.stream().filter(n -> n % 2 == 0).mapToInt(n -> n * n).sum();\n"
            "What is r, and how many intermediate operations are lazily evaluated?"
        ),
        "options": [
            "r = 20; both filter and map are lazy and evaluated only when sum() (the terminal) runs",
            "r = 30; filter runs eagerly over the whole list",
            "r = 20; filter is eager but map is lazy",
            "r = 55; the pipeline squares all five numbers",
        ],
        "answer": [0],
        "explanation": (
            "Even numbers 2 and 4 square to 4 + 16 = 20. Streams are lazy: filter/map produce "
            "lazy stages executed element-by-element only when the terminal operation sum() "
            "triggers evaluation."
        ),
    },
    {
        "subject": "JAVA",
        "topic": "Garbage Collection",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "scenario",
        "text": (
            "A latency-sensitive trading application with a 60 GB heap pauses for 800 ms during "
            "young collections. Which change most directly reduces young-GC pause time?"
        ),
        "options": [
            "Switch to Serial GC — it never pauses for young collections",
            "Reduce the young generation size so survivors are scanned faster",
            "Increase -XX:SurvivorRatio to allocate a larger eden — pause time is proportional to survivor copy volume, not allocation rate",
            "The pause is dominated by scanning live objects in the young generation; reduce the young-gen size or switch to a concurrent collector like ZGC/G1 with bounded pause targets",
        ],
        "answer": [3],
        "explanation": (
            "Young-GC pause time tracks the number of live objects copied, not the allocation "
            "rate — a large young generation full of short-lived garbage is fast to collect, but "
            "long-lived survivors are expensive. Shrinking young gen or using G1/ZGC with pause "
            "goals directly attacks the pause; Serial would make it worse."
        ),
    },
    {
        "subject": "JAVA",
        "topic": "Generics",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "assertion_reason",
        "text": (
            "Assertion (A): At runtime, the expression (list instanceof List<String>) does not "
            "compile.\n"
            "Reason (R): Java generics are erased at compile time, so the runtime type of a "
            "generic collection does not retain its type argument."
        ),
        "options": AR,
        "answer": [0],
        "explanation": (
            "Type erasure removes type arguments at compile time; instance checks against "
            "parameterized types are illegal because the JVM cannot verify them. Both statements "
            "are true and R explains A."
        ),
    },
    {
        "subject": "JAVA",
        "topic": "Java 8+ Features",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "single",
        "text": (
            "Which statement about CompletableFuture.supplyAsync(...).thenApplyAsync(f) is "
            "correct regarding its executor behavior?"
        ),
        "options": [
            "thenApplyAsync always runs on the common ForkJoinPool unless an executor is explicitly supplied",
            "thenApplyAsync runs f on the thread that completed the previous stage when no executor is given",
            "thenApplyAsync with no executor uses the same executor that ran supplyAsync",
            "CompletableFuture stages never switch threads",
        ],
        "answer": [0],
        "explanation": (
            "The *Async variants without an explicit executor use ForkJoinPool.commonPool() by "
            "default; thenApply (no Async) runs on the completing thread. This distinction is the "
            "classic source of unexpected thread pools and starvation bugs."
        ),
    },
    # ------------------------------------------------------------------
    # SOFTWARE ENGINEERING
    # ------------------------------------------------------------------
    {
        "subject": "SE",
        "topic": "Architecture",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "scenario",
        "text": (
            "A system must serve 50k RPS with strict durability requirements, an SLA of 200 ms "
            "p95, and occasional offline batch jobs that must not degrade online latency. "
            "Which architecture decision set is most appropriate?"
        ),
        "options": [
            "A single relational database with a monolithic API — simplest and sufficient for 50k RPS",
            "Stateless API tier behind a load balancer, event-driven writes with durable queues, a read-optimized cache, and isolated compute for batch jobs",
            "Microservices with a separate database per service and no shared schema — correctness is impossible otherwise",
            "Serverless functions for every operation with a 5-second timeout",
        ],
        "answer": [1],
        "explanation": (
            "The constraints (high RPS, durability, latency SLA, batch isolation) point to "
            "stateless serving, asynchronous durable writes, caching for reads, and resource "
            "isolation for batch. Microservices are a means, not a guarantee; a single monolith "
            "struggles at 50k RPS with strict p95; serverless timeouts break batch."
        ),
    },
    {
        "subject": "SE",
        "topic": "Quality & Testing",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "single",
        "text": (
            "A test suite reports 98% line coverage, yet a critical data-corruption bug ships. "
            "Which explanation is most plausible?"
        ),
        "options": [
            "Coverage measures execution, not correctness: the corrupted branch was executed but its outcome was never asserted, or the test data never exercised the failing input class",
            "Line coverage cannot exceed 80% in professional projects",
            "The bug was in a library, so coverage of the application is irrelevant",
            "Higher coverage is impossible without mutation testing",
        ],
        "answer": [0],
        "explanation": (
            "Coverage is a necessary, not sufficient, quality signal. Executed-but-unasserted "
            "paths and untested input partitions are exactly how high-coverage suites miss "
            "corruption bugs — which is why property/mutation testing and good assertions matter "
            "more than the percentage."
        ),
    },
    {
        "subject": "SE",
        "topic": "Estimation & Process",
        "difficulty": "hard",
        "experience_min": 5,
        "type": "numerical",
        "text": (
            "A team has 6 developers who each work 8 hours/day but spend 25% of time in "
            "meetings/reviews. A feature is estimated at 240 ideal person-hours. How many "
            "calendar days does the estimate imply?"
        ),
        "options": ["5 days", "6.7 days", "8 days", "10 days"],
        "answer": [1],
        "explanation": (
            "Effective hours per developer-day = 8 × 0.75 = 6. Team effective rate = 6 × 6 = 36 "
            "hours/day. 240 / 36 = 6.67 days. Ideal-hours estimates must be converted through "
            "availability (and typically inflated further for uncertainty)."
        ),
    },
    {
        "subject": "SE",
        "topic": "Design",
        "difficulty": "very_hard",
        "experience_min": 7,
        "type": "debugging",
        "text": (
            "Two services A and B both need user data. A calls B over HTTP for every request. "
            "B's p99 latency spikes from 40 ms to 4 s during load, and A's retries amplify the "
            "load. Which pattern directly addresses the root problem rather than the symptom?"
        ),
        "options": [
            "Increase A's HTTP timeouts so B's slow responses do not fail",
            "Add retries with exponential backoff and jitter to tolerate the spikes",
            "Reduce B's coupling by having A read user data from a replicated read model / cache, and protect B with circuit breakers, load shedding and capacity checks",
            "Move A and B to the same host to reduce network latency",
        ],
        "answer": [2],
        "explanation": (
            "The symptom is latency amplification from synchronous coupling plus retries. The "
            "root fix is to remove the synchronous dependency (replicated read model) and add "
            "circuit breakers/bulkheads so B's degradation cannot cascade. Longer timeouts just "
            "extend A's tail latency; retries multiply load."
        ),
    },
    {
        "subject": "SE",
        "topic": "Requirements & Contracts",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "scenario",
        "text": (
            "A payment service returns 'PENDING' forever for 0.001% of transactions, and the "
            "team cannot reproduce it. Which engineering practice is most likely to surface the "
            "root cause first?"
        ),
        "options": [
            "Increase logging verbosity in production for all transactions",
            "Add structured tracing with a correlation ID per transaction, idempotency keys, and a reconciliation/outbox job that detects stuck states",
            "Rewrite the payment service in a new language",
            "Disable the pending state entirely",
        ],
        "answer": [1],
        "explanation": (
            "Rare, unreproducible states are best attacked with end-to-end correlation IDs, "
            "idempotency guarantees, and a reconciliation sweep that finds stuck transactions "
            "regardless of the original code path — turning a 0.001% mystery into an observable "
            "job output."
        ),
    },
    {
        "subject": "SE",
        "topic": "DevOps & Reliability",
        "difficulty": "expert",
        "experience_min": 9,
        "type": "single",
        "text": (
            "A deployment to 100 instances was rolled out to 5%, then paused for canary "
            "observation. The error rate is healthy, but the canary instances' CPU is 60% higher "
            "than baseline. What is the correct action and why?"
        ),
        "options": [
            "Promote immediately — error rate is the only release gate",
            "Investigate: CPU divergence at healthy error rates can indicate an algorithmic regression or a shift in behavior (e.g., retries, tight loops) that will degrade capacity and cost before errors appear",
            "Roll back all instances because any divergence is a failure",
            "Ignore CPU because autoscaling will compensate automatically",
        ],
        "answer": [1],
        "explanation": (
            "Error rate alone misses efficiency regressions. A sustained 60% CPU increase with "
            "normal errors often precedes latency/cost problems; the canary should be held while "
            "profiling confirms whether it is a real regression or measurement noise."
        ),
    },
    {
        "subject": "SE",
        "topic": "Security Engineering",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "assertion_reason",
        "text": (
            "Assertion (A): A web application that validates user input only on the client is "
            "not secure.\n"
            "Reason (R): Any validation executed in the browser can be bypassed by sending "
            "requests directly to the server."
        ),
        "options": AR,
        "answer": [0],
        "explanation": (
            "Client-side validation is UX, not security: an attacker bypasses the page entirely "
            "and sends crafted requests. Server-side validation is the security boundary. Both "
            "statements are true and R explains A."
        ),
    },
    {
        "subject": "SE",
        "topic": "Code Quality",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "code",
        "text": (
            "Which code snippet has the highest cyclomatic complexity, and why does it matter "
            "for maintainability?"
        ),
        "options": [
            "Five sequential statements with no branches — complexity 1",
            "A method with three if/else-if branches and one loop — complexity 5",
            "A method that calls 20 other methods — complexity 20 regardless of branches",
            "A class with 500 lines — complexity is proportional to line count",
        ],
        "answer": [1],
        "explanation": (
            "Cyclomatic complexity = 1 + number of decision points (if/else-if, loops, case "
            "labels, &&/||). 1 + 3 + 1 = 5. It correlates with the number of test paths and "
            "review effort; method calls and line counts do not directly raise it."
        ),
    },
]
