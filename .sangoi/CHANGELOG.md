# Changelog

## 2026-10-20

- Preserve native stack dependencies when the solver provides a full or empty range, without expanding type hints or changing finite-range exclusion. Add both decoded-byte GN-2 branch-order regressions. Native validation passes 19/19, rebuilt bridge pcode XML passes 1/1 and host/plugin production witnesses pass 2/2. The bridge pin follows the committed correction. The paired local Code Gate returned `PROCEED` with complete admitted coverage and no required correction. See `task-logs/2026-10-20-gn2-stack-dependencies.md`.

- Extend native dependency coverage to circular/lossy finite ranges and intersecting access widths while keeping layout hints separate. Reject stale or ambiguous patch preparation without changing source bytes; validate Make/Meson build reuse and preserve matching Git-free prepared distributions. Combined validation passes 28 native tests, seven preparation tests and pcode XML, with six root production observations. The new paired Code Gate is pending. See `task-logs/2026-10-20-native-dependencies-and-preparation.md`.
