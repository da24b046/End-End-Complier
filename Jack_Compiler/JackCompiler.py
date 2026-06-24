"""
JackCompiler.py
End-to-end Jack compilation pipeline.

Usage
-----
    python JackCompiler.py <file.jack>        # compile a single file
    python JackCompiler.py <directory/>       # compile all .jack files in dir

Outputs (written next to each source file, or to the specified out_dir)
-------
    <ClassName>T.xml   — tokenizer output
    <ClassName>.xml    — parse-tree XML
    <ClassName>.vm     — VM code
"""

import os
import sys

from JackTokenizer    import JackTokenizer
from CompilationEngine import CompilationEngine


def compile_file(jack_path, out_dir):

    if not jack_path.endswith('.jack'):
        raise ValueError(f'Expected a .jack file, got: {jack_path}')

    src_dir    = os.path.dirname(os.path.abspath(jack_path))
    class_name = os.path.splitext(os.path.basename(jack_path))[0]
    dest_dir   = out_dir or src_dir

    os.makedirs(dest_dir, exist_ok=True)
    tokenizer = JackTokenizer(jack_path)
    tokens    = tokenizer.tokenize()
    src_txml  = os.path.join(src_dir, class_name + 'T.xml')
    if out_dir and src_txml != os.path.join(dest_dir, class_name + 'T.xml'):
        import shutil
        shutil.copy(src_txml, dest_dir)

    engine = CompilationEngine(tokens, dest_dir, class_name)
    engine.compileclassname()



def compile_directory(directory, out_dir):

    jack_files = [
        os.path.join(directory, f)
        for f in sorted(os.listdir(directory))
        if f.endswith('.jack')
    ]
    if not jack_files:
        print(f'No .jack files found in {directory}')
        return
    for path in jack_files:
        compile_file(path, out_dir)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if os.path.isdir(target):
        compile_directory(target, out_dir)
    elif os.path.isfile(target):
        compile_file(target, out_dir)
    else:
        print(f'Error: {target} is not a file or directory.')
        sys.exit(1)


if __name__ == '__main__':
    main()
