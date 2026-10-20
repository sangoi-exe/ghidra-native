# ghidra-native unit tests

Focused regression tests for the decompiler patches in `patches/`.
The tests build the vendored decompiler sources with meson and run the
tests from `src/unittests/` with the small driver in `tests/main.cc`.

The tests in `src/unittests/` are picked up by the upstream
`src/decompiler/Makefile` as well (its `UNITTEST_SOURCE` macro looks in
`../unittests`), so `make -C src/decompiler test` builds the same tests
on systems with a full GNU toolchain and BFD.

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

Meson registers `ghidra-native-unittests` and `patch-preparation`. The former compiles its matching x86 language fixture and runs the native driver; the latter currently contains eight controls exercising the real patch runner and stack. They check fresh/matching reuse, Git-free prepared reuse, preserved source bytes on changed patches/source or invalid preparation, reuse with a paired flat native object output, and reuse after compiling x86 languages with the built Sleigh compiler. Edits to native `.cc`/`.hh` sources and processor includes remain refusal cases; only flat `src/decompiler/*.o` outputs paired with adjacent `.cc` files and processor `.sla` outputs paired with `.slaspec` files are excluded from source identity. Set `TMPDIR` to a task-scoped cache directory when running the preparation tests; their disposable source copies are created there. Running `python3 tests/test_apply_patches.py` directly without `SLEIGHC` skips the compiler case; the registered Meson test supplies it.

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
