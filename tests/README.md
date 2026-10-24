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

The existing TASM two-call fixture supplies decoded-field and initial-target facts independently of the optional `LoadImage::isCallPreservedStorage` property. With exact storage preservation, both calls retain their qualified target/model/body/effect checks while machine fields stay unknown and excluded from readonly byte folding. Without the guarantee, the first target resolves but the second remains uncertain after the intervening call. This is a controlled native input contract, not Windows immutability proof or a declaration that the callee is pure. The property supplies no value or target; explicit writes and known call effects retain their existing handling.

The same test owner exercises hidden-return recovery with the x86-64 GCC model. The full action pipeline must retain the existing aggregate-return parameter even when it is unused, while recovering ordinary inputs without fixing the source parameter list. Fixed-input and direct no-types recovery controls cover the same native storage boundary. Meson supplies matching x86, x86-64 and isolated x86-16-protected language fixtures; these native tests do not replace the bridge's host-specificity import checks.

`src/unittests/testsegmentedwide.cc`
: Patch0360 supplies protected-mode C48 regressions. Synthetic CALLF/return/operand32 ENTER cases are local translated-p-code construction and width controls, not invented Windows descriptor behavior. They retain near2/far4 types, stack2, callback conventions, unknown raw far constants and distinct six-byte analysis coordinates. The raw numeric resolver refuses near/far machine encodings without origin. These controls do not qualify every x86 mode, ENTER nesting level or original-game reachability.

Four separate `protected_wide_leave_*_stack16` tests retain the measured Windows3.11/KVM C9/66C9/67C9/6667C9 ESP/EBP comparisons with SS D/B clear. Their adapter uses the explicit observed selector155f-to-file-stack/data-ordinal2 correspondence, rather than numeric selector concatenation. Captured ARPL controls compare changed1566/source1567/result1567/ZF1 and unchanged1567/source3/result1567/ZF0. The captured CS→ARPL→DS excerpt compares unchanged CS1567, loaded DS1567 and equal reads of b37a at code1:0a15. The captured normal FAR case separately maps caller1557 to code3, callee154f to code4 and SS1547 to stack/data5; it compares SP1754→1750→1754, saved IP0028/CS1557 and actual callee/caller CS. Its source WORDs are explicitly initialized comparison inputs, not independently dumped loader bytes; the witness map supplies the address comparison. The adapter rejects selectors absent from those observed maps. These are native consumer comparisons against retained observations, not raw Windows byte equality or a production mapping API.

`src/unittests/testsegmentreferences.cc`
: Patch0380 tests the on-demand query over existing Funcdata/SSA. The paired FAR case leaves literal selector4 unresolved even with a symbol at C48 segment4, while raw and overlay INSTR.EXE components recover their independently supplied complete target through the existing analysis/deindirection actions. The JMP control checks the effective six-byte tail-transfer operand in both raw/overlay inputs, retaining the existing CALLIND/RETURN thunk policy rather than requiring destination-body inlining or return42. Exact initial source slices can form a complete pointer only when the provider admits their common full range; adjacency or target equality alone is not proof. Changed offset bits cannot reuse that pointer fact, including after extraction/reassembly or merges; low-bit selector preservation is relative to the actual selector WORD. The translated CS→ARPL→DS excerpt retains the entry-segment relationship without assigning ordinal bits to CS. Field extraction/reassembly, descriptor-preserving masks, agreeing/conflicting merges and prior-write controls remain separate. The prior-write controls also supply call-preservation metadata without bypassing writes. LOAD and unresolved INDIRECT definitions are not bypassed. Bare numeric near/far values and numeric SegmentOp evaluation remain unavailable in the widened static domain; explicit analysis coordinates remain accepted. Normal analyzed FAR-call fallthrough observes caller CS, while a callee input uses its own entry segment. These bounded native controls do not qualify the separate bridge providers or establish full selector-value correction.

`src/unittests/testrelocatedfields.cc`
: Patch0370 exercises the real Sleigh decoder and ordinary PcodeEmit boundary with controlled machine-field metadata. INSTR.EXE at file0xb13/C48 0x100000913 has two runtime WORD sources, offset0x100000914 and selector0x100000916, inside one four-byte relocation. Raw, overlay and observed-selector-valued input variants preserve those source cells instead of numeric CS/offset values. Protected16 FAR controls emit the existing segment operation and indirect transfer, not a direct C48 target; independent target recovery belongs to Patch0380's analysis controls. Query misses retain literal machine bits without turning selectors into ordinals. Same-valued unrelated immediate fields/generated constants remain untouched, and supplied unrepresentable machine-value uses refuse before emission. These are local construction controls, not qualification of the bridge provider or Windows loader. Ordinary near2/far4 pointer controls remain at the wide-address owner.

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
