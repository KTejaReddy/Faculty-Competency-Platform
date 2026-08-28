"""Additional ARTIFICIAL INTELLIGENCE questions (completes the 16-question bank)."""

AR = [
    "Both A and R are true, and R is the correct explanation of A",
    "Both A and R are true, but R is NOT the correct explanation of A",
    "A is true, but R is false",
    "A is false, but R is true",
]

QUESTIONS = [
    {
        "subject": "AI", "topic": "Search", "difficulty": "hard", "experience_min": 3,
        "type": "single",
        "text": "For uniform-cost search (Dijkstra-style) on a graph with non-negative edge costs, which statement is correct?",
        "options": [
            "It expands nodes in order of increasing path cost g(n), guaranteeing optimality for the first goal popped; it degrades to breadth-first search when all edges have equal cost",
            "It expands the node closest to the goal first",
            "It never expands more nodes than A*",
            "It requires an admissible heuristic",
        ],
        "answer": [0],
        "explanation": "UCS orders the frontier by g(n), so the first goal expanded is provably cheapest (with non-negative costs); equal edge weights make g(n) proportional to depth, which is BFS behavior. It needs no heuristic and can expand more nodes than informed A*.",
    },
    {
        "subject": "AI", "topic": "Search", "difficulty": "very_hard", "experience_min": 6,
        "type": "numerical",
        "text": "In the 8-puzzle, the Manhattan distance heuristic is used with A*. Which statement is true?",
        "options": [
            "Manhattan distance is admissible (never overestimates) and consistent, so A* with it finds optimal solutions; the effective branching factor is far below brute force",
            "Manhattan distance overestimates and can return suboptimal paths",
            "A* requires the heuristic to be exactly the true cost",
            "Manhattan distance is only usable for the 15-puzzle",
        ],
        "answer": [0],
        "explanation": "Each tile must travel at least its Manhattan distance to its goal position, so h ≤ h* (admissible); moving a tile changes h by at most 1 per move (consistent). Optimality follows. The heuristic's quality is what makes 8-puzzle search feasible.",
    },
    {
        "subject": "AI", "topic": "Logic", "difficulty": "hard", "experience_min": 4,
        "type": "single",
        "text": "Which statement about resolution in propositional logic is correct?",
        "options": [
            "Resolution is refutation-complete: to prove a sentence, negate it, convert to CNF, and derive the empty clause — sound and complete for propositional logic",
            "Resolution can only prove satisfiability",
            "Resolution requires converting to DNF",
            "Resolution is incomplete for propositional logic",
        ],
        "answer": [0],
        "explanation": "The resolution rule (p∨q, ¬p∨r ⊢ q∨r) applied to a CNF clause set is refutation-complete: if the set is unsatisfiable, the empty clause is derivable. Proof by contradiction (negate the goal) is the standard procedure.",
    },
    {
        "subject": "AI", "topic": "Knowledge Representation", "difficulty": "very_hard", "experience_min": 7,
        "type": "assertion_reason",
        "text": "Assertion (A): A knowledge base that is consistent can still entail a contradiction when combined with a new belief.\nReason (R): Adding a new belief that conflicts with the existing knowledge base makes the combined set unsatisfiable, so classical logic entails everything (principle of explosion).",
        "options": AR,
        "answer": [0],
        "explanation": "If KB ∪ {φ} is unsatisfiable, it classically entails any sentence (ex falso quodlibet). This is why belief revision and paraconsistent logics exist: a single inconsistent belief poisons classical entailment. Both statements are true and R explains A.",
    },
    {
        "subject": "AI", "topic": "Adversarial Search", "difficulty": "very_hard", "experience_min": 7,
        "type": "single",
        "text": "In a zero-sum game with perfect information, what does the minimax value of the root node represent?",
        "options": [
            "The best outcome the MAX player can guarantee assuming the MIN player also plays optimally",
            "The best outcome against an irrational opponent",
            "The outcome of random play",
            "The outcome if MAX plays greedily",
        ],
        "answer": [0],
        "explanation": "Minimax computes the value assuming both players choose optimally — the guaranteed worst-case payoff for MAX. Against suboptimal opponents the actual outcome can only be better for MAX.",
    },
    {
        "subject": "AI", "topic": "Constraint Satisfaction", "difficulty": "hard", "experience_min": 4,
        "type": "scenario",
        "text": "A map-coloring CSP has variables A..F, three colors, and adjacency constraints. Which ordering/heuristic pair most improves backtracking efficiency?",
        "options": [
            "MRV (minimum remaining values) variable ordering plus the least-constraining-value (LCV) value ordering",
            "Random variable and value selection",
            "Alphabetical ordering with the first color",
            "Maximum cardinality ordering with a fixed value sequence",
        ],
        "answer": [0],
        "explanation": "MRV chooses the variable with the fewest legal values, failing fast when a domain empties; LCV prefers values that rule out the fewest choices for neighbors. Together they dramatically cut backtracking versus static ordering.",
    },
    {
        "subject": "AI", "topic": "Probabilistic Reasoning", "difficulty": "very_hard", "experience_min": 8,
        "type": "numerical",
        "text": "P(A)=0.3, P(B|A)=0.8, P(B|¬A)=0.2. What is P(A|B)?",
        "options": ["0.63", "0.24", "0.5", "0.8"],
        "answer": [0],
        "explanation": "P(B) = P(B|A)P(A) + P(B|¬A)P(¬A) = 0.8×0.3 + 0.2×0.7 = 0.24 + 0.14 = 0.38. P(A|B) = 0.24/0.38 ≈ 0.63. This is Bayes' rule with a binary partition.",
    },
    {
        "subject": "AI", "topic": "Reasoning", "difficulty": "hard", "experience_min": 4,
        "type": "single",
        "text": "What is the main limitation of a pure forward-chaining rule engine on a large knowledge base?",
        "options": [
            "It derives every consequence of the facts, even those irrelevant to the current goal, which can flood working memory and slow inference (goal-directed backward chaining is cheaper when only one query matters)",
            "It cannot handle rules with conjunctions",
            "It is always faster than backward chaining",
            "It cannot fire rules more than once",
        ],
        "answer": [0],
        "explanation": "Forward chaining is data-driven and exhaustive — it computes all consequences regardless of the query. For single-goal queries backward chaining is typically far more efficient, which is why expert systems use it.",
    },
]
