# GN-2 stack dependency preservation

Date: 2026-10-20
Status: complete; local Code Gate `PROCEED`.
Intent owner: `.sangoi/planning/2026-10-20-gn2-stack-dependencies.md`.

## Authority and source

The current user confirmed the revised scope with `sim` in root session `01a15772-6cb8-7670-9ce2-e367137f77b0`, turn `01a15777-1b9a-7300-a158-4e7a728a9db5`, at `2026-10-20T00:59:46.206-03:00` (America/Sao_Paulo). The local Intent Contract audit on `/root/gn2_plan_audit` returned `PROCEED`. No review override, external publication, global installation or residual-risk acceptance is selected.

Engine baseline: `ac2f4fed9184b453f235f6250c14c0e2c23b35a5`. Engine correction: `06632d7bf0927ceeadd32b2829dc935afddbe101`. Bridge baseline: `8bfe4cba36ed61f0e631aa1a4fc99f173f4a259d`; bridge pin/documentation commit: `b5667721e4f0694e2a03abda0c648b80fa4ba4fd`. The engine and bridge are independent Git repositories. The host and MCP have no assigned changes.

## Observed defect and correction

Two 41-byte protected-mode x86-16 witnesses initialize stack words at entry `SP-0x10` and `SP+0x20` to 1 and 2, select either pointer, store 3 through unchanged entry SS and return their sum. Their independent instruction-semantics oracle is 4 or 5, never 3. Baseline C incorrectly adds one candidate's initialization to the other candidate's post-store value. Reversing the branch order reverses which dependency is lost. Root reproduced both C/XML failures before implementation using the retained private host and M18 plugin, with exit 0 and empty stderr.

The solver explicitly reports a full range for the segmented address. `LoadGuard` then substitutes a 0x1000-byte range hint, and dependency consumers treat that hint as exclusion evidence. The new canonical `0160-stack-dependency-guards.patch` separates full/empty solver results from that hint. It initializes and refreshes `rangeIsUnknown` in the existing guard lifecycle. `isGuarded` preserves same-space dependencies for an unknown range; `guardLoads` uses the same predicate; load-copy address forcing uses whole-space coverage only for unknown ranges. Existing INDIRECT-collapse and merge consumers already use the predicate. Finite-range exclusion and min/max/step/type hints remain unchanged.

The first scratch-only mechanism would have removed finite-range exclusion for every guard. The root rejected that broader precision change before any canonical patch existed. The delivered patch contains only the full/empty-range correction. No solver redesign, new proof framework or compatibility path was added.

## Native validation

All source/build artifacts are under `/home/lucas/.cache/codex/ghidra-native/gn2-stack-dependencies/native-NZhwQb/`. Fresh sources consume the entire sorted canonical patch stack; the editable checkout's imported sources and patch marker were not changed.

| Check | Observed result |
| --- | --- |
| Final byte-driven regression against baseline production sources | 0/2; first order misses the positive dependency, second order misses the negative dependency. |
| Corrected focused segmented tests | 10/10. |
| Complete corrected native suite | 19/19, repeated independently by the root through `final-build/tests/decompiler_test` with `SLEIGHHOME=final-build/tests`. |
| Fresh stack application | Successful; `stack-check/src` equals the compiled `final-source/src`. |
| Staged patch whitespace check | Passed before the engine source commit. |

The new tests use decoded bytes and ordinary native decompile actions. Both candidate INDIRECT values must feed the actual returned addition. Final C must retain both initializations, the segmented store and `return aiStack_10[0] + iStack0020;`. The baseline failure is a missing dependency assertion, not only a printer-name mismatch.

Relevant retained logs are `final-baseline-build.log`, `final-baseline-witness.log`, `focused-details.log`, `final-setup.log`, `final-build.log`, `final-suite.log` and the final Meson test log. Baseline executable/source and corrected `final-source/`, `final-build/` and matching compiled x86 languages are retained separately. Sleigh and compiler warnings remain in the logs. No observed regression occurred in the executed suite; no general performance result is claimed.

## Integration, review and limits

The bridge wrap and its active product-document pin now name the exact committed engine correction. Its URL, directory and depth remain unchanged. A fresh disposable bridge source populated the engine by local clone at that detached revision and configured with `--wrap-mode=nodownload`. The private host/development package is `/home/lucas/.cache/codex/radare2/m12-host-WFS7Cw/install`, `r_core` version 6.2.5. Host and plugin linkage were qualified against that install's libraries. The bounded plugin, DATA/x86 language and pcode encoder targets compiled; the pcode XML test passed 1/1.

The integration scratch root is `/home/lucas/.cache/codex/r2ghidra/gn2-stack-dependencies/bridge-cu3d6K/`. The matching plugin is `build-direct/libcore_r2ghidra.so`; language files are under `source/subprojects/ghidra-native/src/Processors/x86/data/languages/`. The root explicitly loaded that plugin into the private host and executed both witnesses in private `malloc://0x2000` buffers. Both exited 0 with empty stderr. Both final C outputs retain both initializations and return `aiStack_10[0] + iStack0020;`. Native result XML independently confirms that both stack INDIRECT outputs caused by the STORE at `ram:0x101c` feed the actual returned addition. Production result: 2/2 passed.

The first invocation set the language directory only after loading the plugin, which emitted a missing-default-Sleigh-home startup diagnostic. The root inspected `SleighAsm::getSleighHome` and supplied its existing `SLEIGHHOME` environment input before plugin loading. The two successful observations used that input plus the explicit plugin config. No source correction, package installation or fallback runtime was needed. The failed assertion before inspecting the first output is not counted as a passing production observation.

Bridge logs are in `logs/`; `logs/test.log` records the encoder result without requiring the inherited-environment dump. Compiler and Sleigh warnings remain in the build logs; their baseline delta was not assessed. Neither all processors nor network-only fetching was exercised. The unused initial setup directory remains as task-owned setup evidence.

The exact production replay command, environment, both byte inputs and XML assertions are retained at one-based lines 427/430 of root session `01a15772-6cb8-7670-9ce2-e367137f77b0`, `/home/lucas/.codex/sessions/2026/10/20/rollout-2026-10-20T00-54-39-01a15772-6cb8-7670-9ce2-e367137f77b0.jsonl`, call ID `call_dlOgpF7qajamfHowoMuq99wX`. Line 427 contains the command; line 430 contains the observed successful output. No standalone production transcript or raw XML file was saved in the bridge evidence directory. The retained structured execution and native regression establish the bounded observation without another proof script or artifact.

This result concerns the executed full/empty unknown-range dependency class. It does not establish solver convergence or correct every finite partial range, access-width overlap, numerical selector alias or real-mode alias. NE, union, MCP and host-runtime corrections are excluded. Remote availability of the local engine commit and a fresh network-only build are unverified. Original game files, global installations and upstream repositories were not changed.

## Final review and follow-up classification

The fixed reviewed candidates are engine `83c0c8d0f6392fea9ed2b269c541e6b0a61aa421` and bridge `b5667721e4f0694e2a03abda0c648b80fa4ba4fd`. Source pair `/root/gn2_source_senior` and `/root/gn2_source_claude` covered the native patch and its direct owner/test chain. Integration pair `/root/gn2_integration_senior` and `/root/gn2_integration_claude` covered the three task documents, two bridge pin changes, evidence adequacy and source/build/runtime seams. Both pairs completed independent assessments and reciprocal examination. Root analysis addressed all findings and limitations before the final cumulative Senior disposition.

The integration Senior returned `PROCEED`, route condition `not-applicable`, at `2026-10-20T01:34:06.826-03:00` (America/Sao_Paulo), root rollout line 668. Semantic coverage is complete for the admitted six-path change set; no required correction, nit or indispensable gap remains. No participation or exchange was dispensed with, and no review override was used. The registered transition enters Closeout; no review rerun is required for this factual memorialization.

- `bookkeeping memorialization`: record the final result and exact production-evidence locator. A review claim that the replay command was unavailable was falsified by the retained execution and explicitly retracted; no missing-evidence defect remains.
- `deferred observation`: existing finite wrapped-range and discarded/very-large-finite-range handling may warrant a separately admitted production probe. These are pre-existing source hypotheses, not reproduced GN-2 regressions or selected corrections. Preserve their uncertainty.
- `deferred observation`: exact printed-C expectations may need revision alongside a future authorized printer/type improvement. The current dataflow checks independently protect the demonstrated defect. An additional finite-index control and broad nonsegmented output/performance study are optional, not missing GN-2 acceptance.
- `deferred observation`: the pre-existing product guide configures the language directory after plugin loading. A separate guide update can document the existing pre-load `SLEIGHHOME` input. The selected bridge change remains pin-only.
- `deferred observation`: native Claude initial reviews did not fully honor the requested no-write behavior. The source call self-reported an unlocated plan summary. The integration call self-reported `/home/lucas/.claude/plans/review-whether-the-documentation-rippling-nest.md`; its existence, 2720-byte size and modification time `2026-10-20T01:28:49.125887373-03:00` were independently confirmed by the review lanes, while authorship rests on the self-report. No repository mutation was observed; reciprocal calls reported no further plan writes. No cleanup or harness change was attempted. The bounded follow-up owner is the native Claude workflow, not this decompiler patch.

Required local non-substantive fixes: none. Substantive runtime/contract fixes: none selected. Bundle/proof corrections: none required. These classifications preserve the review evidence without turning an excluded hypothesis or optional improvement into implementation authority.

The engine source correction, documentary evidence and bridge pin are separate honest local checkpoints. The bridge's pin and hardcoded product-document reference share one commit because neither should advertise a different engine revision. Matching private builds and failure evidence are retained for replay; no extra Git worktree was created. Final closeout changes only this log, the canonical plan and changelog.
