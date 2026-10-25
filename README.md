# NeedBank

A standalone GenLayer runbook resource bank with deadlock avoidance.

Consensus interprets fetched prose into ordered acquire/return instructions. The contract compiles holdings and future claims, then admits a signed acquisition only if every unfinished job can still complete in a safe order. Enough free units alone is insufficient.

Only the bound participant may advance or abort its job. Abort returns its complete holding vector. Releases and completed historical peaks reduce remaining claims. The ledger enforces conservation and terminal jobs cannot restart.

See [architecture and limits](docs/architecture.md), [contract](contracts/need_bank.py), [fixtures](fixtures) and [tests](tests/direct). Synthetic runbooks demonstrate contract-native accounting; they do not prove physical resource possession, machine execution or service delivery.

## Local checks

```sh
pip install -r requirements-dev.txt
genvm-lint download --version v0.2.16
genvm-lint check contracts/need_bank.py --json
python -m pytest tests/direct -q
node --test tests/rpc-preflight.test.cjs
```

The runner, CLI, SDK and transitive Node tooling are pinned. No funds or private keys are stored in the repository. The Banker's safety algorithm is credited to its established literature. Reusable CLI/receipt scaffolding retains its MIT provenance.

## Verified StudioNet deployment

[Primary contract explorer](https://explorer-studio.genlayer.com/address/0xa3f5417C9236fBb75542cD3ea992e0d3ab0C3480) · [35 final-source onchain receipts](proofs/README.md) · [Ready submission text](docs/submission.md) · [Passing CI](https://github.com/moorisi/need-bank/actions/runs/39996788259).

Validation: GenVM lint; 78 direct tests; seven transport tests. Four live suites verify signed calldata, full source, complete votes, resource conservation and full ledger/event replay. The final-source set includes 20 successful executions and 15 exact expected rejections. Historical unexpected deployment errors and an ambiguous timeout are documented separately. See [worked scenarios](docs/scenarios.md) and [architecture](docs/architecture.md).
