# ghidra-native component guide

This independent repository owns the native decompiler, Sleigh compiler and processor specifications used by r2ghidra. Paths and commands below are relative to this root. See [the bridge guide](../AGENTS.md) for plugin integration and the separate build-managed engine copy; editing this checkout does not update that copy or its pin. Follow native Ghidra C++/specification conventions in the affected files, not the host's C conventions. The native Meson project currently selects C++14.

For commits, follow [the shared prospective attribution rule](../../AGENTS.md#shared-prospective-commit-attribution).

## Canonical changes and generated followers

- `patches/*.patch` is the canonical local patch stack. `scripts/apply_patches.py` applies these top-level files in sorted filename order and records their byte identity and the prepared source identity in `patch.done` only after completing the stack; Make and Meson use this same runner. `patches/Attic/` is not in that applied set.
- `src/decompiler/` and `src/Processors/` contain imported baselines. Maintain local decompiler, processor-specification and patch-supplied test deltas in the patch stack; do not also commit applied copies of those deltas. Keep algorithm and RE knowledge in code/specifications and focused tests, not instruction prose.
- A matching `patch.done` validates reuse without Git. Stale, malformed or old empty markers, changed source inputs, and markerless dirty or partly prepared trees refuse without changing source bytes. Preserve changes and prepare a new checkout or use a matching prepared distribution; do not remove the marker and retry on the same tree. Generated flat `src/decompiler/*.o` files paired with adjacent `.cc` inputs and processor `.sla` files paired with `.slaspec` inputs do not invalidate preparation; canonical sources, headers, specifications and includes remain checked.
- `sources.mk` owns the shared native source sets; `scripts/sources.py` exposes them to Meson and embedded consumers. Check native `meson.build` and the bridge's `../src/Makefile`, `../ghidra/deps.mk` and `../r2plugin/` followers when changing source membership or embedding interfaces.
- `src/Processors/<processor>/data/languages/` owns language specifications. The bridge's `../ghidra/` build compiles and installs their runtime followers; changes must be tested with matching compiled languages, not an unrelated installed set.

## Build and focused tests

- `Makefile`, `meson.build` and `meson_options.txt` own the build. `make` or `meson setup <build-dir>` followed by `meson compile -C <build-dir>` prepares fresh sources and builds the native libraries/Sleigh compiler. Make always invokes the runner; Meson configuration and build reuse validate preparation, including exported native dependencies and embedded sources. Fresh preparation mutates the source tree through patch application; inspect the checkout first and use fresh disposable copies for stack validation.
- `make test` enables and runs the Meson regression suite. For a fresh explicit build, use `meson setup <build-dir> -Dtests=true`, `meson compile -C <build-dir>` and `meson test -C <build-dir> --print-errorlogs`. The registered tests cover native regressions and patch preparation, including real Sleigh compilation. See [tests/README.md](tests/README.md) for procedures; `tests/meson.build` and `tests/main.cc` own suite membership, language fixtures and the driver.
- Some test sources exist only after applying patches: `patches/0110-win16-segmented-addresses.patch` supplies `src/unittests/testsegmented.cc`, consumed by `tests/meson.build`. Inspect its canonical patch rather than treating a missing unpatched follower as a missing test. `patches/0120-borland-fmovmem-prototype.patch` owns the corresponding local x86 convention specification.
- For documentation-only changes, check references and `git diff --check` without applying patches or rebuilding. Inspect this repository's Git diff/status directly; the parent ignore hides this checkout from parent tracking and searches.

## Destructive maintenance boundaries

`make mrproper` runs `git reset --hard` and `git clean -xdf`; sync targets replace imported `src/decompiler/` or `src/Processors/` trees. These are destructive maintenance operations, not ordinary build/test cleanup. Do not use them to validate a working checkout with edits or retained build evidence.

Last reviewed: 2026-10-20. Update this guide when patch ownership, source manifests, generated followers or native validation entry points change, and refresh the bridge/workspace maps for cross-repository changes. Shared agent workflow remains in its existing global owners.
