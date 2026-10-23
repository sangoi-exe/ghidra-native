#!/usr/bin/env python3
"""Exercise preparation against the repository's real imported source and stack."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(shutil.which('git') and (ROOT / '.git').exists(), 'fresh preparation requires a Git checkout')
class PatchPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix='native-patch-tests-')
        cls.addClassCleanup(cls.workspace.cleanup)
        cls.pristine = Path(cls.workspace.name) / 'pristine'
        subprocess.run(['git', 'clone', '--quiet', '--no-hardlinks', str(ROOT), str(cls.pristine)], check=True)
        shutil.copy2(ROOT / 'scripts/apply_patches.py', cls.pristine / 'scripts/apply_patches.py')
        shutil.rmtree(cls.pristine / 'patches')
        shutil.copytree(ROOT / 'patches', cls.pristine / 'patches')
        cls.prepared = Path(cls.workspace.name) / 'prepared'
        shutil.copytree(cls.pristine, cls.prepared)
        subprocess.run([sys.executable, str(cls.prepared / 'scripts/apply_patches.py')], check=True, capture_output=True, text=True)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=self.workspace.name)
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / 'engine'
        shutil.copytree(self.prepared, self.root)

    def run_preparation(self, *args, env=None):
        return subprocess.run([sys.executable, str(self.root / 'scripts/apply_patches.py'), *args], env=env, capture_output=True, text=True)

    def sources(self):
        return {path.relative_to(self.root): path.read_bytes() for path in (self.root / 'src').rglob('*') if path.is_file()}

    def add_imported_test_outputs(self):
        for name in ['test_dbg/marshal.o', 'test_dbg/paramactive.o', 'test_dbg/testsegmented.o',
                     'test_dbg/depend', 'test_dbg/depend.12345', 'decomp_test_dbg']:
            output = self.root / 'src/decompiler' / name
            output.parent.mkdir(exist_ok=True)
            output.write_bytes(b'imported Make test output')

    def assert_refused(self):
        sources = self.sources()
        marker = self.root / 'patch.done'
        marker_bytes = marker.read_bytes() if marker.exists() else None
        stamp = Path(self.directory.name) / 'checked.h'
        stamp.write_bytes(b'existing build stamp')
        for args in [(), ('--check', str(stamp))]:
            with self.subTest(args=args):
                result = self.run_preparation(*args)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn('stale or ambiguous patch preparation', result.stderr)
                self.assertEqual(self.sources(), sources)
                self.assertEqual(marker.read_bytes() if marker.exists() else None, marker_bytes)
                self.assertEqual(stamp.read_bytes(), b'existing build stamp')

    def test_fresh_preparation_and_matching_reuse(self):
        shutil.rmtree(self.root)
        shutil.copytree(self.pristine, self.root)
        result = self.run_preparation()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Applying ', result.stdout)
        sources = self.sources()
        marker = (self.root / 'patch.done').read_bytes()
        result = self.run_preparation()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertEqual(self.sources(), sources)
        self.assertEqual((self.root / 'patch.done').read_bytes(), marker)

    def test_prepared_distribution_without_git(self):
        (self.root / 'src/decompiler/marshal.o').write_bytes(b'local object output')
        self.add_imported_test_outputs()
        shutil.rmtree(self.root / '.git')
        env = dict(os.environ, PATH=self.directory.name)
        self.assertIsNone(shutil.which('git', path=env['PATH']))
        result = self.run_preparation(env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        stamp = self.root / 'checked.h'
        result = self.run_preparation('--check', str(stamp), env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(stamp.exists())

    def test_native_objects_preserve_preparation(self):
        (self.root / 'src/decompiler/marshal.o').write_bytes(b'local object output')
        sources = self.sources()
        marker = (self.root / 'patch.done').read_bytes()
        result = self.run_preparation()
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_preparation('--check', str(Path(self.directory.name) / 'checked.h'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.sources(), sources)
        self.assertEqual((self.root / 'patch.done').read_bytes(), marker)
        source = self.root / 'src/decompiler/marshal.cc'
        source.write_bytes(source.read_bytes() + b'\n// user edit\n')
        self.assert_refused()

    def test_imported_make_test_outputs_preserve_preparation(self):
        self.add_imported_test_outputs()
        sources = self.sources()
        marker = (self.root / 'patch.done').read_bytes()
        result = self.run_preparation()
        self.assertEqual(result.returncode, 0, result.stderr)
        stamp = Path(self.directory.name) / 'checked.h'
        result = self.run_preparation('--check', str(stamp))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(stamp.exists())
        self.assertEqual(self.sources(), sources)
        self.assertEqual((self.root / 'patch.done').read_bytes(), marker)

    def test_non_output_files_are_not_excluded(self):
        self.add_imported_test_outputs()
        for name in ['test_dbg/unpaired.o', 'test_dbg/depend.invalid', 'test_dbg/depend.123.extra',
                     'test_dbg/notes.txt', 'test_dbg/nested/marshal.o', 'coreext_local.cc', 'ruleparse.cc', 'ruleparse.hh']:
            with self.subTest(file=name):
                source = self.root / 'src/decompiler' / name
                source.parent.mkdir(exist_ok=True)
                source.write_bytes(b'not a recognized build output')
                try:
                    self.assert_refused()
                finally:
                    source.unlink()

    @unittest.skipUnless(os.environ.get('SLEIGHC'), 'set SLEIGHC to the native Sleigh compiler')
    def test_compiled_languages_preserve_preparation(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/compile_sleigh.py'), os.environ['SLEIGHC'], str(self.root / 'src/Processors/x86'), str(Path(self.directory.name) / 'sleigh-x86.stamp')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        languages = self.root / 'src/Processors/x86/data/languages'
        for name in ['x86.sla', 'x86-64.sla', 'x86-16-protected.sla']:
            self.assertGreater((languages / name).stat().st_size, 0)
        marker = (self.root / 'patch.done').read_bytes()
        result = self.run_preparation()
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_preparation('--check', str(Path(self.directory.name) / 'checked.h'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / 'patch.done').read_bytes(), marker)
        specification = languages / 'x86.slaspec'
        specification.write_bytes(specification.read_bytes() + b'\n')
        self.assert_refused()

    def test_changed_stack_preserves_prepared_sources(self):
        patch = next((self.root / 'patches').glob('*.patch'))
        patch.write_bytes(patch.read_bytes() + b'\n')
        self.assert_refused()

    def test_source_edit_is_preserved(self):
        self.add_imported_test_outputs()
        for name in ['src/decompiler/heritage.cc', 'src/decompiler/heritage.hh',
                     'src/decompiler/grammar.cc', 'src/decompiler/grammar.y',
                     'src/decompiler/xml.cc', 'src/decompiler/xml.y',
                     'src/decompiler/pcodeparse.cc', 'src/decompiler/pcodeparse.y',
                     'src/decompiler/slghparse.cc', 'src/decompiler/slghparse.hh', 'src/decompiler/slghparse.y',
                     'src/decompiler/slghscan.cc', 'src/decompiler/slghscan.l', 'src/decompiler/ruleparse.y',
                     'src/Processors/x86/data/languages/x86.slaspec', 'src/Processors/x86/data/languages/ia.sinc']:
            with self.subTest(source=name):
                source = self.root / name
                original = source.read_bytes()
                source.write_bytes(original + b'\n// user edit\n')
                try:
                    self.assert_refused()
                finally:
                    source.write_bytes(original)

    def test_old_empty_marker_is_not_accepted(self):
        (self.root / 'patch.done').write_bytes(b'')
        self.assert_refused()

    def test_missing_marker_does_not_reapply_partial_preparation(self):
        shutil.rmtree(self.root)
        shutil.copytree(self.pristine, self.root)
        patch = sorted((self.root / 'patches').glob('*.patch'))[0]
        subprocess.run(['git', 'apply', str(patch)], cwd=self.root, check=True, capture_output=True)
        self.assertFalse((self.root / 'patch.done').exists())
        self.assert_refused()


if __name__ == '__main__':
    unittest.main()
