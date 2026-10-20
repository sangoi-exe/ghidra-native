# Intent Contract: GN-2 stack dependency preservation

Status: active
Task mode: Doctrine
Lifecycle phase: Implementation
Strategy epoch: 1
Plan kind: Bugfix / Regression Plan

## Confirmed intent and authority

Correct the demonstrated GN-2 native x86-16 decompiler failure: a conditional segmented stack pointer can select either of two initialized stack words, but the decompiler discards one memory dependency and prints an impossible result. Correct dependency exclusion in the existing native patch stack and the direct followers needed for that result. Preserve type inference and valid unchanged-entry-SS recognition. Update only the corresponding engine pin in r2ghidra after the engine correction is committed.

The current user confirmed the revised paraphrase with `sim` in session `01a15772-6cb8-7670-9ce2-e367137f77b0`, rollout line 149, turn `01a15777-1b9a-7300-a158-4e7a728a9db5`, at `2026-10-20T00:59:46.206-03:00` (America/Sao_Paulo), immediately after the assistant response beginning `Retomei da sua pergunta` at line 142. That response names the objective, the engine/direct-follower boundary, retained behavior, validation, bridge pin and exclusions. This is a new correction task, not a reopening of the completed native-baseline remediation plan. The earlier questioned proposal was not implementation authority.

The root owns this Intent Contract, integration, review and local commits. Workers own declared implementation footprints. The existing workspace rule requires `Co-authored-by: Codex <codex@openai.com>` on materially authored commits. No push, publication, global installation, destructive cleanup or compatibility preservation is authorized.

## Wrong behavior, evidence and baseline

Two 41-byte functions initialize entry-SP-relative words at `-0x10` and `+0x20` to 1 and 2, select one pointer, store 3 through unchanged entry SS and return the sum. The machine result is 4 or 5. The current native pipeline instead prints `return aiStack_10[0] + 2;` or, with branch ordering reversed, `return iStack0020 + 1;`. Each result can be 3. Native result XML retains an INDIRECT for only one candidate; reversing branch order reverses the retained candidate.

The historical production commands are in session `01a14c49-9c6e-7df2-a1eb-2c29aaec3480`, lines 5465–5488. The root re-executed both cases in the current session through the retained private host, explicit M18 plugin and matching protected-mode x86 language. Both exited 0 with empty stderr and reproduced the wrong C/XML. Inputs were private `malloc://` buffers; original binaries were not changed.

Current engine baseline: `ac2f4fed9184b453f235f6250c14c0e2c23b35a5`. Current bridge baseline and pin: bridge `8bfe4cba36ed61f0e631aa1a4fc99f173f4a259d`, engine pin `ac2f4fed9184b453f235f6250c14c0e2c23b35a5`. Both worktrees are clean at intake. No known-good implementation of the conditional witness has been established. The decoded instruction semantics provide the independent 4/5 oracle; wholesale rollback would also discard already-established segmented behavior and is not selected.

## Canonical owner and selected route

The active task workspace is `/home/lucas/work/radare2/r2ghidra/ghidra-native`, which owns the primary correction. `patches/*.patch` owns local native changes and patch-supplied tests. Imported `src/decompiler/` is baseline evidence, not a parallel committed correction path. `patches/0110-win16-segmented-addresses.patch` introduces guarded segmented stack alias discovery; `patches/0130-win16-call-stack-segment.patch` owns retained entry-SS behavior and additional tests in the same native segmented test owner. The bridge's `subprojects/ghidra-native.wrap` is the only engine revision owner.

The current LoadGuard chain conflates heuristic range hints with dependency exclusion. `establishRange` can retain a 0x1000-byte window; `isGuarded` checks only starting-offset containment. Direct dependency consumers are `RuleIndirectCollapse`, `StackAffectingOps::affectsTest`, `Heritage::guardLoads` and `Heritage::handleNewLoadCopies`. `MapState::addGuard` separately consumes range information for type hints. These are the causal frontier, not four preselected patches or four independently reproduced failures.

Select a coherent correction at the existing LoadGuard/dependency owner and its necessary consumers. Unproved or partial range information must not discard a possible dependency. Preserve useful type hints rather than turning every hint into a whole-stack array. Reuse current native address, range and operation APIs. No new solver, parser, registry, cache owner, module or proof framework is selected. Equivalent local implementation choices remain with the Worker.

State 2 is not an independent convergence certificate: the bounded solver returns no completion status, and finalization classifies ranges by their shape. This is a source-backed proof limit, not an executed solver-budget defect and not authority to redesign the solver. The correction must not claim a general completeness guarantee merely from that state.

Plan kind rationale: this task corrects executed wrong decompilation while retaining existing behavior; it is not a general feature, solver redesign or type-analysis refactor. The rejected proposal relied too heavily on state classification and an incomplete consumer list. Repairing only the printed C or one branch ordering would not correct the owner contract.

## Primary-path acceptance and first slice

The first directly verifiable slice is the two decoded-byte witnesses through the ordinary native decompile pipeline. Both pointer choices must retain the necessary memory effects, and final C must not replace a candidate's post-store value with its initialization. Both branch orderings must agree with the independent 4/5 machine semantics.

Keep a focused regression at the existing patch-supplied native segmented test owner. Verify failure on the current candidate and success after correction. Retain the existing segmented stack normalization, call arguments, unknown/independent selector, unlocked stack-parameter and original-byte controls. Preserve the valid unchanged-entry-SS path and useful type inference. Build and run the focused native tests with matching compiled x86 languages. Validate the patch stack on a fresh task-scoped source copy, not by reapplying it to an already patched checkout.

Qualify a bridge build against the corrected engine and matching language files, then rerun the two production witnesses through the host/plugin boundary. A pointer-shaped C expression or passing synthetic owner test alone does not establish production correctness. Run the existing bridge pcode XML test for the rebuilt integration. The wrap must name the exact committed engine correction. A local pin is not evidence that its remote URL serves the commit; no publication is authorized or claimed.

## Non-goals and authority boundaries

Do not redesign ValueSetSolver or solve numeric selector aliasing in real mode. Do not change NE loading, union resolution, MCP, host runtime, original game data, public project formats or existing completed plans. Do not add compatibility paths or hypothetical type/range test matrices. Additional consumers are source-frontier evidence; they do not authorize unrelated corrections. A material owner, API, behavior, risk or Scope change returns to the current user.

## High-level execution and continuity

1. Audit this confirmed Intent Contract through the registered local Plan route.
2. Implement one coherent native dependency correction and focused regression in a bounded Worker entry; validate the fresh applied stack and retained native controls.
3. Commit the engine correction, propagate its exact pin through a bounded bridge Worker entry, and validate the matching production integration.
4. Commit the candidate, complete the required paired local Code Gate, then record task-log/changelog evidence and final Git state.

The root-owned Microtask Program is a transient execution projection. It does not replace this Intent Contract or add another Scope authority.

The local `Senior Plan Auditor / Intent contract audit` on `/root/gn2_plan_audit` returned `PROCEED`, with complete required contract coverage and no material finding. The registered transition enters Implementation without another authorization checkpoint.

The native correction is committed at `06632d7bf0927ceeadd32b2829dc935afddbe101`. `patches/0160-stack-dependency-guards.patch` keeps a per-guard full/empty-range fact separate from the unchanged type hints. Its dependency consumers preserve whole-space coverage only for that unknown result; existing finite-range exclusions remain. This closes the demonstrated unknown-range failure without claiming a general solution for every partial iteration, access-width overlap or solver-budget outcome. The initially considered blanket removal of all range-based exclusion was rejected in scratch before any canonical source edit.

Both exact native regressions fail against baseline production sources and pass after correction. The complete corrected native suite passes 19/19, including an independent root execution. The task log at `.sangoi/task-logs/2026-10-20-gn2-stack-dependencies.md` records the evidence and current limits; it does not own Scope or lifecycle.

The matching bridge build and pcode XML test passed. The root's two host/plugin production observations passed with both STORE-dependent values feeding the actual returned addition and retained in final C. Private host, plugin, language paths and the corrected invocation's explicit `SLEIGHHOME` are recorded in the task log. No global installation or remote build is claimed.

Material decisions still open: none. Residual-risk acceptance: none. Review override: none. Blocker: none. Next high-level action: fix the committed review candidate and complete the required local Code Gate.
