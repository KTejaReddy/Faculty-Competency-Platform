"""Seed questions: MACHINE LEARNING, PYTHON PROGRAMMING, WEB TECHNOLOGIES."""

AR = [
    "Both A and R are true, and R is the correct explanation of A",
    "Both A and R are true, but R is NOT the correct explanation of A",
    "A is true, but R is false",
    "A is false, but R is true",
]

QUESTIONS = [
    # ------------------------------------------------------------------
    # MACHINE LEARNING
    # ------------------------------------------------------------------
    {
        "subject": "ML",
        "topic": "Evaluation",
        "difficulty": "very_hard",
        "experience_min": 5,
        "type": "numerical",
        "text": (
            "A classifier on an imbalanced dataset (1% positive) achieves 98% accuracy. "
            "Given confusion counts TP=90, FN=10, FP=1900, TN=98000, what are precision, "
            "recall, and F1 (macro implications)?"
        ),
        "options": [
            "Precision 0.045, recall 0.9, F1 ≈ 0.086 — accuracy is misleading on imbalanced data",
            "Precision 0.9, recall 0.98, F1 ≈ 0.94 — the model is excellent",
            "Precision 0.98, recall 0.045, F1 ≈ 0.086",
            "Precision 0.045, recall 0.98, F1 ≈ 0.086",
        ],
        "answer": [0],
        "explanation": (
            "Precision = TP/(TP+FP) = 90/1990 ≈ 0.045; recall = TP/(TP+FN) = 90/100 = 0.9; "
            "F1 = 2PR/(P+R) ≈ 0.086. The 98% accuracy comes from the huge TN class, hiding that "
            "the model floods false positives."
        ),
    },
    {
        "subject": "ML",
        "topic": "Regularization",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "single",
        "text": (
            "In L1 (LASSO) versus L2 (ridge) regularization, which statement is correct?"
        ),
        "options": [
            "L1 drives some coefficients exactly to zero (feature selection) because its penalty is non-differentiable at zero; L2 shrinks coefficients smoothly but rarely to exactly zero",
            "L2 drives coefficients exactly to zero because its gradient grows without bound",
            "L1 and L2 have identical solution paths",
            "Neither changes the model's loss landscape",
        ],
        "answer": [0],
        "explanation": (
            "The L1 ball has corners on the axes, so the constrained optimum frequently lies at a "
            "corner → exact zeros. L2's smooth constraint shrinks but keeps coefficients "
            "non-zero. This is the standard geometric argument."
        ),
    },
    {
        "subject": "ML",
        "topic": "Model Selection",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "debugging",
        "text": (
            "You tune a model's hyperparameters with k-fold cross-validation on the training set, "
            "then report the best fold's validation score as the model's expected performance. "
            "What is wrong?"
        ),
        "options": [
            "Nothing — cross-validation scores are unbiased by definition",
            "Selecting the best fold overestimates performance because the chosen hyperparameters were fit to the validation folds (selection bias); the correct estimate needs a held-out test set or nested CV",
            "The validation score is always lower than true performance",
            "k-fold cannot be used for hyperparameter tuning",
        ],
        "answer": [1],
        "explanation": (
            "Using validation-fold performance to both select hyperparameters and estimate "
            "generalization leaks the selection into the estimate. A final held-out test set (or "
            "nested cross-validation) separates tuning from evaluation."
        ),
    },
    {
        "subject": "ML",
        "topic": "Trees & Ensembles",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "assertion_reason",
        "text": (
            "Assertion (A): Random forests do not need extensive pruning the way single decision "
            "trees do.\n"
            "Reason (R): Random forests reduce variance by averaging many decorrelated trees, so "
            "deep individual trees are tolerated."
        ),
        "options": AR,
        "answer": [0],
        "explanation": (
            "A single deep tree has high variance; the forest's bagging + random feature "
            "subsampling decorrelates trees so averaging cancels variance, making pruning "
            "unnecessary. Both statements are true and R explains A."
        ),
    },
    {
        "subject": "ML",
        "topic": "Deep Learning",
        "difficulty": "very_hard",
        "experience_min": 7,
        "type": "scenario",
        "text": (
            "Training a deep CNN: the training loss decreases steadily, but validation loss "
            "starts rising after epoch 5 while validation accuracy plateaus. Which interventions "
            "address the root cause most directly?"
        ),
        "options": [
            "Increase the learning rate so the model escapes the overfitting basin",
            "Add dropout / data augmentation / weight decay and stop early based on validation loss",
            "Train longer — the validation curve often recovers",
            "Remove regularization so the model can fit the validation distribution",
        ],
        "answer": [1],
        "explanation": (
            "Rising validation loss with falling training loss is overfitting. Regularization "
            "(dropout, augmentation, weight decay) plus early stopping directly targets it; a "
            "higher LR would destabilize training and longer training worsens overfitting."
        ),
    },
    {
        "subject": "ML",
        "topic": "Feature Engineering",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "scenario",
        "text": (
            "A linear model must predict house prices from features including 'neighborhood' "
            "(30 categories). Which encoding choice is correct, and what does it change?"
        ),
        "options": [
            "One-hot encode neighborhood — the linear model gets a separate coefficient per category without imposing an ordering",
            "Label-encode 0..29 — the model can then use the numeric ordering meaningfully",
            "Drop the feature — categorical features cannot be used in linear models",
            "Encode as the mean price of each category and also include the original — leakage-free and lossless",
        ],
        "answer": [0],
        "explanation": (
            "Label encoding imposes an arbitrary order that linear models misinterpret as "
            "magnitude. One-hot encoding gives each category an independent weight. Mean "
            "target-encoding with the raw feature causes target leakage unless carefully "
            "cross-validated."
        ),
    },
    {
        "subject": "ML",
        "topic": "Gradient Descent",
        "difficulty": "expert",
        "experience_min": 9,
        "type": "numerical",
        "text": (
            "Training diverges: loss goes to NaN after a few steps. Which is the most likely "
            "cause, and which fix is correct first?"
        ),
        "options": [
            "The learning rate is too high for the loss landscape — reduce it or clip gradients first",
            "The batch size is too large — reduce it to fix divergence",
            "The model is underfitting — add capacity",
            "NaN is harmless; scale the loss down and continue",
        ],
        "answer": [0],
        "explanation": (
            "Loss → NaN early is the classic sign of gradient explosion (large LR, or "
            "unbounded activations). Lowering the LR and/or gradient clipping stabilizes "
            "training; batch size is not the primary cause of NaN, and underfitting would show "
            "high but finite loss."
        ),
    },
    {
        "subject": "ML",
        "topic": "Unsupervised Learning",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "single",
        "text": (
            "k-means clustering is run twice on the same data with the same k and same seed "
            "replaced by a different random seed. The results differ. Which statement is true?"
        ),
        "options": [
            "k-means is sensitive to initialization and converges to a local optimum, not necessarily the global one — different seeds can land in different local minima",
            "k-means is deterministic for a fixed k, so a different seed implies a bug",
            "k-means guarantees the global optimum because it alternates between two convex steps",
            "The data must have been shuffled during preprocessing",
        ],
        "answer": [0],
        "explanation": (
            "k-means alternates assignment and centroid update, both convex steps, but the joint "
            "problem is non-convex; the result depends on the initial centroids. K-means++ "
            "initialization and multiple restarts mitigate this."
        ),
    },
    {
        "subject": "ML",
        "topic": "Bias & Fairness",
        "difficulty": "expert",
        "experience_min": 12,
        "type": "debugging",
        "text": (
            "A hiring model trained on historical data rejects candidates from group G at 4× "
            "the rate of others. The model's accuracy is identical across groups. What is the "
            "correct engineering assessment?"
        ),
        "options": [
            "Equal accuracy proves the model is fair; no action is needed",
            "The model can be fair by accuracy while reproducing historical bias: the labels themselves encoded the bias, and fairness needs to be defined and enforced explicitly (disparate impact checks, bias audits)",
            "The fix is to remove the protected attribute from the features — that guarantees fairness",
            "Retraining with more data always eliminates group disparities",
        ],
        "answer": [1],
        "explanation": (
            "Accuracy parity does not imply fairness: if the historical outcome labels are "
            "biased, the model faithfully reproduces the bias. Dropping the attribute is "
            "insufficient (proxy features remain), and more data amplifies, not removes, label "
            "bias. Fairness must be defined, measured, and enforced."
        ),
    },
    {
        "subject": "ML",
        "topic": "Probabilistic Models",
        "difficulty": "very_hard",
        "experience_min": 7,
        "type": "numerical",
        "text": (
            "P(A)=0.4, P(B)=0.5, P(A∩B)=0.2. What is P(A|B), and are A and B independent?"
        ),
        "options": [
            "P(A|B)=0.4; A and B are independent because P(A|B) = P(A)",
            "P(A|B)=0.5; A and B are independent",
            "P(A|B)=0.4; A and B are dependent",
            "P(A|B)=0.25; A and B are dependent",
        ],
        "answer": [0],
        "explanation": (
            "P(A|B) = P(A∩B)/P(B) = 0.2/0.5 = 0.4 = P(A), and P(A∩B)=0.2=0.4×0.5, so the "
            "events are independent."
        ),
    },
    # ------------------------------------------------------------------
    # PYTHON PROGRAMMING
    # ------------------------------------------------------------------
    {
        "subject": "PY",
        "topic": "Language Internals",
        "difficulty": "very_hard",
        "experience_min": 5,
        "type": "code",
        "text": (
            "What does this print?\n"
            "def f(x, lst=[]):\n"
            "    lst.append(x)\n"
            "    return lst\n"
            "print(f(1))\n"
            "print(f(2))"
        ),
        "options": [
            "[1] then [1, 2] — the default list is evaluated once at definition and shared across calls",
            "[1] then [2] — each call gets a fresh list",
            "[1] then [1, 2] on CPython, but [2] on other interpreters",
            "TypeError because defaults cannot be mutable",
        ],
        "answer": [0],
        "explanation": (
            "Default arguments are bound once, at function definition time, so the same list "
            "object persists across calls. This is the canonical mutable-default-argument bug; "
            "the fix is lst=None."
        ),
    },
    {
        "subject": "PY",
        "topic": "Concurrency",
        "difficulty": "expert",
        "experience_min": 8,
        "type": "debugging",
        "text": (
            "A CPU-bound workload using 8 threads on an 8-core machine runs no faster than 1 "
            "thread. What is the root cause and correct fix?"
        ),
        "options": [
            "The GIL serializes bytecode execution for CPU-bound code; use multiprocessing (or a GIL-free interpreter) instead of threads",
            "Threads are always slower than processes; convert everything to async",
            "The threads contend on the standard library's import lock",
            "Increase the thread stack size so the GIL is released more often",
        ],
        "answer": [0],
        "explanation": (
            "CPython's GIL allows only one thread to execute Python bytecode at a time, so "
            "CPU-bound threading gives no speedup (it can even slow down due to switching). "
            "multiprocessing, or C-extensions that release the GIL (NumPy), are the fixes; "
            "asyncio is for I/O-bound work."
        ),
    },
    {
        "subject": "PY",
        "topic": "Data Structures",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "code",
        "text": (
            "d = {'a': 1, 'b': 2}\n"
            "x = d['c'] if 'c' in d else 0\n"
            "y = d.get('c', 0)\n"
            "z = d.setdefault('c', 0)\n"
            "What are the values of x, y, and d['c'] after this runs?"
        ),
        "options": [
            "x=0, y=0, d['c']=0 — setdefault inserts the key",
            "x=0, y=0, d['c'] raises KeyError",
            "x=0, y=0, d has no 'c' — setdefault does not mutate",
            "x=0, y=None, d['c']=0",
        ],
        "answer": [0],
        "explanation": (
            "x and y are both 0. setdefault inserts 'c':0 into the dict (since it was absent) and "
            "returns it, so d['c'] is now 0 — setdefault mutates, unlike get."
        ),
    },
    {
        "subject": "PY",
        "topic": "Comprehensions & Iterators",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "code",
        "text": (
            "gen = (n * n for n in range(10))\n"
            "print(next(gen))\n"
            "print(list(gen)[:2])"
        ),
        "options": [
            "0 then [1, 4] — the generator is consumed lazily and next() advances it first",
            "0 then [0, 1] — list() restarts from the beginning",
            "1 then [4, 9]",
            "TypeError — generators cannot be sliced",
        ],
        "answer": [0],
        "explanation": (
            "Generators are single-pass: next() yields 0 and advances the state; list(gen) then "
            "consumes the remaining values starting at 1, so the first two are 1 and 4. "
            "Generators have no restart."
        ),
    },
    {
        "subject": "PY",
        "topic": "Scoping",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "code",
        "text": (
            "def outer():\n"
            "    x = 10\n"
            "    def inner():\n"
            "        x += 1\n"
            "        return x\n"
            "    return inner()\n"
            "print(outer())"
        ),
        "options": [
            "UnboundLocalError: x is treated as local to inner because it is assigned there, and the closure is not declared with nonlocal",
            "11 — inner sees the enclosing x",
            "10 — the += is silently ignored",
            "NameError at import time",
        ],
        "answer": [0],
        "explanation": (
            "Assignment makes x local to inner; reading it before assignment raises "
            "UnboundLocalError. Declaring 'nonlocal x' (or avoiding the rebind) fixes it. "
            "Python 3 closures require nonlocal for rebinding, unlike JavaScript."
        ),
    },
    {
        "subject": "PY",
        "topic": "Performance",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "scenario",
        "text": (
            "A data pipeline processes 10 GB of CSV per day and is 3× too slow. Profiling shows "
            "the time is spent in per-row string parsing in pure Python. Which change gives the "
            "largest win with the least risk?"
        ),
        "options": [
            "Use pandas read_csv with dtypes specified and vectorized operations (or a chunked reader); avoid per-row Python loops entirely",
            "Rewrite every function as a lambda for speed",
            "Increase the file system cache size",
            "Convert the CSV to XML first — XML parses faster",
        ],
        "answer": [0],
        "explanation": (
            "Per-row Python parsing is the bottleneck; pandas/numpy vectorization (C-backed) or "
            "Polars moves the loop out of Python. Lambdas do not vectorize; filesystem cache "
            "sizing and XML conversion do not address CPU-bound parsing."
        ),
    },
    {
        "subject": "PY",
        "topic": "Modules & Packaging",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "debugging",
        "text": (
            "A package works on the developer's machine but fails in production with "
            "'ModuleNotFoundError: No module named app.core'. The deployment copies the repo "
            "and runs 'python main.py'. What is the most likely cause?"
        ),
        "options": [
            "The working directory differs, so the repo root is not on sys.path; run as a package (python -m) or install the project so absolute imports resolve",
            "Python cannot import directories with __init__.py in production",
            "The production interpreter is Python 2",
            "The package name contains uppercase letters",
        ],
        "answer": [0],
        "explanation": (
            "Running 'python main.py' puts the script's directory (not necessarily the repo "
            "root) on sys.path; if main.py lives in a subdirectory, 'app.core' resolves "
            "differently than in dev. The robust fix is 'python -m app.main' from the root or a "
            "proper install (pip install -e .)."
        ),
    },
    {
        "subject": "PY",
        "topic": "Type System",
        "difficulty": "very_hard",
        "experience_min": 5,
        "type": "assertion_reason",
        "text": (
            "Assertion (A): mypy can reject a program that runs without error at runtime.\n"
            "Reason (R): Static type checking is conservative and flags code paths that can "
            "never actually execute but violate the declared types."
        ),
        "options": AR,
        "answer": [0],
        "explanation": (
            "Type checkers prove properties statically; false positives occur because they "
            "reason about all possible values per the annotations, not the actual runtime path. "
            "Both statements are true and R explains A."
        ),
    },
    {
        "subject": "PY",
        "topic": "Memory",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "debugging",
        "text": (
            "A long-running service's RSS grows slowly but never shrinks, and the profiler "
            "shows no object leak. What is the most likely explanation?"
        ),
        "options": [
            "The allocator (pymalloc/malloc) does not return freed arenas to the OS promptly; RSS can plateau while the heap stays cached — this is expected allocator behavior, not necessarily a leak",
            "Python always returns freed memory to the OS immediately",
            "The GIL prevents memory growth",
            "RSS growth implies a reference cycle that gc cannot collect",
        ],
        "answer": [0],
        "explanation": (
            "CPython keeps free arenas for reuse; the OS RSS reflects high-water mark and "
            "allocator caching. Reference cycles ARE collected by gc, and a plateauing RSS with "
            "no growing object count is classic allocator retention. Use tracemalloc and RSS "
            "snapshots to distinguish a true leak."
        ),
    },
    {
        "subject": "PY",
        "topic": "Standard Library",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "single",
        "text": (
            "Which statement about the datetime module is correct?"
        ),
        "options": [
            "datetime.now() returns a naive local time; datetime.utcnow() is deprecated in favor of datetime.now(timezone.utc) because the naive variant silently loses timezone context",
            "datetime.now() and datetime.utcnow() are identical",
            "datetime objects are timezone-aware by default",
            "time.time() returns a datetime object",
        ],
        "answer": [0],
        "explanation": (
            "datetime.now() is naive local; datetime.utcnow() was deprecated (3.12) because it "
            "returns a naive UTC time with no tzinfo, inviting misinterpretation. The correct "
            "aware form is datetime.now(timezone.utc)."
        ),
    },
    # ------------------------------------------------------------------
    # WEB TECHNOLOGIES
    # ------------------------------------------------------------------
    {
        "subject": "WEB",
        "topic": "HTTP Semantics",
        "difficulty": "hard",
        "experience_min": 3,
        "type": "single",
        "text": (
            "A client retries an idempotent POST that timed out. The first request actually "
            "succeeded server-side. Why is this dangerous, and what is the fix?"
        ),
        "options": [
            "POST is not guaranteed idempotent, so the retry may create a duplicate resource; the fix is an idempotency key header (Idempotency-Key) processed server-side",
            "Retrying is always safe because POSTs cannot have side effects",
            "The fix is to switch to PUT, which is always idempotent by definition",
            "The client should disable retries entirely",
        ],
        "answer": [0],
        "explanation": (
            "POST is non-idempotent by semantics; a blind retry duplicates the effect. "
            "Idempotency keys let the server dedupe retries. PUT is idempotent but only for "
            "full-resource replacement — it does not solve POST-created resources by itself."
        ),
    },
    {
        "subject": "WEB",
        "topic": "Security",
        "difficulty": "very_hard",
        "experience_min": 6,
        "type": "debugging",
        "text": (
            "An attacker exploits a stored XSS vector: they submit '<img src=x onerror=\"fetch(\'/api/steal\')...\">' which persists in the DB and executes for every viewer. Which defense actually stops the execution?"
        ),
        "options": [
            "Encode user content as HTML entities on output (context-aware escaping) and set a strict Content-Security-Policy that blocks inline event handlers",
            "Add a Content-Type header to the page",
            "Filter the string '<img' on input with a blacklist",
            "Use HTTPS exclusively",
        ],
        "answer": [0],
        "explanation": (
            "Stored XSS executes because the attacker's markup reaches the DOM unescaped. "
            "Output encoding (context-aware) neutralizes the payload, and a strict CSP without "
            "'unsafe-inline' blocks event-handler execution even if encoding fails. Input "
            "blacklists are bypassable; HTTPS does not address injection."
        ),
    },
    {
        "subject": "WEB",
        "topic": "Browser Architecture",
        "difficulty": "very_hard",
        "experience_min": 5,
        "type": "scenario",
        "text": (
            "A page contains a heavy 60fps animation plus a <canvas> that redraws on every "
            "requestAnimationFrame, and the main thread is saturated. Which change most "
            "directly restores smoothness?"
        ),
        "options": [
            "Move the canvas drawing into a Web Worker with OffscreenCanvas and keep the main thread for layout/DOM",
            "Use setTimeout(0) instead of requestAnimationFrame",
            "Increase the canvas resolution to trigger the GPU",
            "Add more DOM nodes to offload the compositor",
        ],
        "answer": [0],
        "explanation": (
            "Main-thread saturation janks rAF-driven work. OffscreenCanvas + Web Worker moves the "
            "drawing off the main thread; the compositor then handles the rest. rAF is already "
            "the correct scheduling primitive; DOM growth and resolution increases worsen "
            "main-thread load."
        ),
    },
    {
        "subject": "WEB",
        "topic": "REST Design",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "single",
        "text": (
            "Which statement about cache-control directives is correct?"
        ),
        "options": [
            "no-cache means 'revalidate before reuse' (store but check), while no-store means 'never persist at all'",
            "no-cache and no-store are synonyms",
            "max-age=0 is equivalent to no-store",
            "private is the default for all responses",
        ],
        "answer": [0],
        "explanation": (
            "no-cache permits storing but requires revalidation on every use; no-store forbids "
            "any persistence. max-age=0 allows storage with immediate revalidation, unlike "
            "no-store; 'private' must be stated and applies to shared caches."
        ),
    },
    {
        "subject": "WEB",
        "topic": "Security",
        "difficulty": "expert",
        "experience_min": 10,
        "type": "debugging",
        "text": (
            "An API issues a session cookie with SameSite=Lax, no Secure flag, HttpOnly set, and "
            "no CSRF token. The API also accepts requests with Content-Type: text/plain. Which "
            "statement is correct?"
        ),
        "options": [
            "SameSite=Lax blocks most CSRF from cross-site subresource requests, but the missing Secure flag exposes the cookie over HTTP and Lax still permits top-level GET navigations that may trigger state changes via GET",
            "SameSite=Lax makes CSRF impossible in every browser",
            "HttpOnly prevents the cookie from being sent cross-site",
            "text/plain is the most dangerous Content-Type for CSRF",
        ],
        "answer": [0],
        "explanation": (
            "SameSite=Lax blocks cross-site POSTs from forms/fetch, but top-level navigations "
            "(GET) still carry the cookie, so any GET with side effects is exploitable; the "
            "missing Secure flag allows cookie theft over plaintext HTTP. HttpOnly only stops "
            "script reads — not transmission."
        ),
    },
    {
        "subject": "WEB",
        "topic": "Performance",
        "difficulty": "very_hard",
        "experience_min": 7,
        "type": "numerical",
        "text": (
            "A page's critical path: 3 CSS files (2 KB, 20 KB, 120 KB), 4 blocking JS files "
            "(40 KB each), and a 300 KB hero image. The bottleneck is render-blocking "
            "resources. What is the largest single win?"
        ),
        "options": [
            "Inline the small CSS, defer or async the non-critical JS, and lazy-load the hero image below the fold — eliminate render-blocking round trips rather than shrink bytes",
            "Compress the hero image to 150 KB",
            "Merge all JS into one file",
            "Move everything to a CDN without changing resource structure",
        ],
        "answer": [0],
        "explanation": (
            "Render-blocking CSS/JS add full round-trip serializations to the critical path; "
            "reducing their count (inline critical CSS, defer/async JS) removes those round "
            "trips, which dominates byte-shaving. Merging JS only reduces header overhead; CDN "
            "helps latency, not blocking."
        ),
    },
    {
        "subject": "WEB",
        "topic": "State Management",
        "difficulty": "hard",
        "experience_min": 4,
        "type": "scenario",
        "text": (
            "A React app fetches the same user profile in three components, each with its own "
            "useEffect fetch. The profile changes and components show inconsistent data. What "
            "is the cleanest architectural fix?"
        ),
        "options": [
            "Lift the data fetch to a single shared source (server-state cache like TanStack Query, or a context/provider) so all consumers read the same snapshot and invalidations propagate",
            "Add more useEffect hooks with dependency arrays",
            "Use localStorage to store the profile",
            "Force a full page reload when data changes",
        ],
        "answer": [0],
        "explanation": (
            "Duplicate fetches with independent state drift is the classic 'fetch-in-effect' "
            "problem. A single server-state layer (dedupe, caching, invalidation) or a shared "
            "provider guarantees consistency; more effects or localStorage paper over it."
        ),
    },
    {
        "subject": "WEB",
        "topic": "Authentication",
        "difficulty": "expert",
        "experience_min": 9,
        "type": "single",
        "text": (
            "Which statement about access-token storage for a SPA is most accurate?"
        ),
        "options": [
            "localStorage is readable by any script on the origin, so a single XSS dumps the token; httpOnly cookies with CSRF protection (or short-lived tokens + refresh flow) reduce exposure",
            "localStorage is safe because it is origin-scoped and scripts cannot read it",
            "JWT in localStorage is immune to XSS",
            "Session cookies are always worse because they cannot be revoked",
        ],
        "answer": [0],
        "explanation": (
            "localStorage is accessible to any injected script on the same origin; tokens stored "
            "there are trivially exfiltrated on XSS. httpOnly cookies survive XSS but need CSRF "
            "defenses; revocation also matters (cookies can be server-side invalidated; JWTs "
            "require a denylist or short lifetimes)."
        ),
    },
]
