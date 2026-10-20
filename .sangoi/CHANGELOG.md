# Changelog

## 2026-10-20

- Preserve native stack dependencies when the solver provides a full or empty range, without expanding type hints or changing finite-range exclusion. Add both decoded-byte GN-2 branch-order regressions. Native validation passes 19/19, rebuilt bridge pcode XML passes 1/1 and host/plugin production witnesses pass 2/2. The bridge pin follows the committed correction. The paired local Code Gate returned `PROCEED` with complete admitted coverage and no required correction. See `task-logs/2026-10-20-gn2-stack-dependencies.md`.

- Candidate: extend native dependency coverage to circular/lossy finite ranges and intersecting access widths while keeping layout hints separate. Combined validation passes 28 native tests, seven preparation tests and pcode XML, with six bounded root production observations. Native Make/Meson upgrade refusal and matching language-generation reuse pass, but the paired Code Gate returned `DO_NOT_PROCEED`: normal bridge Make objects invalidate preparation, XPS/packaged Make bypass reuse checks, and the bridge manager mutates protected trees before refusal. The task is on hold for the current-user correction decision; no new push or installation occurred. See `task-logs/2026-10-20-native-dependencies-and-preparation.md`.
