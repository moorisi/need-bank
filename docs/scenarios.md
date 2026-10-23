# Worked resource scenarios

## Enough free units is insufficient

The avoidance pool contains three processor units and three storage units. Amber's plan borrows two processor units, then two storage units, then returns both. Bronze borrows in the opposite order.

After Amber's first step, free = [1,3]. Bronze's first request [0,2] fits the free vector. However, granting it would leave free = [1,1], Amber holding [2,0] and needing [0,2], and Bronze holding [0,2] and needing [2,0]. Neither unfinished job could obtain its remaining claim and finish. NeedBank rejects this hypothetical grant without changing any holdings, cursor or event.

Amber can instead borrow its storage units, return both resource types, and finish. Bronze can then execute its complete plan. The final free vector is [3,3], both jobs are DONE, and every accepted state has a safe completion witness.

The label UNSAFE refers to this conservative completion test. It is not a claim that the current state is already deadlocked.

## Past peaks, reuse and abort

The reuse pool has capacity [2,2]. Amber's instructions borrow two processor units, return them, borrow one storage unit, and return it. Bronze first borrows two processor units, later borrows two storage units, then returns both.

Bronze is rejected while Amber still holds both processor units. After Amber returns processors and borrows one storage unit, its future processor claim is zero. Bronze's processor acquisition is now admitted. At that point Amber holds [0,1], Bronze holds [2,0], and free = [0,1]. Amber can finish first, allowing Bronze to finish afterwards.

A safety check that retained Amber's obsolete lifetime processor peak would incorrectly reject this state. NeedBank uses suffix peaks at the current cursor.

Only Bronze's signer can abort Bronze. Abort returns its actual [2,0] allocation, leaving Amber's storage unit held until Amber returns it. Bronze becomes ABORTED and cannot resume.

## Unresolved instruction

The review runbook leaves Amber's processor quantity as an unresolved choice between two and three. Leader and validators must classify that step UNKNOWN with an all-zero placeholder vector; they must not choose the convenient lower quantity. The complete pool becomes REVIEW, no resources are reserved, and both jobs' execution and abort calls are disabled.

The zero placeholder is not a zero-demand authorization. There is no executable compiled program in REVIEW.

## Definite impossible demand

The blocked runbook definitely requires four processor units from a capacity-three pool. The semantic classification remains ACQUIRE [4,0], because the text is definite. Deterministic compilation produces BLOCKED with the exact job and step. It does not silently lower the demand, label the source ambiguous, or allow the other job to begin.

## Public API

- `compile()`: permissionless one-time interpretation of the immutable runbook.
- `preview(job)`: permissionless ALLOWED / INSUFFICIENT / UNSAFE / TERMINAL / DISABLED result. An ALLOWED preview includes the entire hypothetical next ledger.
- `advance(job)`: only that job's bound signer; executes exactly the next source-defined operation if safe.
- `abort(job)`: only that job's bound signer; returns all its current units and permanently ends its participation.
- `get_state()`: full source, interpreted instructions, compiled profiles, resource ledger and events.

A preview is state-dependent. Another signed call can change admission before the caller submits its transaction; advance rechecks atomically against current state. There is no promise of a future reservation from a preview alone.

These examples concern contract-native units. Real workers and machines require an external integration that respects the ledger. No proof asserts that synthetic instructions were physically executed.
