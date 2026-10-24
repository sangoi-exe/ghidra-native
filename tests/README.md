# ghidra-native unit tests

Focused regression tests for the decompiler patches in `patches/`.
The tests build the vendored decompiler sources with meson and run the
tests from `src/unittests/` with the small driver in `tests/main.cc`.

The tests in `src/unittests/` are picked up by the imported `src/decompiler/Makefile` as well (its `UNITTEST_SOURCE` macro looks in `../unittests`). This alternate build requires the full GNU toolchain and BFD development files; it is distinct from the root `make test`, which uses Meson. Prepare the sources before calling the imported Makefile, which does not invoke the shared runner itself:

```
python3 scripts/apply_patches.py
make -C src/decompiler test
python3 scripts/apply_patches.py
```

The current imported test target has an object-name collision: `src/decompiler/pcodeinject.cc` and `src/unittests/pcodeinject.cc` both map to `test_dbg/pcodeinject.o`, which appears twice in the link command and causes duplicate definitions. Preparation reuse after its object/dependency generation is supported, but output classification does not fix this link failure or establish a complete alternate test run. Use the Meson suite for native regression execution.

Use matching compiled language files through `SLEIGHHOME` for the native language-dependent tests. Preparation reuse accepts the imported test target's `src/decompiler/test_dbg/*.o` files only when paired with `.cc` inputs in `src/decompiler/` or `src/unittests/`, plus `test_dbg/depend`, its `test_dbg/depend.<numeric PID>` temporary and `src/decompiler/decomp_test_dbg`. Other files in `test_dbg/` are still inputs, not blanket-ignored outputs. The imported Makefile can regenerate parser `.cc`/`.hh` files from `.y`/`.l` inputs; changed parser bytes remain a preparation mismatch, even if generated during a build. Preserve that tree and use new matching prepared sources rather than deleting `patch.done`. Support for these test outputs does not qualify other optional imported targets.

## Running

The tests must run against matching prepared sources. `make test` invokes the shared preparation runner and then runs Meson:

```
make test
```

or manually:

```
meson setup build -Dtests=true
meson compile -C build
meson test -C build --print-errorlogs
```

On Windows, run the commands from a Visual Studio developer prompt
(`vcvars64.bat`) so that meson selects MSVC:

```
call "C:\Program Files\Microsoft Visual Studio\18\Professional\VC\Auxiliary\Build\vcvars64.bat"
meson setup build -Dtests=true
meson compile -C build
meson test -C build --print-errorlogs
```

If the system has no zlib development package, meson falls back to the
`zlib.wrap` file in `subprojects/`.

Preparation and build reuse validate `patch.done` against the current canonical patches and source inputs. A stale, malformed or old empty marker, or a markerless dirty/partly prepared source tree, refuses without changing source bytes. Preserve changes and start with a new checkout or matching prepared distribution; do not remove the marker and retry on the same tree. Matching prepared distributions do not require Git to build, but fresh-preparation tests require a Git checkout and executable.

Meson registers `ghidra-native-unittests` and `patch-preparation`. The former compiles its matching x86 language fixture and runs the native driver; the latter exercises the real patch runner and stack. Its controls check fresh/matching reuse, Git-free prepared reuse with flat and imported test outputs, unchanged source/marker/stamp bytes on refusal, recognized output shapes, and reuse after compiling x86 languages with the built Sleigh compiler. Native sources, headers, grammar inputs and generated parsers, processor specifications/includes and unrelated non-output files remain refusal cases. Only the recognized outputs described above, paired flat native objects and paired processor `.sla` outputs are excluded from source identity. Set `TMPDIR` to a task-scoped cache directory when running the preparation tests; their disposable source copies are created there. Running `python3 tests/test_apply_patches.py` directly without `SLEIGHC` skips the compiler case; the registered Meson test supplies it.

Native owner tests do not qualify every bridge consumer. Bridge Make, XPS Make/Meson and the packaged-distribution Make path need their own preparation/reuse observations; source wiring or a passing native suite alone does not establish full host linkage or runtime readiness.

## Tests

`src/unittests/paramactive.cc`
: `ParamActive::whichTrial` regression tests.  The one-byte cases are
  the regression from rizinorg/rz-ghidra#385: the original code returned
  `-1` as soon as the first trial did not overlap a one-byte access,
  which made callers register duplicate trials or index the trial vector
  with `-1`.

`src/unittests/pcodeinject.cc`
: Dynamic p-code injection tests.  A `<pcode inject="..." dynamic="true"/>`
  declaration needs a front-end (Ghidra's Java side) to supply the
  payload; without one, `InjectPayloadDynamic::inject` throws
  `Missing dynamic inject`, so the shipped processor specs must not
  declare dynamic injects that native-only users cannot service.

`src/unittests/testsegmented.cc`
: Patch-supplied segmented/native regressions, including entry-SS dependencies, full/empty guards and conservative finite/overlapping stack dependencies. The conditional flat32 cases decode machine instructions and inspect returned STORE dependencies; the finite 16-bit circular case uses generated p-code and the real range solver. The nonwrapping access-width cases inspect actual returned STORE dependencies. Boundary-wrap controls inspect guard byte coverage, not a safe function return across frame corruption. These bounded tests do not establish universal alias soundness or replace matching bridge production C/XML observations.

The same test owner exercises hidden-return recovery with the x86-64 GCC model. The full action pipeline must retain the existing aggregate-return parameter even when it is unused, while recovering ordinary inputs without fixing the source parameter list. Fixed-input and direct no-types recovery controls cover the same native storage boundary. Meson supplies matching x86, x86-64 and isolated x86-16-protected language fixtures; these native tests do not replace the bridge's host-specificity import checks.

`src/unittests/testsegmentedwide.cc`
: Patch0360 supplies protected-mode C48 regressions. The existing native emulator executes actual translated CALLF, return, memory-address and operand32 ENTER instructions; its segment adapter delegates to the registered `SegmentOp::execute`, not a copied coordinate formula. CALLF checks vary pointer-cell locations and loaded selector/offset fields independently, including nonzero offset high words, independent DS/SS and SP wrap. Assertions inspect the actual target and saved return frame. Type/constant controls retain near2/far4 pointers, stack2, supplied callback models and value-preserving symbol reconstruction. These finite cases do not certify every x86 mode, descriptor behavior or ENTER nesting level, and do not establish original-game reachability.

Four separate `protected_wide_leave_*_stack16` tests execute C9, 66C9, 67C9 and 6667C9. Their initial ESP/EBP, stack payload and final register values come from an actual MS-DOS 6.22/Windows 3.11 Enhanced Mode run under QEMU 8.2.2 with KVM enabled and SS D/B clear. The measured upper ESP remains unchanged in every case; the operand size selects the popped width. The tests place the payload at the native SS:BP analysis coordinate only to compare this consumer with those observations, not to assert Windows descriptor mapping or raw-byte equality. These cases do not qualify other stack sizes or the bridge runtime.

`src/unittests/testrelocatedfields.cc`
: Patch0370 exercises the real Sleigh decoder and ordinary PcodeEmit boundary with controlled LoadImage field metadata. The FAR-call shape comes from the executed INSTR.EXE instruction at file0xb13/C48 0x100000913: relocation source0x100000914 spans four bytes, its unknown selector source0x100000916 spans two bytes, and the independent static target is0x100000994. Assertions separate the two-byte RAM input to CS from the six-byte CALL coordinate, retain two-byte stack operations, and leave same-valued unrelated immediate fields and generated constants untouched. Raw, analysis-overlay and observed-selector-valued input variants cannot supply a constant CS. Query misses retain numeric decoding; missing static targets and unrepresentable widened machine values refuse before emission. These are local construction controls, not an implementation or qualification of the bridge provider, Windows loader, relationship resolver or full selector/DS-load chain. The existing wide-address owner retains ordinary near2/far4 pointer controls.

## Manual Dalvik integration repro

The Dalvik item of PR #26 is about `<pcode inject="uponentry"
dynamic="true"/>` and `<callotherfixup targetop="moveRangeToIV">` being
removed from `src/Processors/Dalvik/data/languages/Dalvik_Base.cspec`.
To check the behaviour end to end with an r2ghidra build:

1. Get a small DEX (e.g. `dex/Hello.dex` or `dex/dex38.dex` from
   https://github.com/radareorg/radare2-testbins).
2. Decompile the methods of the file with r2ghidra:

   ```
   radare2 -q -a dalvik -b 32 -e io.cache=true -c 'aa; pdg @@f' Hello.dex
   ```

   With the patched (stripped) specification the decompiler must produce
   output for every method without reporting `Missing dynamic inject` or
   asserting.  r2ghidra itself provides native implementations for the
   `moveRangeToIV` userop (`R2DalvikPcodeInjectLibrary`), so leaving the
   userop unresolved is handled gracefully.

3. To exercise the other side, point `SLEIGHHOME` at a stock Ghidra
   installation (whose `Dalvik_Base.cspec` still has the dynamic
   declarations) and repeat; r2ghidra services `uponentry` and
   `moveRangeToIV` natively in that configuration as well.
