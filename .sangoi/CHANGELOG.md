# Changelog

## 2026-10-20

- Preserve native stack dependencies when the solver provides a full or empty range, without expanding type hints or changing finite-range exclusion. Add both decoded-byte GN-2 branch-order regressions. Native validation passes 19/19, rebuilt bridge pcode XML passes 1/1 and host/plugin production witnesses pass 2/2. The bridge pin follows the committed correction; final Code Gate is pending. See `task-logs/2026-10-20-gn2-stack-dependencies.md`.
