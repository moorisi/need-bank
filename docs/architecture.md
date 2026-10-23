# NeedBank boundary and mechanism

Signed next-step call → independently fetched runbook → consensus-verified operations and quantities → deterministic holdings and future-claim profiles → Banker's safety test → atomic resource-ledger update or unchanged-state rejection.

The contract owns a finite pool of **contract-native resource units**, immutable participants and ordered runbooks, onchain holdings, step cursors, safe completion witnesses, terminal states and an append-only event journal. Resource units are accounting capabilities inside this contract. An external executor must consult this ledger to map them to machines; no physical resource possession or service delivery is certified.

The raw publisher owns the prose instructions. Each validator independently re-fetches complete commit-pinned bytes, verifies SHA-256 and the full scope/roster schema, independently interprets every ACQUIRE / RELEASE / UNKNOWN operation and every integer quantity, compares all consequential fields exactly, and audits the leader's quote against the full source. Quotes need not be identical. UNKNOWN is a substantive decision, independently checked; it blocks the complete pool as REVIEW.

The deterministic compiler simulates the entire ordered plan. Definite over-release, over-capacity and unreturned final units cause BLOCKED. They are not relabelled UNKNOWN or repaired to get admission. Otherwise each plan records its holdings after every step and componentwise **remaining suffix peaks**.

For a hypothetical next acquisition, free units are checked first. The safety test then starts with the hypothetical free vector and repeatedly chooses the smallest-index unfinished job whose remaining peak minus its current holdings fits. Finishing a job adds its **current** allocation to the working free vector. Future borrowing nets zero when it is returned. Failure to complete this simulation rejects the whole acquisition even if enough units are physically free now. The canonical completion order is persisted after every accepted call.

An authorized participant may only advance its next source-defined step or abort its own job. Callers cannot supply smaller claims, skip steps, rewrite plans, release another participant's units or resume a terminal job. Abort returns all its current units atomically and removes that job from future claims. Definite releases increase free units, and historical peaks disappear once passed. DONE and ABORTED hold zero.

Conservation: free[r] + sum(allocation[j][r]) == capacity[r] after every accepted call. Every ACTIVE state carries a safe completion order. When all jobs terminate, the status is COMPLETE and every unit is free. Rejecting a call leaves configuration, observations, profiles, cursors, holdings and events unchanged.

Limits: 2–4 participants, 2–3 resource types, 2–6 ordered steps per job, capacities 1–12, per-step quantities 0–16. Every definite step changes at least one unit. The event journal is bounded by the fixed programs and each participant's one possible abort; outsiders cannot consume progress slots. Preview is permissionless and does not mutate state.

Safety is conditional on the compiled runbooks and cooperative progress. This conservative componentwise-peak test can reject a request that some more complex interleaving might complete. It guarantees an available safe completion order, not starvation freedom, scheduler fairness, external work, truthful publishing or forced release from an absent participant. There is no owner override, timeout confiscation, upgrade, external payment, graph-proposal lifecycle, service certificate or one-time consumption token.

Prior scheduler primitives used FIFO footprint exclusion or EDF deadline admission. NeedBank instead reasons about simultaneously held units, future incremental claims, signed releases and aborts, and safe-state preservation. The algorithm itself is established operating-system theory, not claimed as a new mathematical invention.

References: [Banker's algorithm, Yale CS422](https://flint.cs.yale.edu/cs422/lectureNotes/L10.pdf); [GenLayer equivalence principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle). Generic encrypted CLI and receipt transport is reused under MIT; the plan compiler, suffix-claim bank, signed execution, fixtures, tests and independent state oracles implement this mechanism.
