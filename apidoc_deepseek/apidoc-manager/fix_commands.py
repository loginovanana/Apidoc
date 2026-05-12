import re

files = {
    'apidoc_cli/commands/validate.py': ('@app.command(name="validate")', '@app.callback()'),
    'apidoc_cli/commands/tree.py': ('@app.command(name="tree")', '@app.callback()'),
    'apidoc_cli/commands/diff.py': ('@app.command(name="diff")', '@app.callback()'),
    'apidoc_cli/commands/mock.py': ('@app.command(name="mock")', '@app.callback()'),
    'apidoc_cli/commands/testgen.py': ('@app.command(name="testgen")', '@app.callback()'),
    'apidoc_cli/commands/publish.py': ('@app.command(name="publish")', '@app.callback()'),
    'apidoc_cli/commands/convert.py': ('@app.command(name="convert")', '@app.callback()'),
    'apidoc_cli/commands/generate.py': ('@app.command(name="generate")', '@app.callback()'),
}

for fname, (old, new) in files.items():
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(old, new)
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✓ {fname}')