#!/usr/bin/env python3
"""
patch_gromacs.py:
Patches GROMACS source tree when built as an in-source subproject via FetchContent.
Replaces CMAKE_SOURCE_DIR with Gromacs_SOURCE_DIR in CMake scripts so that GROMACS
resolves its internal files relative to its own root rather than the parent project root.
"""

import sys
import os

def patch_gromacs(source_dir):
    extensions = ('.cmake', '.cmakein', '.txt', '.cpp', '.rst', '.in')
    patch_count = 0
    for root, dirs, files in os.walk(source_dir):
        if '.git' in dirs:
            dirs.remove('.git')
        for fname in files:
            if fname.endswith(extensions) or fname == 'CMakeLists.txt':
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    if '${CMAKE_SOURCE_DIR}' in content or '@CMAKE_SOURCE_DIR@' in content:
                        new_content = (content
                                       .replace('${CMAKE_SOURCE_DIR}', '${Gromacs_SOURCE_DIR}')
                                       .replace('@CMAKE_SOURCE_DIR@', '@Gromacs_SOURCE_DIR@'))
                        with open(fpath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        patch_count += 1
                except Exception as e:
                    print(f"Warning: failed to patch {fpath}: {e}", file=sys.stderr)
    print(f"[patch_gromacs] Successfully patched {patch_count} files in {source_dir}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: patch_gromacs.py <gromacs_source_dir>", file=sys.stderr)
        sys.exit(1)
    patch_gromacs(sys.argv[1])
