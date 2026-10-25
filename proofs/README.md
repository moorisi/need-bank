# NeedBank — StudioNet scenario proofs

Four independent gasless StudioNet instances, chain **61999**. The final-source proof set contains **35 FINALIZED / MAJORITY_AGREE receipts**: **20 successful executions** and **15 intentional ERROR rejections**. Every intentional rejection has its exact error bytes and complete unchanged state verified. Historical unexpected errors are archived separately below and do not count toward these 35.

Contract SHA-256: `8a9d8641f3e77e700ab648150391894e415a056a599332e3f6373e28443c7dee`. Deployed source revision: `28a92f3f00bb3448e35e88f20c66515f82041495`. Fixture revision: `e382a460015df470be405e617bd16666f8e97ca9`. Source bytes match deployment calldata and fresh live code in every completed proof workflow.

| Scenario | Contract explorer | Deployment | Runbook consensus | Final result |
|---|---|---|---|---|
| avoidance | [0xa3f5417C9236fBb75542cD3ea992e0d3ab0C3480](https://explorer-studio.genlayer.com/address/0xa3f5417C9236fBb75542cD3ea992e0d3ab0C3480) | [deploy](https://explorer-studio.genlayer.com/tx/0xd5f38732dd9329890c7274139d65e8cf44a9fbcf8668f3520e61ffb652b65346) | [compile](https://explorer-studio.genlayer.com/tx/0x0bececc7e629ceccc7d16b86b6ca10350af3596a0601c05bbf99508a583c1b84) | COMPLETE; both jobs DONE, all [3,3] units returned. Free-but-unsafe request rejected. |
| reuse | [0xc0C1D539D8de291081Eb0cE2F453ac03d0f6a64E](https://explorer-studio.genlayer.com/address/0xc0C1D539D8de291081Eb0cE2F453ac03d0f6a64E) | [deploy](https://explorer-studio.genlayer.com/tx/0x80bf021eb8350060627849ea911eb2a560bdd80c25aca00840198dfb3244e362) | [compile](https://explorer-studio.genlayer.com/tx/0x523d52afa1fbbfe4134a8f366e6c080494ce6dcbc4631e50b4a4ef9f130f2d97) | COMPLETE; Amber DONE, Bronze ABORTED; all [2,2] units returned. Past-peak reuse and exact abort return verified. |
| review | [0x379a839a04FC87AFbE21ec3475B8639125c24a87](https://explorer-studio.genlayer.com/address/0x379a839a04FC87AFbE21ec3475B8639125c24a87) | [deploy](https://explorer-studio.genlayer.com/tx/0x6b6d02b59cf761c64629f5915601a97eeaddd2d51e073cf7c5294eefbf6ac05b) | [compile](https://explorer-studio.genlayer.com/tx/0x7ed933631d74b4f8d2fe5494afaf62dfb35db657982d63497eafe31d77458554) | REVIEW; unresolved instruction preserved; execution and abort rejected with zero allocation. |
| blocked | [0xEe9553AC92EA1aaBAcebdb7886Dd66622BDb4228](https://explorer-studio.genlayer.com/address/0xEe9553AC92EA1aaBAcebdb7886Dd66622BDb4228) | [deploy](https://explorer-studio.genlayer.com/tx/0xe6e56bdce679894450b6635ceb1f1ff007ebab4483b5d110b03b2ba9c6335d55) | [compile](https://explorer-studio.genlayer.com/tx/0x35f6fc0fc8da8bad154f1ecbd2b35f528349970a37a3c7d71c680b1b11ad355d) | BLOCKED / OVER_CAPACITY; definite four-unit demand retained against capacity three; no grants. |

## Consequential scenario checks

- After Amber holds [2,0], Bronze requests [0,2] while [1,3] is free. The hypothetical free vector [1,1] cannot cover either remaining job claim, so the request is rejected without allocating units or advancing a cursor. Amber then completes and returns its resources; Bronze follows.
- In reuse, Amber has already passed its processor peak and holds [0,1]. Bronze may borrow [2,0], leaving [0,1] free and safe order [Amber,Bronze]. Retaining obsolete lifetime peaks would incorrectly reject this state.
- Only Bronze may abort Bronze. Its abort returns precisely [2,0], without returning Amber's storage holding. Terminal participation cannot resume.
- UNKNOWN is not zero-demand authorization: REVIEW stores no executable program. Definite over-capacity demand is ACQUIRE [4,0], not conveniently rewritten or mislabelled ambiguous.

## Every signed receipt

Final votes include the leader and all recorded validators. **Idle is not agreement.** Complete receipt JSON preserves rotation history and earlier rounds as well as the final votes tabulated here.

Recorded dissent: review-compile (3 agree / 1 disagree / 1 idle). These receipts passed by strict majority, not unanimity.

| Call | Transaction | Execution | Agree | Disagree | Idle |
|---|---|---|---:|---:|---:|
| avoidance-deployment | [tx](https://explorer-studio.genlayer.com/tx/0xd5f38732dd9329890c7274139d65e8cf44a9fbcf8668f3520e61ffb652b65346) | SUCCESS | 5 | 0 | 0 |
| avoidance-reject-before-compile | [tx](https://explorer-studio.genlayer.com/tx/0x76ad4e0a9b7ce6d3380471a5be3abae4a0c188d55536670a00b508dd39ca72d5) | ERROR | 3 | 0 | 2 |
| avoidance-compile | [tx](https://explorer-studio.genlayer.com/tx/0x0bececc7e629ceccc7d16b86b6ca10350af3596a0601c05bbf99508a583c1b84) | SUCCESS | 3 | 0 | 2 |
| avoidance-reject-other-signer | [tx](https://explorer-studio.genlayer.com/tx/0x17051ec7dc064b844c6b0ccb04fca0879a5d978564bb488c000e60701dc6b4ab) | ERROR | 3 | 0 | 2 |
| avoidance-amber-borrow-processor | [tx](https://explorer-studio.genlayer.com/tx/0x1704e70b2f9a38725da0607fe4ae3ac6e385fbe8d1c8afff3b379c51e0006f93) | SUCCESS | 3 | 0 | 2 |
| avoidance-reject-free-but-unsafe | [tx](https://explorer-studio.genlayer.com/tx/0xdc26bb3c6d58cc27c11e5db74a75a63f699393cc7e5406e8b9b0e723215ed803) | ERROR | 3 | 0 | 2 |
| avoidance-amber-borrow-storage | [tx](https://explorer-studio.genlayer.com/tx/0x830ce94f86f2714ae571abfb7a02608613b2021ff925d8ae4adc6d09959f54d8) | SUCCESS | 3 | 0 | 2 |
| avoidance-amber-return | [tx](https://explorer-studio.genlayer.com/tx/0xc91eb4f62d9c738a5877d859335a37021fe3ca586c28d507aa341ea90e68ffdf) | SUCCESS | 3 | 0 | 2 |
| avoidance-bronze-borrow-storage | [tx](https://explorer-studio.genlayer.com/tx/0x39c62624f9af0b30a6f5bc9919649d4504f52a5284d655cd1723ef3d94309934) | SUCCESS | 5 | 0 | 0 |
| avoidance-bronze-borrow-processor | [tx](https://explorer-studio.genlayer.com/tx/0x3832b28d2ddedafe8e5b6152352fe4fa6f633c5a6215bc40d1ed8da230780f97) | SUCCESS | 3 | 0 | 2 |
| avoidance-bronze-return | [tx](https://explorer-studio.genlayer.com/tx/0x01ac87bbdc8d25822173d687bcf76644712688de14163dba040ca2b2d6a715bd) | SUCCESS | 3 | 0 | 2 |
| avoidance-reject-complete | [tx](https://explorer-studio.genlayer.com/tx/0x01e8e4ee45055def5deb42e60d2a358943d3374f0da31c2cec35c7ec6cd08850) | ERROR | 4 | 0 | 1 |
| reuse-deployment | [tx](https://explorer-studio.genlayer.com/tx/0x80bf021eb8350060627849ea911eb2a560bdd80c25aca00840198dfb3244e362) | SUCCESS | 5 | 0 | 0 |
| reuse-compile | [tx](https://explorer-studio.genlayer.com/tx/0x523d52afa1fbbfe4134a8f366e6c080494ce6dcbc4631e50b4a4ef9f130f2d97) | SUCCESS | 3 | 0 | 2 |
| reuse-amber-borrow-processor | [tx](https://explorer-studio.genlayer.com/tx/0xfc81cc7a27970792eabfd4d71de5567783b6b2bbc07351f71df08c92f935c7ce) | SUCCESS | 5 | 0 | 0 |
| reuse-reject-unavailable | [tx](https://explorer-studio.genlayer.com/tx/0xb2353c2ebdedce62532232c35b6c459ebd42a6e10c4130f7c8b658fbcafdd370) | ERROR | 3 | 0 | 2 |
| reuse-amber-return-processor | [tx](https://explorer-studio.genlayer.com/tx/0x67ccfd45baeb7bde06a4a479ae15edc751365e1ca46c0b135654e98229570f6d) | SUCCESS | 3 | 0 | 2 |
| reuse-amber-borrow-storage | [tx](https://explorer-studio.genlayer.com/tx/0x71248de5d4554f4b9a3813fb7d337e167d2c2c3f237359b2e687213cd7d2623f) | SUCCESS | 3 | 0 | 2 |
| reuse-bronze-borrow-after-past-peak | [tx](https://explorer-studio.genlayer.com/tx/0x84c1c1a6aab4b615dc3868ec25caf069696e27ae8a3a965c68739f3caa2d5c8b) | SUCCESS | 3 | 0 | 2 |
| reuse-reject-other-abort | [tx](https://explorer-studio.genlayer.com/tx/0x60072e99798446bd1dc1e82b6bb6aafa0396e9d5bd04550224f0fc72e0448061) | ERROR | 3 | 0 | 2 |
| reuse-bronze-abort | [tx](https://explorer-studio.genlayer.com/tx/0x53ba08de76fe661d564acafca95e44ee35ddc5e2f0f2580f1982db69b628a418) | SUCCESS | 3 | 0 | 2 |
| reuse-amber-return-storage | [tx](https://explorer-studio.genlayer.com/tx/0x0f0eb4717b17ad86381daa8ba916c51be0abaf22a0eedc91d4842259188774b3) | SUCCESS | 3 | 0 | 2 |
| reuse-reject-terminal | [tx](https://explorer-studio.genlayer.com/tx/0x7462667561f59a80bcf9f086fdc8fba4d729b8d5415d41a9d7b0fc927ffeb95a) | ERROR | 3 | 0 | 2 |
| review-deployment | [tx](https://explorer-studio.genlayer.com/tx/0x6b6d02b59cf761c64629f5915601a97eeaddd2d51e073cf7c5294eefbf6ac05b) | SUCCESS | 3 | 0 | 2 |
| review-compile | [tx](https://explorer-studio.genlayer.com/tx/0x7ed933631d74b4f8d2fe5494afaf62dfb35db657982d63497eafe31d77458554) | SUCCESS | 3 | 1 | 1 |
| review-reject-amber | [tx](https://explorer-studio.genlayer.com/tx/0x1a8379068b15a4f5f3834344a8ae21132346aef5fdaa2ae488cc5289d7ec5da7) | ERROR | 3 | 0 | 2 |
| review-reject-bronze | [tx](https://explorer-studio.genlayer.com/tx/0x80a762e96e09b8695cdb4e4c8659c86a6733f8df34da6ded7498b5c304c750ac) | ERROR | 4 | 0 | 1 |
| review-reject-abort | [tx](https://explorer-studio.genlayer.com/tx/0xf897750bf2e5775d90e6ca97ecd244f355b09b8250909da606e76fb61aeb86d6) | ERROR | 3 | 0 | 2 |
| review-reject-recompile | [tx](https://explorer-studio.genlayer.com/tx/0x4c919dbccbc693ef0cb77b191bab0af0616e0ec2b3bc6852d6e932e56e0aa530) | ERROR | 5 | 0 | 0 |
| blocked-deployment | [tx](https://explorer-studio.genlayer.com/tx/0xe6e56bdce679894450b6635ceb1f1ff007ebab4483b5d110b03b2ba9c6335d55) | SUCCESS | 5 | 0 | 0 |
| blocked-compile | [tx](https://explorer-studio.genlayer.com/tx/0x35f6fc0fc8da8bad154f1ecbd2b35f528349970a37a3c7d71c680b1b11ad355d) | SUCCESS | 3 | 0 | 2 |
| blocked-reject-amber | [tx](https://explorer-studio.genlayer.com/tx/0x3a314b68d14e10c8a0baec956e3418e133e804b1884bf98861e3ed7dd085e8ee) | ERROR | 3 | 0 | 2 |
| blocked-reject-bronze | [tx](https://explorer-studio.genlayer.com/tx/0x62d785bf402a1e0b8697fb314f6661d9a7538b0204f3213cafa3db2554ea6899) | ERROR | 3 | 0 | 2 |
| blocked-reject-abort | [tx](https://explorer-studio.genlayer.com/tx/0xd79c43b543cc5e068da21463bd67164ec4f51002e728c89752c6975b817a9fc6) | ERROR | 3 | 0 | 2 |
| blocked-reject-recompile | [tx](https://explorer-studio.genlayer.com/tx/0x90f3ff59e68aaf9630a90b5c36290ad0b3eb95cd64f691f88d7143a0481eddfd) | ERROR | 5 | 0 | 0 |

## Verification and provenance

[Merged transaction journal](transactions.json), [full verification](verification.json), [provenance](provenance.json), complete state traces and all individual receipt JSON files are committed here. The verifier decodes actual constructor and method calldata, checks source bytes, signer and target, unique journal hashes, complete vote membership and strict majority, exact expected error bytes, every pre-call preview, complete state before/after each call, conservation, source-defined holdings, suffix claims, completion witnesses and every event. Fresh checks re-fetch live source, complete final state and admission previews.

- [avoidance workflow](https://github.com/moorisi/need-bank/actions/runs/39994131535) — fresh verified 2026-10-23T17:31:53.460Z; [summary](verification-avoidance.json); [78-test report](avoidance-direct-tests.xml).
- [reuse workflow](https://github.com/moorisi/need-bank/actions/runs/39994140257) — fresh verified 2026-10-23T17:30:53.730Z; [summary](verification-reuse.json); [78-test report](reuse-direct-tests.xml).
- [review workflow](https://github.com/moorisi/need-bank/actions/runs/39994148021) — fresh verified 2026-10-23T17:27:29.748Z; [summary](verification-review.json); [78-test report](review-direct-tests.xml).
- [blocked workflow](https://github.com/moorisi/need-bank/actions/runs/39996798280) — fresh verified 2026-10-23T17:46:38.530Z; [summary](verification-blocked.json); [78-test report](blocked-direct-tests.xml).

All four hosted XML reports contain 78 passes and zero failures, errors or skips. Local GenVM lint, 78 direct tests and seven transport tests passed. The independent safety oracle enumerates all job permutations rather than using the contract's greedy method: 1,521 exhaustive small states, 256 generated four-job / three-resource states, and every reachable prefix with advance/abort in both active fixtures. Direct-VM traces for all four scenarios also match the independent JavaScript live oracle. Tests cover conservation, access control, actual native ABI Address inputs, schema failures, independent operation/quantity disagreement, negative UNKNOWN decisions, source refetching, full-source audits, rollback and terminal behavior.

## Earlier failures — excluded

The final BLOCKED archive was retrieved through a temporary read-only Actions export after local artifact-host downloads failed. Its original 56,697-byte ZIP matched GitHub's SHA-256 before extraction. [Retrieval provenance](artifact-retrieval.json) records the artifact and export run; the export submitted no contract calls.

[Historical manifest](history/abi-address-v1/manifest.json) preserves three unexpected VM deployment-error receipts from source `7bc7a6608f4f0224b24541873a0dd7c7973d7f9720c382003ca730cc7cd3aba7`. The CLI encoded participant values as native Address objects, while that constructor attempted a string regex before normalizing. The correction accepts typed addresses and string representations; a regression test reproduces the CLI's ABI boundary.

The earlier reuse workflow separately timed out before reporting a hash. Its artifact contains no transaction journal or receipt, so whether a broadcast occurred is unknown. That attempt was not replayed; corrected workflows use fresh disposable accounts. This timeout is not represented as an onchain success or expected rejection.

A later corrected-source BLOCKED run recorded successful deployment and compilation, then its CLI timed out before reporting a hash for a rejection call. [That partial journal and its two receipts](history/blocked-transport-39994155815/manifest.json) are also excluded from the complete primary set. The CLI wait limit was increased from 90 to 180 seconds, with no automatic send retry. A fresh-instance replacement completes the BLOCKED scenario.

## Reproduce and scope

Install the locked tooling with `npm ci`, set `GENLAYER_CLI_PATH` to `node_modules/genlayer/dist/index.js`, and run `node scripts/verify-proofs.cjs --offline`. With a configured StudioNet CLI account, omit `--offline` for fresh read-only RPC checks. These verifiers never submit transactions; workflow_dispatch scenarios perform deployments and signed actions separately.

The resource units are contract-native accounting capabilities. Synthetic runbooks do not prove physical capacity, machine work, publisher honesty or service delivery. External executors must respect the ledger. The conservative suffix-peak rule guarantees an available completion order under the programs and cooperative progress; it does not guarantee fairness, starvation freedom or forced release by an absent signer. Source, roles and capacities are immutable. Proof callers are disposable encrypted CI accounts; use persistent participant wallets when deploying your own pool. This is StudioNet, not mainnet.
