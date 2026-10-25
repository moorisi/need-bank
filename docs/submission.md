# Submission

**Category:** Builder → Intelligent Contracts

**Title:** NeedBank: Consensus resource claims with deadlock avoidance

**Notes / Description** (992 characters):

NeedBank is a standalone GenLayer resource pool with signed runbook execution and deadlock avoidance. A deployment fixes participants, capacities and a commit-pinned prose runbook/SHA-256. Leader and validators independently fetch complete instructions, extract every acquire/return quantity and verify source quotes. Unknown instructions produce REVIEW; definite infeasible plans produce BLOCKED. The compiler derives holdings and remaining demand peaks. Each acquisition atomically checks free units and a Banker's safe completion order for all unfinished jobs. Only a bound participant can advance its next step or abort and return its holdings. StudioNet proofs cover free-but-unsafe rejection, release and reuse after a past peak, signer checks, abort recovery and disabled pools. Includes 78 direct tests, independent permutation oracles and 35 finalized receipts. Units are contract-native accounting capabilities; synthetic runbooks do not prove machine execution or service delivery.

**Evidence:**

- [Repository](https://github.com/moorisi/need-bank)
- [GenLayer contract source](https://github.com/moorisi/need-bank/blob/main/contracts/need_bank.py)
- [GenLayer contract explorer](https://explorer-studio.genlayer.com/address/0xa3f5417C9236fBb75542cD3ea992e0d3ab0C3480)
- [Deployment transaction](https://explorer-studio.genlayer.com/tx/0xd5f38732dd9329890c7274139d65e8cf44a9fbcf8668f3520e61ffb652b65346)
- [All onchain scenario proofs](https://github.com/moorisi/need-bank/blob/main/proofs/README.md)
- [Passing CI](https://github.com/moorisi/need-bank/actions/runs/39996788259)
