# Changelog

## 2026-10-20

- Preserve native stack dependencies when the solver provides a full or empty range, without expanding type hints or changing finite-range exclusion. Add both decoded-byte GN-2 branch-order regressions. Native validation passes 19/19, rebuilt bridge pcode XML passes 1/1 and host/plugin production witnesses pass 2/2. The bridge pin follows the committed correction. The paired local Code Gate returned `PROCEED` with complete admitted coverage and no required correction. See `task-logs/2026-10-20-gn2-stack-dependencies.md`.

- Candidate: extend native dependency coverage to circular/lossy finite ranges and intersecting access widths while keeping layout hints separate. Earlier combined validation passes 28 native tests, seven preparation tests and pcode XML. The prior Code Gate returned `DO_NOT_PROCEED` for preparation defects. The current-user-selected remediation excludes actual native Make outputs, connects XPS/packaged Make validation and preserves protected trees before revision changes. Eight preparation tests, targeted consumer build/reuse/refusal checks, manager cases and six current Make-plugin C/XML observations pass within the recorded qualification limits. Remediation delta review is pending; no new approval, push or installation is claimed. See `task-logs/2026-10-20-native-dependencies-and-preparation.md`.
