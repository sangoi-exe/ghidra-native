#!/usr/bin/env python3
"""Prepare or validate the native patch stack, for both Make and Meson."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def fingerprint(root, paths):
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(root).as_posix().encode() + b'\0')
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def source_files(root):
    processors = root / 'src/Processors'
    for path in (root / 'src').rglob('*'):
        if not path.is_file():
            continue
        if path.suffix == '.sla' and processors in path.parents and path.with_suffix('.slaspec').is_file():
            continue
        yield path


def refuse():
    raise SystemExit('ghidra-native: stale or ambiguous patch preparation; source files were not changed. '
                     'Preserve your changes and prepare a new checkout or use a matching prepared distribution. '
                     'Do not remove patch.done and retry on this tree.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', metavar='STAMP', type=Path,
                        help='only validate prepared sources, then write the build stamp')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    marker = root / 'patch.done'
    patches = sorted((root / 'patches').glob('*.patch'))
    if not patches:
        raise SystemExit('ghidra-native: no patches found')
    state = {
        'patches': fingerprint(root, patches),
        'sources': fingerprint(root, source_files(root)),
    }
    if marker.exists():
        try:
            prepared = json.loads(marker.read_text())
        except (ValueError, OSError):
            refuse()
        if prepared != state:
            refuse()
    else:
        if args.check:
            refuse()
        try:
            checkout = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=root, stderr=subprocess.DEVNULL).decode().strip()
            clean = subprocess.run(['git', 'diff', '--no-ext-diff', '--quiet', 'HEAD', '--', 'src'], cwd=root, check=False).returncode == 0
            untracked = subprocess.check_output(['git', 'ls-files', '--others', '--', 'src'], cwd=root)
        except (OSError, subprocess.CalledProcessError):
            refuse()
        if Path(checkout).resolve() != root or not clean or untracked:
            refuse()
        for patch in patches:
            print('Applying ' + patch.name, flush=True)
            subprocess.run(['git', 'apply', '--whitespace=nowarn', str(patch)], cwd=root, check=True)
        state['sources'] = fingerprint(root, source_files(root))
        marker.write_text(json.dumps(state) + '\n')
    if args.check:
        args.check.write_text('')


if __name__ == '__main__':
    main()
